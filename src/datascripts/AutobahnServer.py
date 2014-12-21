__author__ = 'thodrek'

from autobahn.twisted.websocket import WebSocketServerProtocol
import json

class ServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
      print("Client connecting: {}".format(request.peer))

    def onMessage(self, payload, isBinary):
        obj = json.loads(payload.decode('utf8'))
        print len(obj)
        payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
        self.sendMessage(payload, isBinary=False)

    def onOpen(self):
      print("WebSocket connection open.")

    def onClose(self, wasClean, code, reason):
      print("WebSocket connection closed: {}".format(reason))

if __name__ == '__main__':
    import sys
    from twisted.python import log
    from twisted.internet import reactor
    log.startLogging(sys.stdout)

    from autobahn.twisted.websocket import WebSocketServerFactory
    factory = WebSocketServerFactory()
    factory.protocol = ServerProtocol

    reactor.listenTCP(9000,factory)
    reactor.run()
