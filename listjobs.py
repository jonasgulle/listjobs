#!/usr/bin/env python
# -*- encoding: utf8 -*-
import config
from urllib2 import urlopen
from shorten import url_shorten
from bs4 import BeautifulSoup

def scrape_jobs(limit=None, search=None):
	page = urlopen(config.url)
	soup = BeautifulSoup(page)
	page.close()

	def is_vacoffer_class(tag):
		return tag.has_attr("class") and "vacoffer" in tag["class"]

	def format_job(job):
		return u"{title} | {location} | {url}".format(**job)

	jobs = []
	parent_div = soup.find("div", {"class": "vacbox2"})
	for c in parent_div.find_all(is_vacoffer_class, limit=limit):
		url = "https://www.spotify.com" + c.a.get("href")
		title = c.a.contents[0].text
		location = c.a.contents[1]
		pos = location.find("-")
		if pos != -1:
			location = location[pos+1:].strip()
		job = {"title": title, "location": location, "url": url}

		if search:
			try:
				if "".join(job.values()).lower().find(search.lower()) > 0:
					job["url"] = url_shorten(job["url"])
					yield(format_job(job))
			except UnicodeError:
				pass
		else:
			job["url"] = url_shorten(job["url"])
			yield(format_job(job))

def main():
	import sys
	if len(sys.argv) != 2:
		print >> sys.stderr, "Usage: listjobs.py [all|latest|search=term]"
		return 1

	arg = sys.argv[1]

	def print_jobs(jobs):
		for job in jobs:
			print job

	if arg == "all":
		print_jobs(scrape_jobs())
	elif arg == "latest":
		print_jobs(scrape_jobs(limit=10))
	elif "search=" in arg:
		print_jobs(scrape_jobs(search=arg.split("=")[1]))
	else:
		print >> sys.stderr, "Unknown argument"
		return 1

	return 0

if __name__ == "__main__":
	exit(main())

