from utilities.util_file import url2filePath 
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from download import download_html
from urllib import parse
from redis import Redis
import requests
import json
import re
import os

redis = Redis()


def autoBackSlash(string):
	if string.find('?') != -1:
		string = string.replace('?', '\?')
	if string.find('(') != -1:
		string = string.replace('(', '\(')
	if string.find(')') != -1:
		string = string.replace(')', '\)')
	if string.find('|') != -1:
		string = string.replace('|', '\|')
	if string.find('+') != -1:
		string = string.replace('+', '\+')
	return string 

def is_interior_url(realUrl, url):
	if parse.urlparse(realUrl).hostname == parse.urlparse(url).hostname:
		return True
	else:
		return False

class htmlParser:
	def __init__(self):
		self.htmlSet = set()
		self.srcDic = dict()
		self.cssSet = set()

	def feed(self,html):
		soup = BeautifulSoup(html, 'lxml')

		# 获取超链接
		for a in soup.find_all('a'):
			if a.has_attr('href'):
				link = a['href']
				self.htmlSet.add(link)

		# 获取src资源
		for src in soup.find_all(src=re.compile('.+')):

			if src.has_attr('type'):
				srcType = src['type']
			else:
				srcType = src.name
			self.srcDic[src['src']] = srcType
			# print(src['src'])



		# 获取CSS链接
		for css in soup.find_all(type='text/css'):
			if css.has_attr('href'):
				self.cssSet.add(css['href'])
				redis.sadd('CSS', css['href'])
		for css in soup.find_all('link', rel='stylesheet'):
			if css.has_attr('href'):
				self.cssSet.add(css['href'])
				redis.sadd('CSS', css['href'])


def htmlSaver(url, html, parser):

	startPath = url2filePath(url)
	postfixList = ['.html', '.hml', '.shtml', 'shml']
	pattern = re.compile('(?<=\"|\')')

	# 处理html
	for link in parser.htmlSet:
		realUrl = parse.urljoin(url, link)
		if is_interior_url(realUrl, url):

			filePath = url2filePath(realUrl)
			try:
				relativePath = os.path.relpath(filePath, os.path.dirname(startPath))
			except:
				continue
			# 处理锚点符号 #
			o = parse.urlparse(realUrl)
			if o.fragment != '':
				urlfile = realUrl.split('#')[0]
				relativePath = relativePath + '#' + o.fragment
			else:
				urlfile = realUrl

			link = autoBackSlash(link)

			html = re.sub('(?<=\"|\')%s(?=\"|\')'%link, relativePath, html)


			# 获取filePath后缀
			postfix = os.path.splitext(parse.urlparse(filePath).path)[1]

			if postfix in postfixList:
				# HTML.add(urlfile)
				redis.sadd('HTML', urlfile)

	# 处理css
	for link in parser.cssSet:
		realUrl = parse.urljoin(url, link)

		filePath = url2filePath(realUrl)
		try:
			relativePath = os.path.relpath(filePath, os.path.dirname(startPath))
			link = autoBackSlash(link)
			html = re.sub('(?<=\"|\')%s(?=\"|\')'%link, relativePath, html)
		except:
			pass
		

	# 处理html中的css的背景链接
	pattern = re.compile('url[ ]*\([^\)]+')
	for link in re.findall(pattern, html):	
		# 将bgurl规格化		
		try:
			bgurl = re.search(re.compile('(?<=\"|\')[^\)]+(?=\"|\')'), link).group()
		except:
			bgurl = link.strip()[3:].strip()[1:]
		realUrl = parse.urljoin(url, bgurl)

		if bgurl[:1] == '/' or bgurl[:4] == 'http':
			filePath = url2filePath(realUrl, 'img')
			relativePath = os.path.relpath(filePath, os.path.dirname(startPath))
			# print(filePath, os.path.dirname(startPath), relativePath)
			link = autoBackSlash(link)
			try:
				html = re.sub('%s(?=\))' %link, 'url(%s' %relativePath, html)
			except Exception as e:
				print(repr(e))
				print('link:', link)
				print('relativePath:', relativePath)
		# 将链接添加到redis里面
		redis.hset('SRC',realUrl, 'img')	


	#处理DOWNLOAD
	for key in parser.srcDic:
		realUrl = parse.urljoin(url, key)
		filePath = url2filePath(realUrl, parser.srcDic[key])
		if filePath == None:
			print(filePath, 'None!')
			continue


		relativePath = os.path.relpath(filePath, os.path.dirname(startPath))
		link = autoBackSlash(key)
		html = re.sub('(?<=\"|\')%s(?=\"|\')'%link, relativePath, html)
	
		redis.hset('SRC', realUrl, parser.srcDic[key])
		# print(realUrl, info[1])

	# 修改编码
	html = re.sub('(?<=charset=)[^\"|\']+', 'utf8', html)

	# 保存修改过后的HTML
	dirName = os.path.dirname(startPath)
	if not os.path.exists(dirName):
		os.makedirs(dirName)
	with open(startPath, 'w') as f:
		f.write(html)

	# 设置STATUS
	redis.sadd('STATUS',url)	


def cssSaver(url, css):

	startPath = url2filePath(url)

	pattern = re.compile('url[ ]*\([^\)]+')
	for link in re.findall(pattern, css):	
		# 将bgurl规格化		
		try:
			bgurl = re.search(re.compile('(?<=\"|\')[^\)]+(?=\"|\')'), link).group()
		except:
			bgurl = link.strip()[3:].strip()[1:]

		realUrl = parse.urljoin(url, bgurl)	
		redis.hset('SRC',realUrl, 'img')

		if bgurl[:1] == '/' or bgurl[:4] == 'http' or bgurl[:2] == '..':
			filePath = url2filePath(realUrl, 'img')
			try:
				relativePath = os.path.relpath(filePath, os.path.dirname(startPath))
				link = autoBackSlash(link)
				css = re.sub('%s(?=\))' %link, 'url(%s' %relativePath, css)
				# 将链接添加到redis里面
			except Exception as e:
				# print(repr(e))
				# print('url = ', url)
				# print('realUrl = ', realUrl)
				continue

	dirName = os.path.dirname(startPath)
	if not os.path.exists(dirName):
		os.makedirs(dirName)
	with open(startPath, 'w') as f:
		f.write(css)
	redis.sadd('STATUS', url)


if __name__ == '__main__':
	url = 'https://media.readthedocs.org/css/sphinx_rtd_theme.css'
	css = requests.get(url).text

	cssSaver(url , css)


		