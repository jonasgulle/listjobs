#!/usr/bin/env python

# The URL feed to use
url = "https://www.spotify.com/se/jobs/vacancies/"

# List of servers to connect to during startup.
# Leave the password blank ("") if the server doesn't require a password.
servers = [
	{
		"host": "irc.gulle.se",
		"nick": "spotifyjobs",
		"port": 6667,
		"password": "",
		"channels": ["#test"]
	},
	# Add another here.
]
