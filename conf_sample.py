#!/usr/bin/env python
# -*- coding: utf-8 -*- #

'''This file is part of the pelican_auto_tweet project. 
It provides configuration variables used into the different scrips of the project.
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

import os.path

class Global:
	blog_directory = '<Pelican_Blog_Home_Directory>'


class Auto:
	tweet_format = '$$POST_TITLE$$ $$POST_URL$$ #blog'

class Summary:
	days     = 10
	interval = 180

	# Twitter conf
	tweet_format          = '#blogReplay $$POST_TITLE$$ $$POST_URL$$ #blog'
	tweet_format_begin    = '#blogReplay Voici les articles publiés ces 7 derniers jours sur $$BLOG_URL$$'
	tweet_format_end_one  = '#blogReplay C\'était le seul article publié cette semaine. Fin du spam! :)'
	tweet_format_end_many = '#blogReplay C\'était les %d articles publiés cette semaine. Fin du spam! :)'
	tweet_begin           = True
	tweet_end             = False


class Links:
	twitter_username = ""
	page_header      = """Title: Liens partagés sur Twitter
	Date: %s
	Author: Quack1"""
	out_file = os.path.join(Global.blog_directory, "content/pages/links.md")


class Twitter:
	consumer_key        = ''
	consumer_secret     = ''
	access_token        = ''
	access_token_secret = ''


class Bitly:
	user    = ""
	api_key = ""
