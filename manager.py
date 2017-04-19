from parser import *
from queue import Queue
from reduceFile import reduceFile
from pybloom import ScalableBloomFilter
import json


def manager(initUrl, crawl_type = 'pc', max_deep=1, max_pageNum=0):
	htmlQueue = Queue()
	cssQueue = Queue()
	htmlQueue.put(initUrl)

	if max_pageNum == 0:
		max_pageNum = -1


	try:
		with open('urlBloomfilter.bloom', 'rb') as f:
			sbf = ScalableBloomFilter().fromfile(f)
	except:
		with open('urlBloomfilter.bloom', 'wb') as f:
			sbf = ScalableBloomFilter(initial_capacity=10000, error_rate=0.00001,
                 mode=ScalableBloomFilter.LARGE_SET_GROWTH)
			sbf.tofile(f)

	for deep in range(max_deep):
		while not htmlQueue.empty():
			url = htmlQueue.get()
			if not url in sbf:			
				htmlrun(url)
			max_pageNum -= 1
			if max_pageNum == 0:
				continue
		reduceFile('data/')
		with open('data/status/total_status.json', 'r') as f:
			d = json.load(f)
			for url in d:
				sbf.add(url)
		with open('data/css/total_css.txt', 'r') as f:
			for url in f:
				cssQueue.put(url.strip())

		while not cssQueue.empty():
			url = cssQueue.get()
			if not url in sbf:
				cssrun(url)
		if max_pageNum == 0:
			break
	with open('urlBloomfilter.bloom', 'wb') as f:
		sbf.tofile(f)


if __name__ == '__main__':
	manager('')



