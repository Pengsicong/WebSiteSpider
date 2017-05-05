from gevent import monkey; monkey.patch_all()
from gevent.lock import BoundedSemaphore
import gevent
from parser import *
from queue import Queue
from pybloom import ScalableBloomFilter
import json
from redis import Redis
from utilities.util_conf import *
import requests


# 设置协程个数
sem = BoundedSemaphore(BoundedSemaphoreNum)

#读取redis
redis = Redis()

def htmlrun(url, user_type='pc', proxies=None):

	sem.acquire()
	try:
	
		html = download_html(url, user_type, proxies)
		# 如果跳转后的url不是内部url
		# if not is_interior_url(redirectUrl, url):
		# 	return
	except:
		sem.release()
		return
	# global html
	if html == None:
		sem.release()
		return False
	html = HTMLParser().unescape(html)
	html = parse.unquote(html)
	parser = htmlParser()
	parser.feed(html)

	htmlSaver(url, html, parser)
	print(url, ' 下载成功！')
	redis.incr('success')
	sem.release()


def cssrun(url):
	sem.acquire()
	for i in range(REDOWNLOAD_TIMES):
		try:
			r = requests.get(url)
			r.raise_for_status()
			css = r.text
			cssSaver(url, css)
			print(url + '下载成功！')
			sem.release()
			return
		except Exception as e:
			print(url, repr(e))
	sem.release()

def manager(initUrlList,  max_deep=MAX_DEEP, max_pageNum=MAX_PAGENUM\
	, crawl_type = CRAWL_TYPE, proxies=PROXIES):

	redis.set('success', 0)

	# 抓取网站个数
	page_num = 0

	htmlQueue = Queue()	

	if isinstance(initUrlList, list):
		initUrl = initUrlList[0]
		for url in initUrlList:
			htmlQueue.put(url)
	elif isinstance(initUrlList, str):
		initUrl = initUrlList
		htmlQueue.put(initUrl)

	if max_pageNum == 0:
		max_pageNum = -1

	if max_deep == 0:
		max_deep = 9999

	try:
		with open('urlBloomfilter.bloom', 'rb') as f:
			sbf = ScalableBloomFilter().fromfile(f)
			print('bllomfilter 读取成功！')
	except:
		sbf = ScalableBloomFilter(initial_capacity=10000, error_rate=0.00001,
             mode=ScalableBloomFilter.LARGE_SET_GROWTH)

	for deep in range(max_deep):
		gList = []
		while not htmlQueue.empty():
			url = htmlQueue.get()
			if not url in sbf or deep == 0:			
				# htmlrun(url)
				gList.append(gevent.spawn(htmlrun, url, crawl_type, 'localhost:8087'))

			max_pageNum -= 1
			page_num += 1
			if max_pageNum == 0:
				continue
		gevent.joinall(gList)

		while redis.scard('STATUS') > 0:
			url = redis.spop('STATUS').decode()
			sbf.add(url)

		if max_pageNum == 0:
			break

		while redis.scard('HTML') > 0:
			url = redis.spop('HTML')
			url = url.decode()
			htmlQueue.put(url)

		# 没有url需要爬取
		if htmlQueue.empty():
			break

	# 下载CSS文件
	while redis.scard('CSS') > 0:
		url = redis.spop('CSS').decode()
		url = parse.urljoin(initUrl, url)
		gList.append(gevent.spawn(cssrun, url))
	gevent.joinall(gList)

	# 最后保存Bloomfilter文件
	with open('urlBloomfilter.bloom', 'wb') as f:
		sbf.tofile(f)

	return page_num

if __name__ == '__main__':
	initUrlList = []
	manager(initUrlList)



