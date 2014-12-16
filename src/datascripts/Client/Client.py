__author__ = 'thodoris'

from twisted.internet import reactor, protocol

# a client protocol

class QueryClient(protocol.Protocol):

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print "Server said:", data
        self.postQuery()

    def postQuery(self):
        queryString = raw_input("New Query: ")
        self.transport.write(queryString)


class QueryFactory(protocol.ClientFactory):
    protocol = QueryClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()


# this connects the protocol to a server runing on port 8000
def main():
    f = QueryFactory()
    reactor.connectTCP("localhost", 8000, f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()