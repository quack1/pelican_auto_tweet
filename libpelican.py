#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''A library that provides usefull functions to interact with Pelican
blog posts.
'''

__author__     = 'quack1'
__version__    = '0.6'
__date__       = '2014-05-27'
__copyright__  = 'Copyright © 2013-2014, Quack1'
__licence__    = 'BSD'
__credits__    = ['Quack1']
__maintainer__ = 'Quack1'
__email__      = 'quack+pelican@quack1.me'
__status__     = 'Development'

import datetime
import os.path
import re

class PelicanBlog:
	'''Represents a Pelican blog.

	This class gives a clean an simple API to interact with a Pelican blog.
	
	After being created with the base directory of the blog, functions allows
	to obtain information about an article.

	The information that's possible to get for an article are : 
	  - author
	  - category
	  - datetime
	  - lang
	  - slug
	  - status
	  - summary
	  - tags
	  - title
	  - url
	
	It is also possible to get information from the whole blog, like : 
	  - A list of all posts
	  - The base URL
	  - The base directory
	  - All the drafts.
	'''


	_blog_directory    = None
	_content_directory = None
	_blog_base_url     = None

	_REGEX_BASE_URL = re.compile(r'SITEURL = \'(.*)\'',re.IGNORECASE)

	def __init__(self, base_directory):
		'''Initiate a new Pelican blog instance.

		Args:
		  base_directory:
		    The directory in which the blog stands.
		    This directory **has to** contain the `content` directory 
		    and the `pelicanconf.py` and `Makefile` files.
		'''
		self._blog_directory = base_directory
		self._content_directory = os.path.join(self._blog_directory, 'content')

	def get_site_base_url(self):
		'''Get the blog base URL from the `pelicanconf.py` file.
		The file must be located in the base directory given in the parameter 
		of the constructor.

		The file which will be read will be {base_directory}/pelicanconf.py.
		'''
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
		'''Get the value of one option field in a post file.
		The file must be located in a `content` directory, located in the base
		directory given in the parameter of the constructor.

		The file which will be read will be `{base_directory}/content/{post_filename}`.

		Args:
		  post_filename:
		    The filename of the article.
		  post_info:
		    The name of the wanted information.
		    The value returned will be get using this regular expression:
		      `{post_info}\s*:\s*(.*)$`
		      If `post_info` is 'Title', the regular expression will match
		      on the following line : "Title: My Very Good Blog Post".
		      The returned value will be "My Very Good Blog Post".
		'''
		regex = re.compile("^%s\s*:\s*(.*)$"%post_info, re.IGNORECASE)

		with open(os.path.join(self._content_directory, post_filename),"r") as f:
			for line in f:
				res = regex.search(line)
				if res:
					return(res.group(1))
			return ""

	def get_base_directory(self):
		'''Get the base directory of a blog instance.

		Returns:
		  The base directory containing a blog instance
		'''
		return self._blog_directory

	def get_post_title(self, post_filename):
		'''Get the title of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The title of the article, or a blank string.
		'''
		return self._get_post_info(post_filename, "Title")

	def get_post_date(self, post_filename):
		'''Get the date of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The date of the article in a **datetime** object.
		  If the date is not defined in the article, None is returned.
		'''
		date = self._get_post_info(post_filename, "Date").strip()
		if date is None or date == "":
			return None
		else:
			return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")

	def get_post_author(self, post_filename):
		'''Get the author of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The author of the article, or a blank string.
		'''
		return self._get_post_info(post_filename, "Author")

	def get_post_category(self, post_filename):
		'''Get the category of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The category of the article, or a blank string.
		'''
		return self._get_post_info(post_filename, "Category")

	def get_post_tags(self, post_filename):
		'''Get the tags of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  A list containing all the tags of the article. If no tags is defined, the
		    list can contain only an empty string.

		TODO: If the string returned by get_post_info is blank, return an empty
		  list.
		'''
		tags = self._get_post_info(post_filename, "Tags").split(',')
		return [x.strip() for x in tags]

	def get_post_slug(self, post_filename):
		'''Get the slug of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The slug of the article, or a blank string.

		TODO: If the slug option is not defined, generate the URL with
		  the Pelican core method.
		'''
		return self._get_post_info(post_filename, "Slug")

	def get_post_summary(self, post_filename):
		'''Get the summary of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The summary of the article, or a blank string.
		'''
		return self._get_post_info(post_filename, "Summary")

	def get_post_lang(self, post_filename):
		'''Get the lang of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The lang of the article, or a blank string.
		'''
		return self._get_post_info(post_filename, "Lang")

	def get_post_status(self, post_filename):
		'''Get the status of a blog post.
		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The status of the article, or a blank string.
		'''
		return self._get_post_info(post_filename, "Status")

	def is_draft(self, post_filename):
		'''Returns the 'draft' status of a blog post.
		If the uppercase status of the blog post is 'DRAFT', it is considered
		as a draft.

		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  True if the blog post is a draft.
		'''
		return self.get_post_status(post_filename).upper() == 'DRAFT'

	def posts_have_drafts(self, posts_filenames):
		'''Look if a list of articles contains drafts.
		Args:
		  posts_filenames:
		    A list containing the filename of the articles.

		Returns:
		  True if at least one article in the list is a draft.
		'''
		for f in posts_filenames:
			if self.get_post_status(f).upper() == 'DRAFT':
				return True
		return False

	def get_post_url(self, post_filename):
		'''Get the complete URL of a blog post.
		The URL is generated by appending the post slug after the site 
		base URL.

		Args:
		  post_filename:
		    The filename of the article.

		Returns:
		  The complete URL to the article.
		'''
		return self.get_site_base_url() + self.get_post_slug(post_filename) + ".html"

	def get_posts(self):
		'''Get the list of all articles of the blog.

		Returns:
		  A list containing all the articles of the blog.
		'''
		l = os.listdir(self._content_directory)
		posts = []
		for post_filename in l:
			base,ext = os.path.splitext(post_filename)
			if ext in ('.rst','.md'):
				posts.append(post_filename)
		return posts
	
	def get_drafts(self):
		'''Get the list of all drafts of the blog.

		To be considered as a draft, the status of the article (get with the
			`get_post_status()` method), uppercase, has to be 'DRAFT'.

		Returns:
		  A list containing all the drafts of the blog.
		'''
		l = os.listdir(self._content_directory)
		posts = []
		for post_filename in l:
			base,ext = os.path.splitext(post_filename)
			if ext in ('.rst','.md'):
				if self.get_post_status(post_filename).upper() == "DRAFT":
					posts.append(post_filename)
		return posts
