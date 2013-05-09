#!/usr/bin/env python
# -*- encoding: utf8 -*-
from config import *
from threading import Thread
from urllib2 import urlopen
from HTMLParser import HTMLParser
import xml.etree.ElementTree as ET
import datetime, time, os, sys

class MLStripper(HTMLParser):
	def __init__(self):
		self.reset()
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return "".join(self.fed)

def strip_description(s):
	stripper = MLStripper()
	stripper.feed(s)
	return " ".join(stripper.get_data().split())[:DESCLENGTH]

def update_cache_thread():
	print "Refreshing cache"
	with open(CACHEFILE, "w") as f:
		page = urlopen(URL)
		f.write(page.read())
		page.close()

def get_xml_feed():
	# Do we have a previous cache?
	if os.path.isfile(CACHEFILE):
		# Is it time to refresh the cache?
		if int((time.time() - os.path.getmtime(CACHEFILE)) / 60.0) > UPDATEINTERVAL:
			thread = Thread(target=update_cache_thread)
			thread.start()
		return
	else:
		# First time running the script.
		# Save the cache and wait for the thread to finish.
		thread = Thread(target=update_cache_thread)
		thread.start()
		thread.join()

def get_jobs():
	get_xml_feed()
	tree = ET.parse(CACHEFILE)
	root = tree.getroot()
	# This is the fields we are extracting from each <job> node.
	keys = ["title", "date", "category", "region", "location", "detail-url", "apply-url", "description"]
	result = []
	for job in root.iter("job"):
		d = {}
		for k in keys:
			d[k] = job.find(k).text.encode("utf-8")
		# Convert the date string to a real date
		d["date"] = datetime.datetime.strptime(d["date"], "%m/%d/%Y").date()
		# Strip all HTML from the description
		d["description"] = strip_description(d["description"])
		result.append(d)
	# Return the list sorted by date (descending)
	return sorted(result, key=lambda k: k["date"], reverse=True)

def format_job(job):
	return "{date} [{apply-url}] ({title} in {location}) {description} See {detail-url} for more\n".format(**job)

def save_all(filename):
	with open(filename, "wt") as f:
		for job in get_jobs():
			f.write(format_job(job))

def save_latest(filename):
	with open(filename, "wt") as f:
		for job in get_jobs()[:20]:
			f.write(format_job(job))

def save_by_term(filename, term):
	with open(filename, "wt") as f:
		f.write("Searching for %s...\n" % term)
		for job in get_jobs():
			fields = "location region category description".split()	
			for field in fields:
				if term.lower() in job[field].lower():
					f.write(format_job(job))

def main():
	if len(sys.argv) != 3:
		print >> sys.stderr, "Usage: listjobs.py file [all|latest|search=term]"
		return 1

	filename, arg = "%s/%s" % (FEEDDIR, sys.argv[1]), sys.argv[2]

	if arg == "all":
		save_all(filename)
	elif arg == "latest":
		save_latest(filename)
	elif "search=" in arg:
		save_by_term(filename, arg.split("=")[1])
	else:
		print >> sys.stderr, "Unknown argument"

if __name__ == "__main__":
	exit(main())

