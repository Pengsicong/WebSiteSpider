__all__ = [
    "REDOWNLOAD_TIMES",
    "ALLOW_POSTFIX",
    "HEADERS_PC",
    "HEADERS_PHONE",
    "BoundedSemaphoreNum",
    "MAX_DEEP",
    "MAX_PAGENUM",
    "CRAWL_TYPE",
    "PROXIES",
]

# 定义下载失败时，重试次数
REDOWNLOAD_TIMES = 3

# 定义协程数
BoundedSemaphoreNum = 30

# 下载深度, 0为全站下载
MAX_DEEP = 1

# 限制下载网页数， 0为不限制
MAX_PAGENUM = 0

# 抓取类型 'pc'为电脑端， 'phone'为手机端
CRAWL_TYPE = 'pc'

# 是否设置代理
PROXIES = 'localhost:8087'

# 允许下载的文件类型
ALLOW_POSTFIX = [
'.html', '.jpg','.jpeg','.png','.gif','.bmp','.ico',
'.mp4a','.mp3','.wma','.js','.css','.pdf',
]


HEADERS_PC = {
	'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}

HEADERS_PHONE = {
	'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
}

if __name__ == '__main__':
	pass
