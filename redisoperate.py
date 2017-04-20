from redis import Redis


# 批量删除
def redisDeletes(keylist, redis):
	for key in keylist:
		redis.delete(key)

# 批量合并set
def redisMerge(keylist, redis, targe):
	if keylist == []:
		return
	redis.sunionstore(targe, keylist)



if __name__ == '__main__':
	redis = Redis()
	keylist = redis.keys()
	redisMerge(keylist, redis, 'M')
	redisDeletes(keylist, redis)
	print(redis.keys())
