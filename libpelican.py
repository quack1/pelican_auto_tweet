#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This library provides usefull functions to interact with Pelican
blog posts.
'''

__author__     = 'quack1'
__version__    = '0.1'
__date__       = '2014-05-04'
__copyright__  = 'Copyright © 2014, Quack1'
__licence__    = 'BSD'
__credits__    = ['Quack1']
__maintainer__ = 'Quack1'
__email__      = 'quack+pelican@quack1.me'
__status__     = 'Development'

import datetime
import os.path
import re

class PelicanBlog:

	_blog_directory    = ""
	_content_directory = ""
	_blog_base_url     = ""

	_REGEX_BASE_URL = re.compile(r'SITEURL = \'(.*)\'',re.IGNORECASE)

	def __init__(self, base_directory):
		self._blog_directory = base_directory
		self._content_directory = os.path.join(self._blog_directory, 'content')

	def get_site_base_url(self):
		'''Get the site base url from the pelicanconf.py file.
		The file must be located in the base directory given in the parameter 
		of the constructor.'''
		if self._blog_base_url:
			return self._blog_base_url
		else:
			with open(os.path.join(self._blog_directory,"pelicanconf.py")) as f:
				for l in f:
					res = self._REGEX_BASE_URL.search(l)
					if res:
						self._blog_base_url = res.group(1)
						if not self._blog_base_url.endswith('/'):
							self._blog_base_url += '/'
						return self._blog_base_url


	def _get_post_info(self, post_filename, post_info):
		'''Get the value of one option field in a post file.'''
		regex = re.compile("^%s\s*:\s*(.*)$"%post_info, re.IGNORECASE)

		#with open(os.path.join(self._content_directory, post_filename),"r") as f:
		with open(post_filename),"r") as f:
			for line in f:
				res = regex.search(line)
				if res:
					return(res.group(1))
			return ""

	def get_base_directory(self):
		return self._blog_directory

	def get_post_title(self, post_filename):
		'''Get the title of one blog post.'''
		return self._get_post_info(post_filename, "Title")

	def get_post_date(self, post_filename):
		'''Get the date of one blog post.'''
		date = self._get_post_info(post_filename, "Date").strip()
		return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")

	def get_post_author(self, post_filename):
		'''Get the author of one blog post.'''
		return self._get_post_info(post_filename, "Author")

	def get_post_category(self, post_filename):
		'''Get the category of one blog post.'''
		return self._get_post_info(post_filename, "Category")

	def get_post_tags(self, post_filename):
		'''Get the list of tags of one blog post.'''
		tags = self._get_post_info(post_filename, "Tags").split(',')
		return [x.strip() for x in tags]

	def get_post_slug(self, post_filename):
		'''Get the slug of one blog post.'''
		# TODO: If the slug is not defined, generate the slug from the Title of
		# the post.
		return self._get_post_info(post_filename, "Slug")

	def get_post_summary(self, post_filename):
		'''Get the summary of one blog post.'''
		return self._get_post_info(post_filename, "Summary")

	def get_post_lang(self, post_filename):
		'''Get the lang of one blog post.'''
		return self._get_post_info(post_filename, "Lang")

	def get_post_status(self, post_filename):
		'''Get the status of one blog post.'''
		return self._get_post_info(post_filename, "Status")

	def posts_have_drafts(self, posts_filenames):
		'''Return true if (at least) one of the posts in posts_filenames
		is a draft.'''
		for f in posts_filenames:
			if self.get_post_status(f).upper() == 'DRAFT':
				return True
		return False

	def get_post_url(self, post_filename):
		return self.get_site_base_url() + self.get_post_slug(post_filename) + ".html"

	def get_posts(self):
		l = os.listdir(self._content_directory)
		posts = []
		for post_filename in l:
			base,ext = os.path.splitext(filename)
			if ext in ('.rst','.md'):
				posts.append(post_filename)
		return posts
	
	def get_drafts(self):
		l = os.listdir(self._content_directory)
		posts = []
		for post_filename in l:
			base,ext = os.path.splitext(post_filename)
			if ext in ('.rst','.md'):
				filename = os.path.join(self._content_directory, post_filename)
				if self.get_post_status(filename).upper() == "DRAFT":
					posts.append(post_filename)
		return posts
