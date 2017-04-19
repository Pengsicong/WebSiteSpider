from gevent import monkey; monkey.patch_all()
from gevent.lock import BoundedSemaphore
from gevent.pool import Pool
from urllib import parse
import random
import os
import time
import requests

sem = BoundedSemaphore(4)

def save(url,r):
	
	o = parse.urlparse(url)
	if o.path == '/' or o.path == '':
		filepath = o.netloc + '/index.html'
	else:
		filepath = o.netloc + o.path		
		if o.path.find('.') == -1:
			filepath += '.html'

	filepath = os.path.join('Website',filepath)

	if not os.path.exists(filepath):
		if not os.path.exists(os.path.dirname(filepath)):
			os.makedirs(os.path.dirname(filepath))
		with open(filepath, 'w') as f:
			f.write(r.text)




def simulateHttpIo(url):

	sem.acquire()
	start = time.time()
	print(url + ' 下载开始！')
	r = requests.get(url)
	r.encoding = r.apparent_encoding
	save(url, r)
	# time.sleep(2)
	sem.release()
	duration  = time.time() - start
	print(url + ' 下载完毕！用时：%.2fs ' %duration)


urlList = []


for url in urlList:
	simulateHttpIo(url)

simulateHttpIo('http://www.baidu.com/')

gList = [gevent.spawn(simulateHttpIo,url) for url in urlList]

gevent.joinall(gList)

pool = Pool()


pool.map(simulateHttpIo, urlList)