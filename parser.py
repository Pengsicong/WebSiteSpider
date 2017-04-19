from utilities.util_file import url2filePath, saveSet
from html.parser import HTMLParser
from hashlib import md5
from urllib import parse
import requests
import json
import re
import os

class htmlParser(HTMLParser):
	"""docstring for Parser"""
	def __init__(self):
		HTMLParser.__init__(self) 
		self.htmlSet = set()
		self.xmlSet = set()
		self.imgSet = set()
		self.cssSet = set()
		self.jsSet = set()
		self.otherSet = set()
		self.sourceSet = set()

	def handle_starttag(self, tag, attrs):
		for attr in attrs:
			if 'href' in attr:
				# 获取HTML链接
				if tag == 'a':
					link = parse.unquote(attr[1])
					self.htmlSet.add(link)

			# 获取source链接
			elif 'src' in attr:
				# print(attrs)
				source = attr[1]
				for attr in attrs:
					if 'type' in attr:
						# print(attr)
						sourceType = attr[1]
						break
					else:
						sourceType = tag
				self.sourceSet.add((sourceType, source))

		# 获取CSS链接
		if tag == 'link':
			for attr in attrs:
				if 'stylesheet' in attr or 'text/css' in attr:
					for attr in attrs:
						if 'href' in attr:
							self.cssSet.add(attr[1])

		# 获取XML链接			
		if tag == 'link':
			for attr in attrs:
				if 'application/rss+xml' in attr:
					for attr in attrs:
						if 'href' in attr:
							link = parse.unquote(attr[1])
							self.xmlSet.add(link)

		# # 获取IMG链接
		# if tag == 'img':
		# 	for attr in attrs:
		# 		if 'src' in attr or 'href' in attr:
		# 			link = parse.unquote(attr[1])
		# 			self.imgSet.add(link)

		# # 获取JS链接
		# if tag == 'script':
		# 	for attr in attrs:
		# 		if 'src' in attr:
		# 			self.jsSet.add(attr[1])


def autoBackSlash(string):
	if string.find('?') != -1:
		string = string.replace('?', '\?')
	return string 

def is_interior_url(realUrl, url):
	if parse.urlparse(realUrl).hostname == parse.urlparse(url).hostname:
		return True
	else:
		return False

