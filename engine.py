# -*- encoding: utf-8 -*-

from queue import Queue
from utilities import test


def engine(initUrl, crawl_type='pc', max_deep=0, max_pageNum=0):
	if get_url_tyep(initUrl) != 'html':
		print('URL ERROR!')
		return

	htmlQueue = Queue()
	htmlQueue.get(initUrl)

	manager(htmlQueue, initUrl, crawl_type, max_deep, max_pageNum)

	

if __name__ == '__main__':
	pass
	# # 入口url
	# initUrl = ''
	# # 抓取类型,'pc' or 'phone'
	# crawl_type = ''
	# # 最大深度
	# max_deep = 
	# # 最大网页数
	# max_pageNum = 

	# engine(initUrl, crawl_type, max_deep, max_pageNum)