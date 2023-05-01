#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'James D. Triveri'
SITENAME = 'The Pleasure of Finding Things Out'
SITEURL = 'http://jtrive.com'
TIMEZONE = 'America/Chicago'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_LANG = 'en'
PATH  = 'content'

ARTICLE_PATHS   = [
    "articles/Statistical_Modeling", "articles/Machine_Learning", "articles/Python",
    "articles/R", 
    ]

OUTPUT_PATH = 'output/'

PAGE_PATHS   = ["pages"]

STATIC_PATHS = ["images", "extras"]

DEFAULT_PAGINATION = 25
SUMMARY_MAX_LENGTH = 50

RELATIVE_URLS = True
USE_FOLDER_AS_CATEGORY = True
DISPLAY_PAGES_ON_MENU = True

# Feed generation is usually not desired when developing.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
DELETE_OUTPUT_DIRECTORY = False
OUTPUT_SOURCES = True
TYPOGRIFY = True
CACHE_CONTENT = False


# Blogroll
LINKS = (
    ('Python.org', 'http://python.org/'),
    ("The Python Module Index", "https://docs.python.org/3/py-modindex.html"),
    ("Scikit-Learn", "https://scikit-learn.org/stable/documentation.html"),
    ("Scipy Docs", "https://www.scipy.org/docs.html"),
    ("OpenAI", "https://openai.com/")
    )


# Plugins ----------------------------------------------------------------------
PLUGIN_PATHS=['./pelican-plugins']
PLUGINS = ['render_math', 'i18n_subsites']


# Theme Related ----------------------------------------------------------------
THEME = "G:\\Repos\\TPOFTO\\pelican-themes\\pelican-bootstrap3"

BOOTSTRAP_FLUID = True
BOOTSTRAP_NAVBAR_INVERSE = True
DISPLAY_ARTICLE_INFO_ON_INDEX = False
DISPLAY_TAGS_ON_SIDEBAR = False
HIDE_SIDEBAR = False
SIDEBAR_ON_LEFT = False

ABOUT_ME = "Data Scientist interested in ML/DL, automation and scientific computing."

AVATAR = "images/JDTGOOG.JPG"

BANNER = "images/probdists0.png"


# BOOTSTRAP_THEME = "Darkly"
# BOOTSTRAP_THEME = "Flatly"
# BOOTSTRAP_THEME = "Simplex"
# BOOTSTRAP_THEME = "Slate"
# BOOTSTRAP_THEME = "Lumen"
# BOOTSTRAP_THEME = "Journal"
# BOOTSTRAP_THEME = "Spacelab"
# BOOTSTRAP_THEME = "Superhero"
# BOOTSTRAP_THEME = "Cyborg"
# BOOTSTRAP_THEME = "Cerulean"
# BOOTSTRAP_THEME = "Cosmo"
# BOOTSTRAP_THEME = "Sandstone"
# BOOTSTRAP_THEME = "United"
BOOTSTRAP_THEME = "Yeti"

# Bad Themes.
# BOOTSTRAP_THEME = "Minty"
# BOOTSTRAP_THEME = "Litera"
# BOOTSTRAP_THEME = "Materia"
# BOOTSTRAP_THEME = "Pulse"
# BOOTSTRAP_THEME = "Sketchy"
# BOOTSTRAP_THEME = "Solar"


SIDEBAR_IMAGES = [
    "images/Sidebar/sidebarA.jpg", "images/Sidebar/sidebarB.png", 
    "images/Sidebar/sidebarC.jpg", "images/Sidebar/sidebarD.jpg"
    ]

JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}

# The value is the location where you tell Pelican to put the file (see below):
CUSTOM_CSS = "static/css/custom.css"

EXTRA_PATH_METADATA = {
    'extras/custom.css': {'path': 'static/css/custom.css'},
    }

PYGMENTS_STYLE = "default"
# autumn
# borland
# bw
# colorful
# darcula
# default
# emacs
# friendly
# fruity
# manni
# monokai
# murphy
# native
# pastie
# perldoc
# solarizeddark
# solarizedlight
# tango
# trac
# vim
# vs
# zenburn
