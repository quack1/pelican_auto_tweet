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

from conf import *

BASE_DIR = ''
SITE_BASE_URL = ''
REGEX_BASE_URL = re.compile(r'SITEURL = \'(.*)\'',re.IGNORECASE)
REGEX_TITLE = re.compile(r'Title:\s+(.*)',re.IGNORECASE)
REGEX_SLUG = re.compile(r'Slug:\s+(.*)',re.IGNORECASE)
REGEX_STATUS = re.compile(r'Status:\s*(.*)', re.IGNORECASE)
TWITTER_API = None
BITLY_API = None

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
	TWITTER_API = twitter.Api(consumer_key=CONSUMER_KEY, 
		consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, 
    access_token_secret=ACCESS_TOKEN_SECRET)

def twitter_send(text):
	'''Post an update on Twitter.
	If the API is not connected, a call to twitter_connect() is made.'''
	if not TWITTER_API:
		twitter_connect()
	TWITTER_API.PostUpdate(text)
	print(text)

def get_site_base_url():
	'''Get the site base url from the pelicanconf.py file.
	The file must be located at ../pelicanconf.py related to the base 
	directory given in the parameter of the script'''
	global SITE_BASE_URL
	f = open(os.path.join(BASE_DIR,"pelicanconf.py"))
	if f:
		for l in f:
			res = REGEX_BASE_URL.search(l)
			if res:
				SITE_BASE_URL = res.group(1)
				if not SITE_BASE_URL.endswith('/'):
					SITE_BASE_URL += '/'
				break
		f.close()

def get_post_infos(filename):
	'''Get the base informations necessary to build the text send 
	to Twitter from the post source file. The 2 read tags are 'title'
	and 'slug'.'''
	title,url = '',''
	with open(os.path.join(BASE_DIR, filename),"r") as f:
		for line in f:
				res = REGEX_TITLE.search(line)
				if res:
					title = res.group(1)
				else:
					res = REGEX_SLUG.search(line)
					if res:
						url = res.group(1)
	if not url:
		url = ''
	return title,url

def articles_contains_draft(articles):
	'''Get the status of an article. 
	Returns True if the article is a draft. Else, returns False.
	The file must be located in BASE_DIR.'''
	contains_draft = False
	for filename in articles:
		with open(os.path.join(BASE_DIR,filename), 'r') as f:
			for l in f:
				res = REGEX_STATUS.search(l)
				if res:
					if res.group(1).strip().upper() == "DRAFT":
						contains_draft = True
	return contains_draft


# Check arguments
if len(sys.argv) >= 2:
	BASE_DIR = sys.argv[1]
elif not BASE_DIR:
	BASE_DIR = './'


if not BASE_DIR:
	print 'Error... No content dir'
	sys.exit(2)

# Trying to connect to BitlyAPI
try:
	if not BITLY_USER:
		print("Error. No BITLY_USER defined.")
	if not BITLY_API_KEY:
		print("Error. No BITLY_API_KEY defined.")
	BITLY_API = bitlyapi.Connection(BITLY_USER, BITLY_API_KEY)
	# Test Bitly connection. If the link to Bitly API is down, an exception is thrown and
	# Bitly will not be used.
	BITLY_API.lookup(SITE_BASE_URL)
except:
	BITLY_API = None

get_site_base_url()
if not SITE_BASE_URL.endswith('/') : 
	SITE_BASE_URL = SITE_BASE_URL + '/'

os.chdir(BASE_DIR)
result = commands.getoutput('git show --pretty="format:%s" --name-only')

log_message = result.splitlines()[0]
files = result.splitlines()[1:]

if not TWEET_FORMAT_AUTO:
	TWEET_FORMAT_AUTO = '$$POST_TITLE$$ $$POST_URL$$ #blog'



if log_message.startswith('[POST]'):

	# Check that we are not publishing a draft
	if articles_contains_draft(files):
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

	os.system('git pull --commit --no-edit')
	os.system('git push')
	os.system('make ssh_upload')
	for filename in files:
		base, ext = os.path.splitext(filename)
		if base.startswith('content/') and ext in ('.rst','.md'):
			title,slug = get_post_infos(os.path.join(BASE_DIR, filename))
			url = SITE_BASE_URL + slug + ".html"

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
sys.exit(0)
