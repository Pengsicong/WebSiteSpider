from urllib import parse
import os
import re

def url2filePath(url, source_type = 'html'):
    postfixDict = {
        'html': '.html',
        'img': '.jpg',
        'text/javascript': '.js',
        'audio/mpeg': 'mp3',
        'source':'.mp3',
    }
    o = parse.urlparse(url)
   
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

    filepath = os.path.join(dirName, fileName)

    return filepath

if __name__ == '__main__':
    print(url2filePath('http://www.baidu.com/'))