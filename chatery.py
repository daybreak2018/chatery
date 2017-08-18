# -*- coding: utf-8 -*-
import time
import pytz
import argparse
import random
import os
import tweepy

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

import constants
import json
import utils

from dbutils.models import MessageTable
from dbutils.managers import SQLiteDBManager

DB_TABLE = MessageTable(constants.DB_NAME,constants.DB_PATH)
DB_MGR = SQLiteDBManager(DB_TABLE)

DP_MAP = {}
TWITTER_ACCESS_TOKEN_MAP = {}

TIMEZONE = "GMT"

class ChatPlugin(WebSocketPlugin):
    def __init__(self, bus):
        WebSocketPlugin.__init__(self, bus)
        self.clients = {}

    def start(self):
        WebSocketPlugin.start(self)
        self.bus.subscribe('add-client', self.add_client)
        self.bus.subscribe('get-client', self.get_client)
        self.bus.subscribe('del-client', self.del_client)

    def stop(self):
        WebSocketPlugin.stop(self)
        self.bus.unsubscribe('add-client', self.add_client)
        self.bus.unsubscribe('get-client', self.get_client)
        self.bus.unsubscribe('del-client', self.del_client)

    def add_client(self, name, websocket):
        self.clients[name] = websocket

    def get_client(self, name):
        if name in self.clients:
            return self.clients[name]

    def del_client(self, name):
        if name in self.clients:
            del self.clients[name]


class ChatWebSocketHandler(WebSocket):
    def opened(self):
        cherrypy.engine.publish('add-client', self.username, self)

    def received_message(self, m):
        text = m.data.decode('utf8')
        tweet_id = 0;
        status=""
        timezone = pytz.timezone(TIMEZONE)

        isoTime = utils.to_iso8601(timezone)

        curr_time = utils.from_iso8601(timezone, isoTime)

        dp = DP_MAP.get(self.username)
        if not dp:
            dp = constants.DEFAULT_DP_PATH

        published_msg = {"username":self.username,"message":text,"time":curr_time.strftime(constants.DATE_FORMAT),"display_picture":dp}
        if text.find("@") == -1:
            try:
                # echo to all
                if(text.find("tweet:")!=-1 or text.find("RT:")!=-1):
                    credentials = TWITTER_ACCESS_TOKEN_MAP.get(self.username)
                    if(credentials):
                        if(text.find("RT:")!=-1):
                            status = utils.tweet(credentials,text,True)
                            if status:
                                published_msg["message"] = text = status.text
                        else:
                            status = utils.tweet(credentials,text,False)

                        if status:
                            published_msg["tweet_id"] = tweet_id = str(status.id)
                        else:
                            status = "Stop"
                    else:
                        published_msg["message"] = published_msg["message"].replace("tweet:","").replace("RT:","")

                if status!="Stop":
                    cherrypy.engine.publish('websocket-broadcast', json.dumps(published_msg))
                    result = DB_MGR.run_query(DB_TABLE.get_insert_query(),[self.username, text, isoTime,tweet_id])
            except Exception as  e:
                cherrypy.log(e)
        else:
            # or echo to a single user
            left, message = text.rsplit(':', 1)
            from_username, to_username = left.split('@')
            client = cherrypy.engine.publish('get-client', to_username.strip()).pop()
            published_msg["message"] = to_username+"::"+message
            if not client:
                client = cherrypy.engine.publish('get-client', self.username).pop()
                published_msg["message"] = "Sorry, I am no longer in this chatroom"
                published_msg["username"] = to_username
                published_msg["display_picture"] = DP_MAP.get(to_username) or constants.DEFAULT_DP_PATH
            client.send(json.dumps(published_msg))

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('del-client', self.username)
        #cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))


