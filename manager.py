from gevent import monkey; monkey.patch_all()
from parser import *
from queue import Queue
from reduceFile import reduceFile
from pybloom import ScalableBloomFilter
import json
from redis import Redis


def manager(initUrl,  max_deep=1, max_pageNum=0, crawl_type = 'pc'):
	# 设置协程个数
	sem = BoundedSemaphore(20)

	#读取redis
	redis = Redis()

	htmlQueue = Queue()
	cssQueue = Queue()
	htmlQueue.put(initUrl)

	if max_pageNum == 0:
		max_pageNum = -1

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
			if not url in sbf or url == initUrl:			
				# htmlrun(url)
				gList.append(gevent.spawn(htmlrun, url))

			max_pageNum -= 1
			if max_pageNum == 0:
				continue
		gevent.joinall(gList)

		while redis.scard('CSS') > 0:
			url = redis.spop('CSS')
			url = url.decode()
			cssQueue.put(url)

		while not cssQueue.empty():
			url = cssQueue.get()
			if not url in sbf:
				# cssrun(url)
				gList.append(gevent.spawn(cssrun, url))
		gevent.joinall(gList)

		while redis.scard('STATUS') > 0:
			url = redis.spop('STATUS')
			url = url.decode()
			sbf.add(url)

		if max_pageNum == 0:
			break

		while redis.scard('HTML') > 0:
			url = redis.spop('HTML')
			url = url.decode()
			htmlQueue.put(url)

	# 最后保存Bloomfilter文件
	with open('urlBloomfilter.bloom', 'wb') as f:
		sbf.tofile(f)


if __name__ == '__main__':
	manager('https://maoxian.de/',2)



