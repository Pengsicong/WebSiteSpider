# -*- encoding: utf-8 -*-
from redis import Redis
from manager import manager
from download import downloader
import requests
import time

redis = Redis()

def engine(initUrls):

	total_pages = manager(initUrls)

	downloader()

	success_page = int(redis.get('success'))
	success_rate = success_page / total_pages
	print('success_page:', success_page)
	print('total_pages:', total_pages)
	print('success_rate: %0.2f%%' %(success_rate*100))


if __name__ == '__main__':
	pass
	engine('http://python3-cookbook.readthedocs.io/zh_CN/latest/')
