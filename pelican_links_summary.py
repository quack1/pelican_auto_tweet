#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This script is used to create a page on a Pelican blog with the last links shared on Twitter.'''

__author__     = 'quack1'
__version__    = '0.9'
__date__       = '2014-05-27'
__copyright__  = 'Copyright © 2013-2014, Quack1'
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
import sys

# From http://code.google.com/p/python-twitter/
import twitter

import conf


TWITTER_API  = None
LAST_ID      = None
LAST_ID_FILE = "./.links_summary.id"
RE_URL       = r"(?P<url>https?://[^\s]+)"


def twitter_connect():
	'''Connect the API to Twitter with the OAuth protocol.'''
	global TWITTER_API
	TWITTER_API = twitter.Api(consumer_key=conf.Twitter.consumer_key, 
		consumer_secret=conf.Twitter.consumer_secret, access_token_key=conf.Twitter.access_token_key, 
    access_token_secret=conf.Twitter.access_token_secret)


# Get the id of the last tweet in which we find a link
if os.path.exists(LAST_ID_FILE):
	with open(LAST_ID_FILE, "r") as f:
		try:
			LAST_ID = int(f.readline())
		except exceptions.ValueError:
			LAST_ID = 0
else:
	LAST_ID = 0


# Connect to Twitter and get the tweets sent since the LAST_ID, limiting the
# result to 200 tweets.
twitter_connect()
print LAST_ID
tweets = TWITTER_API.GetUserTimeline(screen_name=conf.Links.twitter_username, since_id=LAST_ID, count=200, include_rts=False,exclude_replies=True)

# Get the timestamp for the last day
date_start = datetime.date.today() - datetime.timedelta(1)
date_end   = datetime.date.today()

date_start_timestamp = (date_start - datetime.date(1970, 1, 1)).total_seconds()
date_end_timestamp = (date_end - datetime.date(1970, 1, 1)).total_seconds()

# Generate the new content from the links
CONTENT = u""
urls = []

for tweet in tweets:
	timestamp = tweet.GetCreatedAtInSeconds()
	raw_text   = tweet.GetText()
	users = [x.screen_name for x in tweet.user_mentions]

	# If the tweet matches some criteria, its link will be shared on the
	# blog page.
	# The criteria are (in the 'if' order):
	#	- published in the last day
	#	- is not a mention to someone
	#	- is not a retweet
	#	- was not published automaticaly by the blog
	#	- is not a replay for one of the lastest articles.
	if timestamp >= date_start_timestamp and timestamp < date_end_timestamp and not raw_text.startswith("@") and not raw_text.startswith("RT") and not "#blog" in raw_text and not "#blogReplay" in raw_text:		
		
		final_text = u""

		# Is there a URL in the tweet ?
		res = re.search(RE_URL, raw_text)
		if not res:
			continue

		# Search each URL in the tweet
		for item in raw_text.split(" "):
			res = re.search(RE_URL, item)
			if res:
				# The item is a URL, and it's added to the text of the line
				# as a URL
				url = res.group("url")
				urls.append(url)
				final_text += u"[%s](%s) "%(url,url)
			elif item.startswith('@') and item[1:] in users:
				s = "[%s](https://twitter.com/%s)"%(item, item[1:])
				final_text += u"%s "s
			else:
				# The item is just a "word", and it's added too to the
				# line
				final_text += u"%s "%item
		## Replace every mention by a link to the user profile
		#for user in users:
		#	s = "[@%s](https://twitter.com/%s)"%(user, user)
		#	final_text = final_text.replace('@%s'%user, s)
		# Replace the commentary mark by its HTML equivalent.
		if final_text.startswith("#"):
			final_text = "&#35;" + final_text[1:]

		# Add the line to the content of the page
		CONTENT += u"\n\n%s"%final_text
		print raw_text.encode("utf-8")

# Generate the page header from a format in the configuration file.
# The 'now' timestamp is used to keep a trace of the latest modification
header = conf.Links.page_header%(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

if len(sys.argv) >= 2:
	base_dir = sys.argv[1]
elif conf.Global.blog_directory:
	base_dir = conf.Global.blog_directory
else:
	base_dir = './'

print base_dir

os.chdir(base_dir)
# Get the lastest version of the sources from the git repository
# Pull the last modifications in the git repository
os.system('git pull --commit --no-edit')

# The content is written in the source file
# The resulting source will be :
#	- HEADER
#	- New content
#	- Previous content
with open(conf.Links.out_file+"_tmp",'w') as f:
	f.write(header+"\n")
	f.write(CONTENT.encode("utf-8")+"\n")
	# Read the old content
	with open(conf.Links.out_file, "r") as fIn:
		# Pass the old header
		for c in xrange(header.count('\n')+1):
			fIn.readline()
		# Add the other lines (the real content)
		line = fIn.readline()
		while line:
			f.write(line)
			line = fIn.readline()

# Remove the old page source file, and move the temporary source file
# to the real page source file.
os.remove(conf.Links.out_file)
os.rename(conf.Links.out_file+"_tmp", conf.Links.out_file)

# Add the modifications and commit them
fname = conf.Links.out_file.replace(base_dir, '')
os.system('git add %s'%fname)
os.system('git commit -m "Add new Twitter links"')
# Push our updates
os.system('git push')
# Generate and upload the blog
os.system('make ssh_upload')

# Write the new last ID in the log file
if len(tweets):
	LAST_ID = tweets[0].GetId()
	with open(LAST_ID_FILE, "w") as f:
		f.write(str(LAST_ID))

# If new links were added, commit the modifications and exit with
# a custom error code
if len(urls) > 0:
	# Commit and push the new updates into the git repository
	os.system('git add %s'%conf.Links.out_file)
	os.system('git commit -m "Add %d new Twitter links"'%len(urls))
	os.system('git push')
	# Generate and upload the blog
	os.system('make ssh_upload')
	# Exit
	sys.exit(0)
else:
	sys.exit(1)

# END
