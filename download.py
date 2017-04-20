import json
import requests
from utilities.util_file import url2filePath, saveSet


def downloads():
	with open('data/download/total_download.json', 'w') as f:
		d = json.load(f)
	for filePath in d:
		download(filePath, d[filePath])


def download(filePath, url):
	filePath = 'website/' + filePath
	try:
		r = requests.get(url)
		r.encoding = r.apparent_encoding
		# contentType = r.headers['Content-Type'].split(';')[0]
		saveSet(filePath)
		with open(filePath, 'wb') as f:
			f.write(r.content)
	except:
		print(url, ' 下载失败！')

if __name__ == '__main__':
	download('')	
