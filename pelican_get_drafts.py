#! /usr/bin/env python
# -*- coding: utf-8 -*- 

'''This script prints the drafts present on a Pelican blog.
If no argument is passed, the current directory ('.') is used.
'''

__author__     = 'quack1'
__version__    = '0.5'
__date__       = '2014-05-21'
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
if len(sys.argv) >= 2:
	base_dir = sys.argv[1]
else:
	base_dir = './'

BLOG = libpelican.PelicanBlog(base_dir)

drafts = BLOG.get_drafts()
for article in drafts:
	print "File '%s' ([%s] %s)"%(article, BLOG.get_post_date(article), BLOG.get_post_title(article))