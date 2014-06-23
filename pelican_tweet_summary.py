#! /usr/bin/env python
# -*- coding: utf-8 -*- 

'''This script is used to automaticaly tweet links to the blog posts published in the
	last 7 days on the blog.
Both Markdown and Rest syntax are supported. The 'Slug' tag **has** to be set
	so the script can create the complete URI to the post.
'''

__author__     = 'quack1'
__version__    = '0.7'
__date__       = '2014-05-27'
__copyright__  = 'Copyright © 2013-2014, Quack1'
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

import conf
import libpelican



TODAY         = datetime.date.today()
TWITTER_API   = None
FIRST_TWEETED = False
SLUGS         = []
POSTS         = []
BITLY_API     = None
LOG_FILE      = '/var/log/pelican_auto_tweet/summary.log'

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
# If one argument is passed, it will be considered as the base blog directory.
# If it's not present, the current working directory will be used.
if len(sys.argv) >= 2:
	base_dir = sys.argv[1]
elif conf.Global.blog_directory:	# BASE_DIR comes from conf.py
	base_dir = conf.Global.blog_directory
else:
	base_dir = './'

# A new blog instance is created on this directory.
BLOG = libpelican.PelicanBlog(base_dir)

# Get in the configuration file the number of days for which posts should be 
# considered as new. If the configuration file is not present a default value
# is used.
days = 0
try:
	if conf.Summary.days < 0:
		days = 0
	else:
		days = conf.Summary.days
except:
	print('Using default number of days : 7')
	days = 7

# Get in the configuration file the interval between two new twitter updates.  
# If the configuration file is not present a default value is used. The value 
# is in seconds.
interval = 0
try:
	if conf.Summary.interval < 0:
		interval = 0
	else:
		interval = conf.Summary.interval
except:
	print('Using default number of interval : 180s')
	interval = 180


# Trying to connect to BitlyAPI
try:
	if not conf.Bitly.user:
		print("Error. No conf.Bitly.user defined.")
	if not conf.Bitly.api_key:
		print("Error. No conf.Bitly.api_key defined.")
	BITLY_API = bitlyapi.Connection(conf.Bitly.user, conf.Bitly.api_key)
	# Test Bitly connection. If the link to Bitly API is down, an exception is 
	# thrown and Bitly will not be used.
	BITLY_API.lookup(BLOG.get_site_base_url())
except:
	BITLY_API = None


# Get all the blog articles. For every article published in the last 
# `conf.Summary.days` days, a tweet will be published.
# Tweets are not sent for the drafts.
# A new array is created with the blog posts that have to be tweeted.
# This array contains dicts containing :
#	- the URL of the article
#	- the date of the article
#	- and its title.
# This array is finally sorted by the publication date.
for post_filename in BLOG.get_posts():
	if not BLOG.is_draft(post_filename):
		post_date = BLOG.get_post_date(post_filename).date()
		if post_date + datetime.timedelta(days) >= TODAY:
			title = BLOG.get_post_title(post_filename)
			url   = BLOG.get_post_url(post_filename)
			if not url in SLUGS:
				p = dict()
				p['url'] = url
				p['date'] = post_date
				p['title'] = title
				SLUGS.append(url)
				POSTS.append(p)
POSTS.sort(key=lambda item:item['date'])

# Get the tweet format from the configuration file. If the format is not present,
# a default one is created.
if not conf.Summary.tweet_format:
	TWEET_FORMAT = '#blogReplay $$POST_TITLE$$ $$POST_URL$$ #blog'
else:
	TWEET_FORMAT = conf.Summary.tweet_format

# Get the length of 'pure' text of the TWEET_FORMAT. 
# We suppress, by now, two variables : 
#	- $$POST_TITLE$$ -> Will be replaced by the title of the article
#	- $$POST_URL$$ -> Will be replaced by the URL to the article
TWEET_FORMAT_LENGTH = len(TWEET_FORMAT)
if '$$POST_TITLE$$' in TWEET_FORMAT:
	TWEET_FORMAT_LENGTH -= len('$$POST_TITLE$$')
