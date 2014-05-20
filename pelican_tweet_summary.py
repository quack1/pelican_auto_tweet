#! /usr/bin/env python
# -*- coding: utf-8 -*- 

'''This script is used to automaticaly tweet links to the blog posts published in the
	last 7 days on the blog.
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

import datetime
import os
import re
import sys
import time
from HTMLParser import HTMLParser

# From http://code.google.com/p/python-twitter/
import twitter
# From https://github.com/bitly/bitly-api-python
import bitly_api as bitlyapi
import unicodedata

from conf import *



TODAY          = datetime.date.today()
TWITTER_API    = None
FIRST_TWEETED  = False
SLUGS          = []
DATES          = []
TITLES         = []
BITLY_API      = None
LOG_FILE       = '/var/log/pelican_auto_tweet/summary.log'

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

def first_tweet(msg):
	global FIRST_TWEETED
	if not FIRST_TWEETED:
		twitter_send(msg)
		FIRST_TWEETED = True

# Check arguments
if len(sys.argv) >= 2:
	base_dir = sys.argv[1]
elif BASE_DIR:	# BASE_DIR comes from conf.py
	base_dir = BASE_DIR
else:
	base_dir = './'

BLOG = libpelican.PelicanBlog(base_dir)

# Get number of days for which posts should be considered as new
try:
	if SUMMARY_DAYS < 0:
		SUMMARY_DAYS = 0
except:
	print('Using default number of days : 7')
	SUMMARY_DAYS = 7

# Get interval between 2 Twitter updates
try:
	if SUMMARY_INTERVAL < 0:
		SUMMARY_INTERVAL = 0
except:
	print('Using default interval : 180')
	SUMMARY_INTERVAL = 180


BLOG.get_site_base_url()

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

for post_filename in BLOG.get_posts:
	post_date = BLOG.get_post_date(post_filename).date()
	if post_date+datetime.timedelta(SUMMARY_DAYS) >= TODAY:
		title = BLOG.get_post_title(post_filename)
		url   = BLOG.get_post_url(post_filename)
		if not url in SLUGS:
			SLUGS.append(url)
			DATES.append(post_date)
			TITLES.append(title)	

#---------------------------------------------------
# TWEET_FORMAT for tweets
#---------------------------------------------------
if not TWEET_FORMAT_SUMMARY:
	TWEET_FORMAT_SUMMARY = '#blogReplay $$POST_TITLE$$ $$POST_URL$$ #blog'

# Get the length of 'pure' text of the TWEET_FORMAT. 
# We suppress 
TWEET_FORMAT_LENGTH = len(TWEET_FORMAT_SUMMARY)
if '$$POST_TITLE$$' in TWEET_FORMAT_SUMMARY:
	TWEET_FORMAT_LENGTH -= len('$$POST_TITLE$$')
if '$$POST_URL$$' in TWEET_FORMAT_SUMMARY:
	TWEET_FORMAT_LENGTH -= len('$$POST_URL$$')

#---------------------------------------------------
# Text for first tweet
#---------------------------------------------------
#if not IS_TWEET_SUMMARY_BEGIN:
#	IS_TWEET_SUMMARY_BEGIN = True
if IS_TWEET_SUMMARY_BEGIN:
	if not TWEET_SUMMARY_BEGIN:
		TWEET_SUMMARY_BEGIN = '#blogReplay Voici les articles publiés ces %d derniers jours sur $$BLOG_URL$$'%(SUMMARY_DAYS)
	if '$$BLOG_URL$$' in TWEET_SUMMARY_BEGIN:
		TWEET_SUMMARY_BEGIN = TWEET_SUMMARY_BEGIN.replace('$$BLOG_URL$$', SITE_BASE_URL)

#---------------------------------------------------
# Text for last tweet
#---------------------------------------------------
#if not IS_TWEET_SUMMARY_END:
#	IS_TWEET_SUMMARY_END = True
if IS_TWEET_SUMMARY_END: 
	if not TWEET_SUMMARY_END_ONE:
		TWEET_SUMMARY_END_ONE = "#blogReplay C'était le seul article publié cette semaine. Fin du spam! :)"
	if not TWEET_SUMMARY_END_MANY:
		TWEET_SUMMARY_END_MANY = "#blogReplay C'était les %d articles publiés cette semaine. Fin du spam! :)"


with open(LOG_FILE, 'a') as log_file:
	log_file.write('[%s] %s'%(TODAY, BASE_DIR) + "\n")
	# Generate summary
	if len(SLUGS):
		POSTS = []
		for i in xrange(len(SLUGS)):
			article = {'url':SLUGS[i],'date':DATES[i],'title':TITLES[i]}
			POSTS.append(article)
		POSTS.sort(key=lambda item:item['date'])
		
		if IS_TWEET_SUMMARY_BEGIN:
			first_tweet(TWEET_SUMMARY_BEGIN)

		for a in POSTS:
			time.sleep(SUMMARY_INTERVAL)

			url = a['url']

			if BITLY_API:
				s = BITLY_API.shorten(url)
				u = s['url']
				url = unicodedata.normalize('NFKD', u).encode('ascii','ignore')
			
			title = a['title']

			# Calculate maximum length for the title : 
			# 140 (max length for a tweet) - length of TWEET_TEXT - spaces - length of URL
			max_length = 140 - TWEET_FORMAT_LENGTH - 5 - len(url)
			if len(title) >= max_length:
				title = "%s%s"%(title[:max_length],"...")

			# Generate tweet message from TWEET_FORMAT
			tweet_text = TWEET_FORMAT_SUMMARY.replace('$$POST_TITLE$$', title)
			tweet_text = tweet_text.replace('$$POST_URL$$', url)
			tweet_text = strip_tags(tweet_text)

			# Post tweet
			twitter_send(tweet_text)
			log_file.write(tweet_text + "\n")
			
		if IS_TWEET_SUMMARY_END:
			if len(SLUGS) == 1:
				twitter_send(TWEET_SUMMARY_END_ONE)
				log_file.write(TWEET_SUMMARY_END_ONE + "\n")
			else:	
				twitter_send(TWEET_SUMMARY_END_MANY%len(SLUGS))
				log_file.write(TWEET_SUMMARY_END_MANY%len(SLUGS) + "\n")
	else:
		log_file.write("No new posts\n")

sys.exit(0)
