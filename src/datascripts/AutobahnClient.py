__author__ = 'thodrek'

import json
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory
import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import cgi

class MyClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print "Connected to server"

    def onMessage(self, payload, isBinary):
        if isBinary:
            return "Binary message received"
        else:
            return "Text message received: "+ str(payload.decode('utf8'))

    def sendMessage(self,s):
        obj = {'a':s,'b':2}
        payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
        self.sendMessage(payload, isBinary=False)


class FormPage(Resource):

        def __init__(self, wsFactory):
            self._wsFactory = wsFactory

        def render_GET(self, request):
            return '<html><body><form method="POST"><input name="the-field" type="text" /></form></body></html>'

        def render_POST(self, request):
            input = cgi.escape(request.args["the-field"][0])
            s = self._wsFactory.protocol.sendMessage(input)
            return '<html><body>You submitted: %s</body></html>' % (s,)

if __name__ == '__main__':

    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory()
    factory.protocol = MyClientProtocol

    root = Resource()
    root.putChild("form", FormPage(factory))
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()