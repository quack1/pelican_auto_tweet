#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This script is used to automaticaly tweet link of the last published post from
a Pelican blog.
Both Markdown and Rest syntax are supported. The 'Slug' tag **have** to be set
	so the script can create the complete URI to the post.
'''

__author__     = 'quack1'
__version__    = '0.4'
__date__       = '2013-11-11'
__copyright__  = 'Copyright © 2013, Quack1'
__licence__    = 'BSD'
__credits__    = ['Quack1']
__maintainer__ = 'Quack1'
__email__      = 'quack@quack1.me'
__status__     = 'Development'

import exceptions
import datetime
import os
import os.path
import re

# From http://code.google.com/p/python-twitter/
import twitter

from conf import *



TWITTER_API  = None
LAST_ID      = None
LAST_ID_FILE = "./.links_summary.id"
RE_URL       = r"(?P<url>https?://[^\s]+)"


def twitter_connect():
	'''Connect the API to Twitter with the OAuth protocol.'''
	global TWITTER_API
	TWITTER_API = twitter.Api(consumer_key=CONSUMER_KEY, 
		consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, 
    access_token_secret=ACCESS_TOKEN_SECRET)


# Get the id of the last tweet for which we got a link
if os.path.exists(LAST_ID_FILE):
	with open(LAST_ID_FILE, "r") as f:
		try:
			LAST_ID = int(f.readline())
		except exceptions.ValueError:
			LAST_ID = 0
else:
	LAST_ID = 0


# Connect to Twitter and get tweets
twitter_connect()
print LAST_ID
tweets = TWITTER_API.GetUserTimeline(screen_name=TWITTER_USERNAME, since_id=LAST_ID, count=200, include_rts=False,exclude_replies=True)

# Get Timestamp for last day
date_start = datetime.date.today() - datetime.timedelta(1)
date_end   = datetime.date.today()

date_start_timestamp = (date_start - datetime.date(1970, 1, 1)).total_seconds()
#date_start_timestamp = 0
date_end_timestamp = (date_end - datetime.date(1970, 1, 1)).total_seconds()


# Generate content with the links
CONTENT = u""

for tweet in tweets:
	timestamp = tweet.GetCreatedAtInSeconds()
	raw_text   = tweet.GetText()

	if timestamp >= date_start_timestamp and timestamp < date_end_timestamp and not raw_text.startswith("@") and not raw_text.startswith("RT") and not "#blog" in raw_text and not "#blogReplay" in raw_text:		
		
		final_text = u""
		urls       = []

		res = re.search(RE_URL, raw_text)
		if not res:
			continue

		# Search each url in the tweet
		for item in raw_text.split(" "):
			res = re.search(RE_URL, item)
			if res:
				# The item is an url
				url = res.group("url")
				urls.append(url)
				final_text += u"[%s](%s) "%(url,url)
			else:
				# The item is just a "word"
				final_text += u"%s "%item
		if final_text.startswith("#"):
			final_text = "&#35;" + final_text[1:]
		CONTENT += u"\n\n%s"%final_text

# Generate the page header
header = PAGE_HEADER%(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

# Write the content in the source file
with open(LINKS_OUT_FILE+"_tmp",'w') as f:
	f.write(header+"\n")
	f.write(CONTENT.encode("utf-8")+"\n")
	with open(LINKS_OUT_FILE, "r") as fIn:
		for c in xrange(header.count('\n')+1):
			fIn.readline()
		line = fIn.readline()
		while line:
			f.write(line)
			line = fIn.readline()
os.remove(LINKS_OUT_FILE)
os.rename(LINKS_OUT_FILE+"_tmp", LINKS_OUT_FILE)


# Write the new last ID
if len(tweets):
	LAST_ID = tweets[0].GetId()
	with open(LAST_ID_FILE, "w") as f:
		f.write(str(LAST_ID))