if '$$POST_URL$$' in TWEET_FORMAT:
	TWEET_FORMAT_LENGTH -= len('$$POST_URL$$')

# Get the text for the first tweet from the configuration file. If the format is 
# not present, a default one is used.
# Only one variable can be used in the format : 
#	- $$BLOG_URL$$ -> Will be replaced by the URL ot the blog
if conf.Summary.tweet_begin:
	if not conf.Summary.tweet_format_begin:
		TWEET_BEGIN = '#blogReplay Voici les articles publiés ces %d derniers jours sur $$BLOG_URL$$'%(days)
	else:
		TWEET_BEGIN = conf.Summary.tweet_format_begin
	if '$$BLOG_URL$$' in TWEET_BEGIN:
		TWEET_BEGIN = TWEET_BEGIN.replace('$$BLOG_URL$$', BLOG.get_site_base_url())

# Get the text for the last tweet from the configuration file. If the format is 
# not present, a default one is used.
# No variable can be used in the format
if conf.Summary.tweet_end: 
	if not conf.Summary.tweet_format_end_one:
		TWEET_END_ONE = "#blogReplay C'était le seul article publié cette semaine. Fin du spam! :)"
	else:
		TWEET_END_ONE = conf.Summary.tweet_format_end_one

	if not conf.Summary.tweet_format_end_many:
		TWEET_END_MANY = "#blogReplay C'était les %d articles publiés cette semaine. Fin du spam! :)"
	else:
		TWEET_END_MANY = conf.Summary.tweet_format_end_many


# After opening the log file, the tweets are sent.
with open(LOG_FILE, 'a') as log_file:
	log_file.write('[%s] %s'%(TODAY, base_dir) + "\n")
	if len(POSTS):		
		# Post the first tweet
		if conf.Summary.tweet_begin:
			first_tweet(TWEET_BEGIN)

		# Post a new tweet for each article
		for a in POSTS:
			time.sleep(interval)

			# Get the title and the URL of the article and, if necessary, 
			# shorten it.
			title = a['title']
			url = a['url']
			if BITLY_API:
				s = BITLY_API.shorten(url)
				u = s['url']
				url = unicodedata.normalize('NFKD', u).encode('ascii','ignore')
			

			# Calculate the maximum length for the title of the article.
			# This length is equal to : 
			# 	140 - length of TWEET_TEXT - spaces - length of the URL
			# 	140 is max length for a tweet 
			# If the title is too large to fit in a tweet, it is shorten
			# and some dots are added at its end.
			max_length = 140 - TWEET_FORMAT_LENGTH - 5 - len(url)
			if len(title) >= max_length:
				title = "%s%s"%(title[:max_length-3],"...")

			# Generate the tweet message from TWEET_FORMAT, and remove any extra
			# HTML character.
			tweet_text = TWEET_FORMAT.replace('$$POST_TITLE$$', title)
			tweet_text = tweet_text.replace('$$POST_URL$$', url)
			tweet_text = strip_tags(tweet_text)

			# Post the tweet on Twitter
			twitter_send(tweet_text)
			log_file.write(tweet_text + "\n")
			
		# At the end, publish the ending tweet.
		# If more than one tweet were sent, the last tweet will contains the number
		# of tweets. In this purpose, the TWEET_SUMMARY_END_MANY variable **has** 
		# to contains a '%d' (integer) replacement tag.
		if conf.Summary.tweet_end:
			if len(POSTS) == 1:
				twitter_send(TWEET_END_ONE)
				log_file.write(TWEET_END_ONE + "\n")
			else:	
				twitter_send(TWEET_END_MANY%len(POSTS))
				log_file.write(TWEET_END_MANY%len(POSTS) + "\n")
	else:
		# If no new articles were published, log it.
		log_file.write("No new posts\n")

# END
