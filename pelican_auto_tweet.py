#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This script is used to automaticaly tweet link of the last published post from
a Pelican blog.
Both Markdown and Rest syntax are supported. The 'Slug' tag **has** to be set
	so the script can create the complete URL of the post.
'''

__author__     = 'quack1'
__version__    = '0.6'
__date__       = '2014-05-27'
__copyright__  = 'Copyright © 2013-2014, Quack1'
__licence__    = 'BSD'
__credits__    = ['Quack1']
__maintainer__ = 'Quack1'
__email__      = 'quack@quack1.me'
__status__     = 'Development'

import re
import os.path
import sys
import commands
import unicodedata
import os
from HTMLParser import HTMLParser

# From https://github.com/bitly/bitly-api-python
import bitly_api as bitlyapi
# From http://code.google.com/p/python-twitter/
import twitter

import conf
import libpelican

TWITTER_API = None
BITLY_API   = None
BLOG        = None

#
# From http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
#
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def twitter_connect():
	'''Connect the API to Twitter with the OAuth protocol.'''
	global TWITTER_API
	TWITTER_API = twitter.Api(consumer_key=conf.Twitter.consumer_key, 
		consumer_secret=conf.Twitter.consumer_secret, access_token_key=conf.Twitter.access_token_key, 
    	access_token_secret=conf.Twitter.access_token_secret)

def twitter_send(text):
	'''Post a new tweet on Twitter.
	If the API is not connected, a call to twitter_connect() is made.'''
	if not TWITTER_API:
		twitter_connect()
	TWITTER_API.PostUpdate(text)
	print(text)


# Check arguments
# If one argument is passed, it will be considered as the base blog directory.
# If it's not present, the current working directory will be used.
if len(sys.argv) >= 2:
	base_dir = sys.argv[1]
elif conf.Global.blog_directory:
	base_dir = conf.Global.blog_directory
else:
	base_dir = './'

print base_dir

# A new blog instance is created on this directory.
BLOG = libpelican.PelicanBlog(base_dir)

# Try to connect to BitlyAPI
try:
	if not conf.Bitly.user:
		print("Error. No conf.Bitly.user defined.")
	if not conf.Bitly.api_key:
		print("Error. No conf.Bitly.api_key defined.")
	BITLY_API = bitlyapi.Connection(conf.Bitly.user, conf.Bitly.api_key)
	# Test Bitly connection. If the link to Bitly API is down, an exception is thrown and
	# Bitly will not be used.
	BITLY_API.lookup(BLOG.get_site_base_url())
except:
	BITLY_API = None

# Move to the blog base directory, and get the last commit message and the last
# commited files. 
os.chdir(BLOG.get_base_directory())
result = commands.getoutput('git show --pretty="format:%s" --name-only')

# The first line is the commit message. The following lines contain the filenames.
log_message = result.splitlines()[0]
files       = result.splitlines()[1:]

# Get the tweet format from the configuration file. If the format is not present,
# a default one is created.
if not conf.Auto.tweet_format:
	TWEET_FORMAT_AUTO = '$$POST_TITLE$$ $$POST_URL$$ #blog'
else:
	TWEET_FORMAT_AUTO = conf.Auto.tweet_format

# If the log message starts by '[POST]', it means that (at least) one new post was 
# writen and needs to be published. 
if log_message.startswith('[POST]'):

	f = []
	for x in files:
		name = os.path.basename(x)
		b,ext = os.path.splitext(name)
		if ext in ('.md', '.rst'):
			f.append(name)
	# Check that there is no drafts in the commited articles. 
	if BLOG.posts_have_drafts(f):
		print "You are about to publish drafts."
		response = raw_input("Do you want to publish them (y-n) ? [n]")
		if not response:
			response = "N"
		while response.upper() not in ("N", "Y"):
			response = raw_input("Do you want to publish them (y-n) ? [n]")
			if not response:
				response = "N"
		if response.upper() == "N":
			sys.exit(2)

	# Pull the last modifications in the git repository
	os.system('git pull --commit --no-edit')
	# Push our updates
	os.system('git push')
	# Generate and upload the blog
	os.system('make ssh_upload')

	# A new tweet is sent for each commited article.
	for filename in files:
		post_filename = os.path.basename(filename)
		base, ext     = os.path.splitext(filename)
		# An article is a '.rst' or '.md' file in the 'content/' directory.
		if base.startswith('content/') and ext in ('.rst','.md'):
			title = BLOG.get_post_title(post_filename)
			url   = BLOG.get_post_url(post_filename)

			# Shorten the link if Bitly is used.
			if BITLY_API:
				s = BITLY_API.shorten(url)
				u = s['url']
				url = unicodedata.normalize('NFKD', u).encode('ascii','ignore')

			# Generate tweet message from TWEET_FORMAT_AUTO
			tweet_text = TWEET_FORMAT_AUTO.replace('$$POST_TITLE$$', title)
			tweet_text = tweet_text.replace('$$POST_URL$$', url)
			tweet_text = strip_tags(tweet_text)

			# Post tweet
			twitter_send(tweet_text)

#END
