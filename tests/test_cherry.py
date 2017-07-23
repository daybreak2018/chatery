import unittest
import urllib
import cherrypy

import app
from unittest.mock import MagicMock, call

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket
from ws4py.framing import Frame, OPCODE_TEXT, OPCODE_CLOSE

import socket
import time

local = cherrypy.lib.httputil.Host('127.0.0.1', 9000, "")
remote = cherrypy.lib.httputil.Host('127.0.0.1', 9004, "")


def setupServer():
    import logging,os
    from ws4py import configure_logger
    configure_logger(level=logging.DEBUG)

    cherrypy.config.update({
        'server.socket_host': "127.0.0.1",
        'server.socket_port': 9000,
    })
    config = {
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': app.ChatWebSocketHandler,
            'tools.websocket.protocols': ['toto', 'mytest', 'hithere']
        }
    }

    app.ChatPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = app.WebSocketTool()

    app_root = app.Root("127.0.0.1", 9000, None)
    cherrypy.tree.mount(app_root,'/',config)
    cherrypy.engine.start()

def setUpModule():
    cherrypy.config.update({'environment': "test_suite"})

    # prevent the HTTP server from ever starting
    cherrypy.server.unsubscribe()
    setupServer()

setup_module = setUpModule

def tearDownModule():
    cherrypy.engine.exit()
teardown_module = tearDownModule

class BaseCherryPyTestCase(unittest.TestCase):
    def webapp_request(self, path='/', method='GET', **kwargs):
        headers = [('Host', '127.0.0.1')]
        qs = fd = None

        if method in ['POST', 'PUT']:
            qs = urllib.parse.urlencode(kwargs)
            headers.append(('content-type', 'application/x-www-form-urlencoded'))
            headers.append(('content-length', '%d' % len(qs)))
            fd = str(qs)
            qs = None
        elif kwargs:
            qs = urllib.parse.urlencode(kwargs)

        # Get our application and run the request against it
        app = cherrypy.tree.apps['']
        # Let's fake the local and remote addresses
        # Let's also use a non-secure scheme: 'http'
        request, response = app.get_serving(local, remote, 'http', 'HTTP/1.1')
        try:
            response = request.run(method, path, qs, 'HTTP/1.1', headers, fd)
        finally:
            if fd:
                fd.close()
                fd = None

        if response.output_status.startswith(b'500'):
            print(response.body)
            raise AssertionError("Unexpected error")

        # collapse the response into a bytestring
        response.collapse_body()
        return response

class TestCherryPyApp(BaseCherryPyTestCase):
    def test_index(self):
        response = self.webapp_request('/')
        self.assertEqual(response.output_status, b'200 OK')
        # response body is wrapped into a list internally by CherryPy
        self.assertEqual(response.headers["Content-Type"], 'text/html;charset=utf-8')

    def test_login(self):
        response = self.webapp_request('/login')
        self.assertEqual(response.output_status, b'303 See Other')

if __name__ == '__main__':
    unittest.main()