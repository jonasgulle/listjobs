#!/usr/bin/env python
# -*- encoding: utf8 -*-
from config import *
from threading import Thread
from urllib2 import urlopen
import xml.etree.ElementTree as ET
import datetime, time, os, sys

def update_cache_thread():
	tempfile = "%s.part" % CACHEFILE
	with open(tempfile, "w") as f:
		page = urlopen(URL)
		f.write(page.read())
		page.close()
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
		result.append(d)
	# Return the list sorted by date (descending)
	return sorted(result, key=lambda k: k["date"], reverse=True)

def main():
	jobs = get_jobs()
	for job in jobs:
		print job["date"],

if __name__ == "__main__":
	main()
