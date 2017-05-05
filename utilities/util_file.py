from urllib import parse
from html.parser import HTMLParser
# from util_conf import *
import os
import re

ALLOW_POSTFIX = [
'.html', '.jpg','.jpeg','.png','.gif','.bmp','.ico','.mp4a','.mp3','.wma','.js',
'.css','.pdf', '.m4a','.svg','ogg','.JPG'
]

def url2filePath(url, source_type = 'html'):
    postfixDict = {
        'html': '.html',
        'img': '.jpg',
        'text/javascript': '.js',
        'text/css': '.css',
        'script': '.js',
        'audio/mpeg': 'mp3',
        'source':'.mp3',
    }

    # 定义url格式
    pattern = re.compile('^(http).{1,200}$')
    if not re.match(pattern, url):
        # print(url,source_type)
        return None

    url = HTMLParser().unescape(url)
    url = parse.unquote(url)

    o = parse.urlparse(url)

    # 如果url带参数
    if o.query:
        file_postfix = os.path.splitext(o.path)
        filepath = o.hostname +  file_postfix[0] + '_' + '_'.join(o.query.split('=')) + file_postfix[1]
    else:
        filepath = o.hostname + o.path

    if o.path == '' or o.path[-1] == '/':
        filepath += '/index.html'

    dirName = os.path.dirname(filepath)
    if dirName.find('.html') != -1:
        dirName = dirName.replace('.html', '')

    fileName = os.path.basename(filepath)

    # 后缀名为空
    if os.path.splitext(fileName)[1] == '':
        try:
            fileName += postfixDict[source_type]
        except:
            pass

    # 后缀名为 “.asp”
    if os.path.splitext(fileName)[1] == '.asp':
        fileName = os.path.splitext(fileName)[0] + '.html'

    filepath = os.path.join(dirName, fileName)


    filepath = 'WWW/' + filepath


    # 后缀名过滤
    if not os.path.splitext(fileName)[1] in ALLOW_POSTFIX:
        # print(os.path.splitext(fileName)[1])
        return None

    return filepath

def saveSet(fileName, itemSet=None):

    dirName = os.path.dirname(fileName)
    if not os.path.exists(dirName):
        os.makedirs(dirName)

    if itemSet == None:
        return

    with open(fileName, 'w') as f:
        for item in itemSet:
            f.write(item + '\n')


if __name__ == '__main__':
    print(url2filePath('https://media.readthedocs.org/fonts/Inconsolata-Regular.ttf'))