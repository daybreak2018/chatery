__author__ = 'shaur'

import os

#DB Details

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"database/")
DB_NAME = "DB"

#Template Path
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"assets/")
INDEX_NAME = "index.html"
CHATBOX_NAME = "chatbox.html"


#Settings
DATE_FORMAT = "%B %d,%Y at %I:%M %p"
DEFAULT_DP_PATH = "images/dp.jpg";