class Root(object):
    def __init__(self, host, port, ssl=False, ssl_port=9443):
        self.host = host
        self.port = port
        self.ssl_port = ssl_port
        self.ssl = ssl
        self.scheme = 'wss' if ssl else 'ws'
        self.twitter_request_token = ""

    @cherrypy.expose
    def index(self):
        auth = tweepy.OAuthHandler(consumer_key=constants.CONSUMER_KEY, consumer_secret=constants.CONSUMER_SECRET,
                 callback=constants.CALLBACK_URL)

        auth.secure = True

        #auth.set_access_token(constants.ACCESS_TOKEN,constants.ACCESS_SECRET)

        try:
            redirect_url = auth.get_authorization_url()
            self.twitter_request_token = auth.request_token
        except tweepy.TweepError as e:
            cherrypy.log(e.reason)
            redirect_url = ""

        with open(constants.TEMPLATE_PATH+constants.INDEX_NAME,'r') as chat_template:
            template = chat_template.read()
        return template % {"tweet_login":redirect_url}

    @cherrypy.expose
    def login(self,username=None,display_picture=None,oauth_verifier=None,oauth_token=None):
        cookie = cherrypy.response.cookie

        cookie['username'] = username or ""
        cookie['username']['max-age'] = constants.COOKIE_MAX_AGE
        cookie['username']['path'] = '/'

        if(username):
            display_picture = display_picture or constants.DEFAULT_DP_PATH
            DP_MAP[username] = display_picture

        cookie['oauth_verifier'] = oauth_verifier or ""
        cookie['oauth_verifier']['max-age'] = constants.COOKIE_MAX_AGE
        cookie['oauth_verifier']['path'] = '/'

        cookie['oauth_token'] = oauth_token or ""
        cookie['oauth_token']['max-age'] = constants.COOKIE_MAX_AGE
        cookie['oauth_token']['path'] = '/'
        raise cherrypy.HTTPRedirect("/chatroom")


    @cherrypy.expose
    def archive(self,start=None):
        timezone = pytz.timezone(TIMEZONE)
        for row in DB_MGR.run_query(DB_TABLE.get_count(),[]):
            count = row[0]
        if not start or int(start)>=count:
            start = count-100 if count-100>0 else 0
			
        if int(start)<0:
            start=0
            
        
        messages = []

        result = DB_MGR.run_query(DB_TABLE.get_limited_start(),[int(start)])
        for row in result:
            dp = DP_MAP.get(row[0])
            if not dp:
                dp = constants.DEFAULT_DP_PATH
            if row[3]:
                tweet_id = str(row[3])
            else:
                tweet_id = ""

            curr_time = utils.from_iso8601(timezone, row[2])

            messages.append({"username":row[0],"message":row[1],"time":curr_time.strftime(constants.DATE_FORMAT),"display_picture":dp,"tweet_id":tweet_id})

        with open(constants.TEMPLATE_PATH+constants.ARCHIVE_NAME,'r') as chat_template:
            template = chat_template.read()
        return template % {'username': "none",'port': self.ssl_port if self.ssl else self.port, 'scheme': self.scheme,
           'messages': json.dumps(messages),"start":start}

    @cherrypy.expose
    def chatroom(self):
        cookie = cherrypy.request.cookie

        username = cookie.get("username").value if cookie.get("username") else ""
        display_picture = cookie.get("display_picture").value if cookie.get("display_picture") else ""
        oauth_verifier = cookie.get("oauth_verifier").value if cookie.get("oauth_verifier") else ""
        oauth_token = cookie.get("oauth_token").value if cookie.get("oauth_token") else ""

        if not (username or oauth_verifier):
            raise cherrypy.HTTPRedirect("/")

        username = username or "User%d" % random.randint(0, 100)

        messages = []

        #Twitter's keyword not allowed in normal login.
        if "Twitter's" in username:
            username = "".join(username.split("Twitter's"))

        if(oauth_verifier):
            try:
                token = self.twitter_request_token
                self.twitter_request_token = ""
                auth = tweepy.OAuthHandler(consumer_key=constants.CONSUMER_KEY, consumer_secret=constants.CONSUMER_SECRET)
                token['verifier'] = oauth_verifier
                auth.request_token = token
                auth.get_access_token(oauth_verifier)

                api = tweepy.API(auth)
                me = api.me()
                username = "Twitter's "+me.screen_name

                TWITTER_ACCESS_TOKEN_MAP[username] = utils.generate_twitter_access_object(auth.access_token,auth.access_token_secret)

                display_picture = me.profile_image_url_https
                DP_MAP[username] = display_picture

            except tweepy.TweepError as e:
                cherrypy.log(e.reason)


        timezone = pytz.timezone(TIMEZONE)

        result = DB_MGR.run_query(DB_TABLE.get_limited_get_query(),[])
        for row in result:
            dp = DP_MAP.get(row[0])
            if not dp:
                dp = constants.DEFAULT_DP_PATH
            if row[3]:
                tweet_id = str(row[3])
            else:
                tweet_id = ""

            curr_time = utils.from_iso8601(timezone, row[2])

            messages.append({"username":row[0],"message":row[1],"time":curr_time.strftime(constants.DATE_FORMAT),"display_picture":dp,"tweet_id":tweet_id})

        with open(constants.TEMPLATE_PATH+constants.CHATBOX_NAME,'r') as chat_template:
            template = chat_template.read()
        return template % {'username': username,'port': self.ssl_port if self.ssl else self.port, 'scheme': self.scheme,
           'messages': json.dumps(messages),"display_picture":display_picture}

    @cherrypy.expose
    def ws(self, username):
        # let's track the username we chose
        cherrypy.request.ws_handler.username = username
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))



def main():
    import logging
    from ws4py import configure_logger
    global TIMEZONE
    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl-port', default=9443, type=int)
    parser.add_argument('--ssl', action='store_true')
    parser.add_argument('--cert', default='./server.crt', type=str)
    parser.add_argument('--key', default='./server.key', type=str)
    parser.add_argument('--chain', default='./server.chain', type=str)
    parser.add_argument('--tz', default='GMT', type=str)

    args = parser.parse_args()

    TIMEZONE = args.tz

    cherrypy.config.update({
        'server.socket_host': args.host,
        'server.socket_port': args.port,
        'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets')),
    })
    config = {
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': ChatWebSocketHandler,
            'tools.websocket.protocols': ['toto', 'mytest', 'hithere']
        },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
        },
        '/styles': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'stylesheets'
        },
        '/images': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'images'
        },
    }

    if args.ssl:
        ssl_server = cherrypy._cpserver.Server()
        ssl_server.socket_host = args.host
        ssl_server.ssl_certificate = args.cert
        ssl_server.ssl_private_key = args.key
        ssl_server.socket_port = args.ssl_port
        ssl_server.ssl_certificate_chain = args.chain
        ssl_server.subscribe()

    ChatPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    app_root = Root(args.host, args.port,args.ssl, ssl_port=args.ssl_port)
    cherrypy.quickstart(app_root, '', config=config)


if __name__ == "__main__":
    main()
