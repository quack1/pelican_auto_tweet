# Pelican-Twitter Bridge

This set of Python scripts are aimed at allowing users of the [Pelican](http://getpelican.com) blog engine to link some of their posts to Twitter.

## Presentation

For now, I only wrote two scripts:

- `pelican_auto_tweet.py`
- `pelican_tweet_summary.py`

The first one is usefull to automatically post a tweet on Twitter for the latest blog post. As Pelican is text-based and often used with Git, this script makes use of Git logs to find new posts. More details are given below.

The second script posts a tweet on Twitter for each article posted on the blog in the last 7 days. Like the previous script, I give some details below.

## Installation

Just fork this repo! :)

Since I use two external libraries, you also need to install them if you want to use these scripts.

### Python-Twitter

Located at [http://code.google.com/p/python-twitter/](http://code.google.com/p/python-twitter/), the steps for installing it are : 

```bash
hg clone http://python-twitter.googlecode.com/hg/ python-twitter
cd python-twitter
hg update
python setup.py build
python setup.py install
```

### Bitly 

To shorten links, I use Bitly. This API is available in [Pip repository](http://www.pip-installer.org/en/latest/installing.html "How to install Pip"), so installation is quite easy.

```bash
pip install bitly_api
```

The results of requests made to Bitly API are Unicode encoded, so I also need a library to re-encode them. This library is [Unidecode](https://pypi.python.org/pypi/Unidecode). _If you have a better way to work with Bitly, I will appreciate if you can tell me about!_

```Python
git clone http://www.tablix.org/~avian/git/unidecode.git unidecode
python setup.py build
python setup.py install
```

## Usage

The script need some configuration. For this, use the file `conf.py`.

```bash
/
|- conf.py
|- pelican_auto_tweet.py
|- pelican_tweet_summary.py
|- README.md
```

In this script, you **have** to define four variables for the [Twitter API](https://dev.twitter.com): 

```Python
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
```

And two variables for the [Bitly API](https://bitly.com/). _For now, Bitly is required in `pelican_auto_tweet.py`, but I plan to make it optional. It's already optional for `pelican_tweet_summary.py`_

```Python
BITLY_USER = ''
BITLY_API_KEY = ''
```

You can also define in a variable the base directory of you Pelican blog. This option is optional.

```Python
BASE_DIR = '~/pelican_blog/'
```

Now, you can use the scripts.

### Pelican_auto_tweet

I use this script to tweet the link of my **last** blog post. 

#### TL;DR; 

This script do 4 things :

1. It checks if a new article was writen (by looking if the [Git [FR]](http://blog.quack1.me/tag/git.html "Blog Quack1 - Tag « Git »") _commit_ log starts with `[POST]`).
2. In this case, it pushes the new _commits_ on the [default git repository [FR]](http://blog.quack1.me/git_push_multiple_remote.md "Git : Pusher ses modifications sur plusieurs dépôts en une seule commande").
3. It updates the blog on the serveur through SSH (command `make ssh_upload` for the _Pelican-ists_).
4. It posts a tweet.

#### Long explanation

I use Git to backup my blog. After each new blog post, I commit the new file with a commit message that starts with `[POST]`. I adapted the script to my own needs, so it get the last commit message, and if the message starts with `[POST]`, it tweets it. 

Before posting a tweet, the script pushes the new commits to the default Git repository, and updates the blog using Pelican Makefile.

The script gets the title and the URL of the lasts posts directly from the source file. If there are many files involved in the commit, every file that is located in `content/` and has a `.md` or `.rst` extension will be considered as one of the lasts posts for which a tweet will be send.

**Tweet text**

The tweet message is constructed based on a format given by the user.

This configuration is set in `conf.py`, with the variable `TWEET_FORMAT_AUTO`. It's simply a string that contains variables, that will be replaced by real values during execution of the script. 

Available variables are : 

- `$$POST_TITLE$$` : Will be replaced by the title of the article.
- `$$POST_URL$$` : Will be replaced by the URL of the article.

If the variable `TWEET_FORMAT_AUTO` is not defined, the default one will be used : 

```Python
TWEET_FORMAT_AUTO = '$$POST_TITLE$$ $$POST_URL$$ #blog'
```

The post title and URL come from the post source file. `$$POST_TITLE$$` is the title of the post (post variable `Title:`). To construct the URL, the script extract the URL of the site in the `pelicanconf.py` file (variable `SITEURL=`), and append to it the slug of the blog post (variable `Slug:` in the header of the blog post file).


#### Execution

To launch the script, you have some options.

1. Run it directly from the root of your Pelican directory:
	```
	$ python ~/pelican_auto_tweet.py
	```
2. Run it from anywhere, and give it the path to the root of your Pelican directory:
	```
	$ python ~/pelican_auto_tweet.py ~/pelican_blog/
	```	



### Pelican_tweet_summary

This script sends one tweet for each blog post published in the last few days.

I use the same method I used for the previous script to get the URL of the posts, or their title.


#### Number of days for which posts should be considered as new

By default, the value is 7 days.

This value can be modified in `conf.py` (here, 14 days):

```Python
SUMMARY_DAYS = 14
```


#### Time between two Twitter updates

By default, each tweet is sent 3 minutes (180seconds) after the previous one.

It's possible to use a different interval using a variable in the configuration file `conf.py` (here, 60 seconds): 

```Python
SUMMARY_INTERVAL = 60
```


#### Tweet text

3 types of tweets are sent : 

1. `TWEET_SUMMARY_BEGIN` : A message to inform that the « blog replay » is starting.
2. `TWEET_FORMAT_SUMMARY` : A message for each post.
3. `TWEET_SUMMARY_END_ONE` and `TWEET_SUMMARY_END_MANY` : A message to inform that the « blog replay » is finished.

The first tweet can (or not) contains one variable : the name/url of the website. For this, use `$$BLOG_URL$$`. A second variable is mandatory. Place `%d` anywhere you want, and this variable will be replaced by the number of days for which we check for new posts. Exemple : `Here are the articles posts in the last %d days on $$BLOG_URL$$` will become `Here are the articles posts in the last 7 days on http://blog.quack1.me`.
If you don't want to use send a first tweet, just set the `IS_TWEET_SUMMARY_BEGIN` variable to `False` in the configuration file :

```Python
IS_TWEET_SUMMARY_BEGIN = False
```

The second tweet can contains variables like for `pelican_auto_tweet.py` (see above).

There are two cases for the last tweet : 

1. Only one new post was posted. The `TWEET_SUMMARY_END_ONE` is sent (no variable allowed).
2. Many posts were posted. The `TWEET_SUMMARY_END_MANY` is sent. One variable is mandatory. Add `%d` in your text. This will be replaced by the numbered of new posts. Exemple : `There were %d articles` will become `There were 24 articles`.

As for the first tweet, you can define the last tweet not to be sent. Set the `IS_TWEET_SUMMARY_END` variable to `False` in the configuration file :

```Python
IS_TWEET_SUMMARY_END = False
```

&nbsp;

All these 4 variables can be ommited, and will be replaced by default values : 

```Python
TWEET_FORMAT_SUMMARY   = '#blogReplay $$POST_TITLE$$ $$POST_URL$$ #blog'
IS_TWEET_SUMMARY_BEGIN = True
TWEET_SUMMARY_BEGIN    = '#blogReplay Voici les articles publiés ces 7 derniers jours sur $$BLOG_URL$$'
TWEET_SUMMARY_END      = True
TWEET_SUMMARY_END_ONE  = '#blogReplay C'était le seul article publié cette semaine. Fin du spam! :)'
TWEET_SUMMARY_END_MANY = '#blogReplay C'était les %d articles publiés cette semaine. Fin du spam! :)'
```

#### Execution

The usage of this script is quite the same as the previous one

1. Run it directly from the root of your Pelican directory:
	```
	$ python ~/pelican_tweet_summary.py
	```
2. Run it from anywhere, and give it the path to the root of your Pelican directory:
	```
	$ python ~/pelican_tweet_summary.py ~/pelican_blog/
	```

## More

I wrote some posts on my blog about this script : 

- [Presentation](http://blog.quack1.me/pelican_auto_tweet-en.html) ;
- [How to automate the publication with Git hooks](http://blog.quack1.me/git_hooks_pelican-en.html).

I also created the theme I use on my blog, which is available [on Github](https://github.com/quack1/notebook).
