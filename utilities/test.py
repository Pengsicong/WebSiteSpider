from urllib import parse
from html.parser import HTMLParser
import os


if __name__ == '__main__':
	url = 'http://cn.gravatar.com/avatar/226b4231827a466e42e9418f068ee2f0?s=50&amp;d=wavatar&amp;r=G/001.jpg'

	o = parse.unquote(url)
	o = parse.urlsplit(o)
	filepath = o.netloc + o.path
	filepath = os.path.join('Website',filepath)

	if not os.path.exists(filepath):
		if not os.path.exists(os.path.dirname(filepath)):
			print(os.path.dirname(filepath))
			# os.makedirs(os.path.dirname(filepath))

	

	hp = HTMLParser()
	print(hp.unescape(url))

# print(parse.parse_qs(o.query))



	print(o)
#


