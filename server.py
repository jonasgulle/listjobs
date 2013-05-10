#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from wsgiref.simple_server import make_server
import listjobs

PORT = 8000

def jobs_app(environment, start_response):
	#ret = "\n".join(["%s=%s" % (k, v) for k, v in dict.items(environment)])
	ret = ""
	arg = environment["PATH_INFO"]
	if "/all" == arg:
		ret = listjobs.get_all()
	elif "/latest" == arg:
		ret = listjobs.get_latest()
	elif "/search=" in arg:
		ret = listjobs.get_by_term(arg.split("=")[-1])

	status = "200 OK"
	headers = [
		("content-type", "text/plain"),
		("content-length", str(len(ret)))
	]

	start_response(status, headers)
	return [ret]

httpd = make_server("", PORT, jobs_app)
print "Serving on port %d..." % PORT

try:
	httpd.serve_forever()
except KeyboardInterrupt:
	print "Exiting..."

