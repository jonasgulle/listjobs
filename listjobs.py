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
	tempfile = "%s.part" % CACHEFILE
	if os.path.isfile(tempfile):
		print "Update is pending"
		return

	print "Refreshing cache"

	outfile = open(tempfile, "w")
	page = urlopen(URL)
	outfile.write(page.read())
	page.close()
	outfile.close()

	if os.path.isfile(CACHEFILE):
		os.remove(CACHEFILE)

	os.rename(tempfile, CACHEFILE)

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
	return "{date} [{apply-url}] ({title} in {location}) {description}... See {detail-url} for more".format(**job)

def get_all():
	return [format_job(job) for job in get_jobs()]

def get_latest():
	return [format_job(job) for job in get_jobs()[:20]]

def get_by_term(term):
	ret = []
	for job in get_jobs():
		fields = "location title region category description".split()	
		for field in fields:
			if job[field].lower().find(term.lower()) != -1:
				ret.append(format_job(job))
	return ret

def main():
	if len(sys.argv) != 2:
		print >> sys.stderr, "Usage: listjobs.py [all|latest|search=term]"
		return 1

	arg = sys.argv[1]

	if arg == "all":
		print get_all()
	elif arg == "latest":
		print "".join(get_latest())
	elif "search=" in arg:
		print get_by_term(arg.split("=")[1])
	else:
		print >> sys.stderr, "Unknown argument"

if __name__ == "__main__":
	exit(main())