def htmlFilter(url, html, parser):
	HTML = set()
	CSS = set()
	XML = set()
	DOWNLOAD = set()

	startPath = url2filePath(url)
	postfixList = ['.html', '.hml', '.shtml', 'shml', '']
	pattern = re.compile('(?<=\"|\')')

	# 处理html
	for link in parser.htmlSet:
		realUrl = parse.urljoin(url, link)
		if is_interior_url(realUrl, url):

			filePath = url2filePath(realUrl)

			relativePath = os.path.relpath(filePath, os.path.dirname(startPath))

			o = parse.urlparse(realUrl)
			if o.fragment != '':
				urlfile = realUrl.split('#')[0]
				relativePath = relativePath + '#' + o.fragment
			else:
				urlfile = realUrl

			html = re.sub('(?<=\"|\')%s(?=\"|\')'%link, relativePath, html)

			# 获取url后缀
			postfix = os.path.splitext(parse.urlparse(urlfile).path)[1]
			if postfix in postfixList:
				HTML.add(urlfile)

	# 处理CSS
	for link in parser.cssSet:
		realUrl = parse.urljoin(url, link)
		filePath = url2filePath(realUrl)
		relativePath = os.path.relpath(filePath, os.path.dirname(startPath))
		link = autoBackSlash(link)
		html = re.sub('(?<=\"|\')%s(?=\"|\')'%link, relativePath, html)
		CSS.add(realUrl)

	# 处理DOWNLOAD
	for info in parser.sourceSet:
		realUrl = parse.urljoin(url, info[1])
		filePath = url2filePath(realUrl, info[0])
		relativePath = os.path.relpath(filePath, os.path.dirname(startPath))
		link = autoBackSlash(info[1])
		html = re.sub('(?<=\"|\')%s(?=\"|\')'%link, relativePath, html)
		DOWNLOAD.add(realUrl)

	# 处理XML
	for link in parser.xmlSet:
		realUrl = parse.urljoin(url, link)
		filePath = url2filePath(realUrl)
		if os.path.splitext(filePath)[1] == '.html':
			filePath = os.path.splitext(filePath)[0] + '.xml'
		XML.add(realUrl)




	m = md5(url.encode('utf8'))
	hexdigest = str(m.hexdigest())

	html_txt_filename = 'data/html/html_' + hexdigest + '.txt'
	saveSet(html_txt_filename, HTML)

	css_txt_filename = 'data/css/css_' + hexdigest + '.txt'
	saveSet(css_txt_filename, CSS)

	xml_txt_filename = 'data/xml/xml_' + hexdigest + '.txt'
	saveSet(xml_txt_filename, XML)

	download_filename = 'data/download/download_' + hexdigest + '.json' 
	saveSet(download_filename, DOWNLOAD)

	status_filename = 'data/status/status_' + hexdigest + '.json'
	saveSet(status_filename)
	with open(status_filename, 'w') as f:
		d = {}
		d[url] = True
		json.dump(d, f, indent=2)

	startPath = 'website/' + startPath 

	dirName = os.path.dirname(startPath)
	if not os.path.exists(dirName):
		print(dirName)
		os.makedirs(dirName)
	with open(startPath, 'w') as f:
		f.write(html)

	with open(status_filename, 'w') as f:
		d = {url:True}
		json.dump(d, f, indent = 2)

def download_html(url, user_type, proxies):
	if user_type == 'pc':
		headers = {
		'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
		}
	elif user_type == 'phone':
		headers = {
		'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
		}
	
	if proxies != None:
		proxies = {
		'http:':proxies,
		'https':proxies
		}
	try:
		r = requests.get(url, headers=headers, proxies=proxies)
		r.raise_for_status()
		if not r.headers['Content-Type'].split(';')[0] == 'text/html':
			print('NO HTML')
			return None
		r.encoding = r.apparent_encoding
		# 反转义
		html = HTMLParser().unescape(r.text)
		html = parse.unquote(r.text)
		return r.url, html
	except:
		print(url + '  获取html失败！')
		return None

def cssFilter(url, css):
	imgSet = set()
	startPath = url2filePath(url)

	for link in re.findall('(?<=url\()[^\)]+', css):
		realUrl = parse.urljoin(url, link)
		filePath = url2filePath(realUrl)
		if link[:1] == '/' or link[:4] == 'http':
			realtivePath = os.path.relpath(filePath, os.path.dirname(startPath))
			css = re.sub('(?<=url\()%s(?=\))' %link, realtivePath, css)

		imgSet.add(realUrl)

	m = md5(url.encode('utf8'))
	hexdigest = str(m.hexdigest())
	fileName = 'data/img/img_' + hexdigest + '.txt'
	saveSet(fileName, imgSet)

	status_filename = 'data/status/status_' + hexdigest + '.json'
	saveSet(status_filename)
	with open(status_filename, 'w') as f:
		d = {}
		d[url] = True
		json.dump(d, f, indent=2)



def htmlrun(url, user_type='pc', proxies=None):

	url, html = download_html(url, user_type, proxies)
	# global html
	if html == None:
		return False
	html = HTMLParser().unescape(html)
	html = parse.unquote(html)
	parser = htmlParser()
	parser.feed(html)
	htmlFilter(url, html, parser)

def cssrun(url):
	try:
		r = requests.get(url)
		r.raise_for_status()
		css = r.text
		cssFilter(url, css)
	except:
		print('获取css失败')
		return

if __name__ == '__main__':

	htmlrun('https://www.leavesongs.com/')



		