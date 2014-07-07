#! /usr/bin/env python
# -*- coding: utf-8 -*- 

'''This script prints the articles present on a Pelican blog ordered by post date asc.
If no argument is passed, the current directory ('.') is used.
'''

__author__     = 'quack1'
__version__    = '0.9'
__date__       = '2014-07-07'
__copyright__  = 'Copyright © 2013-2014, Quack1'
__licence__    = 'BSD'
__credits__    = ['Quack1']
__maintainer__ = 'Quack1'
__email__      = 'quack@quack1.me'
__status__     = 'Development'

import libpelican
import sys
import os.path
import datetime

# Check arguments
# If one argument is passed, it will be considered as the base blog directory.
# If it's not present, the current working directory will be used.
if len(sys.argv) >= 2:
	base_dir = sys.argv[1]
else:
	base_dir = './'

# A new blog instance is created on this directory.
BLOG = libpelican.PelicanBlog(base_dir)

# Get the drafts from the blog instance and print them.
posts = BLOG.get_posts()
posts = sorted(posts, key=lambda x: BLOG.get_post_date(x))
for article in posts:
	print "File '%s' ([%s] %s)"%(article, BLOG.get_post_date(article), BLOG.get_post_title(article))

# END
