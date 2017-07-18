# -*- coding: utf-8 -*-
import time
import sqlite3
import argparse
import random
import os

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

import constants
import json
import  datetime

from dbutils.models import MessageTable
from dbutils.managers import SQLiteDBManager

DB_TABLE = MessageTable(constants.DB_NAME,constants.DB_PATH)
DB_MGR = SQLiteDBManager(DB_TABLE)

DP_MAP = {}

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
        return self.clients[name]

    def del_client(self, name):
        del self.clients[name]

class ChatWebSocketHandler(WebSocket):
    def opened(self):
        cherrypy.engine.publish('add-client', self.username, self)

    def received_message(self, m):
        text = m.data.decode('utf8')

        timestamp = int(time.time())

        dp = DP_MAP.get(self.username)
        if not dp:
            dp = constants.DEFAULT_DP_PATH

        published_msg = {"username":self.username,"message":text,"time":datetime.datetime.fromtimestamp(
           int(timestamp)).strftime(constants.DATE_FORMAT),"display_picture":dp}
        if text.find("@") == -1:
            # echo to all
            cherrypy.engine.publish('websocket-broadcast', json.dumps(published_msg))

            result = DB_MGR.run_query(DB_TABLE.get_insert_query(),[self.username, text, timestamp])
        else:
            # or echo to a single user
            left, message = text.rsplit(':', 1)
            from_username, to_username = left.split('@')
            client = cherrypy.engine.publish('get-client', to_username.strip()).pop()
            published_msg["message"] = to_username+"::"+message
            client.send(json.dumps(published_msg))

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('del-client', self.username)
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

class Root(object):
    def __init__(self, host, port, ssl=False, ssl_port=9443):
        self.host = host
        self.port = port
        self.ssl_port = ssl_port
        self.ssl = ssl
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        with open(constants.TEMPLATE_PATH+constants.INDEX_NAME,'r') as chat_template:
            template = chat_template.read()
        return template

    @cherrypy.expose
    def chatroom(self, username=None,display_picture=None):
        username = username or "User%d" % random.randint(0, 100)
        display_picture = display_picture or constants.DEFAULT_DP_PATH
        messages = []

        DP_MAP[username] = display_picture

        result = DB_MGR.run_query(DB_TABLE.get_limited_get_query(),[])
        for row in result:
            dp = DP_MAP.get(row[0])
            if not dp:
                dp = constants.DEFAULT_DP_PATH
            messages.append({"username":row[0],"message":row[1],"time":datetime.datetime.fromtimestamp(
                int(row[2])).strftime(constants.DATE_FORMAT),"display_picture":dp})

        with open(constants.TEMPLATE_PATH+constants.CHATBOX_NAME,'r') as chat_template:
            template = chat_template.read()
        return template % {'username': username, 'host': self.host,
           'port': self.ssl_port if self.ssl else self.port, 'scheme': self.scheme,
           'messages': json.dumps(messages),"display_picture":display_picture}

    @cherrypy.expose
    def ws(self, username):
        # let's track the username we chose
        cherrypy.request.ws_handler.username = username
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

if __name__ == '__main__':
    import logging
    from ws4py import configure_logger
    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl-port', default=9443, type=int)
    parser.add_argument('--ssl', action='store_true')
    parser.add_argument('--cert', default='./server.crt', type=str)
    parser.add_argument('--key', default='./server.key', type=str)
    parser.add_argument('--chain', default='./server.chain', type=str)
    args = parser.parse_args()

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

    app_root = Root(args.host, args.port, args.ssl, ssl_port=args.ssl_port)
    cherrypy.quickstart(app_root, '', config=config)
