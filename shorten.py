#!/usr/bin/env python
from bitly_api import Connection
from os import environ

def shorten(url):
    token = environ["BITLY_TOKEN"]
    conn = Connection(access_token=token)
    short_url = conn.shorten(url)
    return short_url["url"]

def main():
    from sys import argv, stderr
    if len(argv) != 2:
        print >> stderr, "Usage: shorten.py url"
        return 1
    print shorten(argv[1])

if __name__ == "__main__":
    exit(main())
