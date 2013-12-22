#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# Script Config
BASE_DIR         = ''
SUMMARY_DAYS     = 10
SUMMARY_INTERVAL = 180

# Twitter conf
TWEET_FORMAT_AUTO      = '$$POST_TITLE$$ $$POST_URL$$ #blog'
TWEET_FORMAT_SUMMARY   = '#blogReplay $$POST_TITLE$$ $$POST_URL$$ #blog'
TWEET_SUMMARY_BEGIN    = '#blogReplay Voici les articles publiés ces 7 derniers jours sur $$BLOG_URL$$'
TWEET_SUMMARY_END_ONE  = '#blogReplay C\'était le seul article publié cette semaine. Fin du spam! :)'
TWEET_SUMMARY_END_MANY = '#blogReplay C\'était les %d articles publiés cette semaine. Fin du spam! :)'
IS_TWEET_SUMMARY_BEGIN = True
IS_TWEET_SUMMARY_END   = False

# Twitter API
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

# Bitly API
BITLY_USER = ""
BITLY_API_KEY = ""
