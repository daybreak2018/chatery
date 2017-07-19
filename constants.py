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

#Twitter Settings
CONSUMER_KEY = "Sb2J920e9N1EOz6s9vgVV8LvY"
CONSUMER_SECRET = "dYFImQSBvSQwHN6kYEn24rFlHnZwUxR0FE1pzqHdv4Yp1IHpno"
CALLBACK_URL = "http://127.0.0.1:9000/chatroom"

ACCESS_TOKEN = "15326646-K0fsVwgHsZDrKCQSyAjWpZcIhnxttAOiRQRoow1uP"
ACCESS_SECRET = "tpNQ0ZJAH4RsTflf7JlwEJu4K2mJhNOYyKqaxfg7cqBPs"