#!/usr/bin/env python
from bitly_api import Connection
from os import environ
import cPickle as pickle

URLCACHE = "url_cache.pickle"

def url_shorten(url):
	url_cache = {}
	try:
		url_cache = pickle.load(open(URLCACHE, "rb"))
		if url_cache.has_key(url):
			return url_cache[url]
	except IOError:
		# Assuming File Not Found
		pass
	token = environ["BITLY_TOKEN"]
	conn = Connection(access_token=token)
	short_url = conn.shorten(url)
	url_cache[url] = short_url["url"]
	pickle.dump(url_cache, open(URLCACHE, "wb"))
	return short_url["url"]

def main():
    from sys import argv, stderr
    if len(argv) != 2:
        print >> stderr, "Usage: shorten.py url"
        return 1
    print url_shorten(argv[1])

if __name__ == "__main__":
    exit(main())
