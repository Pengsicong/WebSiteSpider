from gevent import monkey; monkey.patch_all()
from gevent.lock import BoundedSemaphore
from redis import Redis
import gevent
from html.parser import HTMLParser
from urllib import parse
from redis import Redis
import json
import requests
from utilities.util_file import url2filePath, saveSet
from utilities.util_conf import *
import time 
import os

redis = Redis()
sem = BoundedSemaphore(BoundedSemaphoreNum)

def downloader():
	redis = Redis()
	src = redis.hgetall('SRC')
	gList = []
	for key in src:
		url = key.decode()
		urlType = src[key].decode()
		gList.append(gevent.spawn(download, url, urlType))
		redis.hdel('SRC', key.decode())
	gevent.joinall(gList)


def download(url, urlType):
	filePath = url2filePath(url, urlType)
	if filePath == None:
		return
	if os.path.exists(filePath):
		print(filePath, '已存在')
		return
	sem.acquire()
	for i in range(REDOWNLOAD_TIMES):
		try:
			# 动态超时设置
			seconds = 15 * (i + 1)
			r = requests.get(url,stream=True, timeout=seconds)
			# contentType = r.headers['Content-Type'].split(';')[0]
			# 创建文件夹
			saveSet(filePath)
			# 流式下载
			with open(filePath, 'wb') as f:
				for chunck in r.iter_content(16384):
					f.write(chunck)

			# 验证完整性
			# if 'Content-Length' in r.headers:
			# 	length = int(r.headers['Content-Length'])
				# if os.path.getsize(filePath) != length:
				# 	os.remove(filePath)
				# 	print(url, '下载不完整，已删除')
				# 	continue					

			print(url, '下载成功！！')
			# redis.hdel('FAIL',url)
			sem.release()
			return 
		except:
			print(url, ' 下载失败！')
			time.sleep(3)

	redis.hset('FAIL_SRC',url, urlType)

	sem.release()

def download_html(url, user_type, proxies, redirects=False):
	if user_type == 'pc':
		headers = HEADERS_PC
	elif user_type == 'phone':
		headers = HEADERS_PHONE 

	if proxies != None:
		proxies = {
		'http:':proxies,
		'https':proxies
		}


	# 下载失败，重新下载
	for i in range(REDOWNLOAD_TIMES):
		try:
			r = requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=10)
			r.raise_for_status()
			if not r.headers['Content-Type'].split(';')[0] == 'text/html':
				print('NO HTML' , url)
				return None
			r.encoding = r.apparent_encoding
			# 反转义
			html = HTMLParser().unescape(r.text)
			html = parse.unquote(r.text)
			return html
		except:
			print(url, '下载失败，重新下载中…%d' %i+1)
			time.sleep(2)			
			continue

	print(url + '  获取html失败！')
	redis.sadd('FAILED_HTML', url)
	return None

if __name__ == '__main__':
	downloader()
	# print(download_html('http://www.jianshu.com/c/22f2ca261b85?order_by=top&page=1', 'pc', None))	
