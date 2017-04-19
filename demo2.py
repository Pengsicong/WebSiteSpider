from html.parser import HTMLParser
from hashlib import md5
from urllib import parse
import os
import re



print(link.replace('?', '\?'))
relativePath = '22'
print(re.sub('(?<=\"|\')%s(?=\"|\')'%link, relativePath, html))

# dirname = os.path.dirname(dirname)

# o = parse.urlparse(filePath)
# print(o)
# filepath = o.hostname + o.path
# print(filepath)

# # print(parse.quote(filePath,safe=''))

# m = md5(filePath.encode('utf8'))

# print(os.path.splitext(parse.urlparse(filePath).path)[1])



