from html.parser import HTMLParser
from hashlib import md5
from urllib import parse
import os
import re
import redis


r = redis.Redis(host='localhost', port=6379, db=0)


