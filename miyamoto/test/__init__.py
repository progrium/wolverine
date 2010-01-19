from twisted.trial import unittest
from twisted.internet import reactor, threads, defer
from twisted.web import server, resource
from twisted.protocols.policies import WrappingFactory

from urllib2 import urlopen, Request

from miyamoto.web import MiyamotoResource

class SiteTestCase(unittest.TestCase):
    def setUp(self):
        self.cleanupServerConnections = 0
        self.site = server.Site(MiyamotoResource.setup(), timeout=None)
        self.wrapper = WrappingFactory(self.site)
        self.port = reactor.listenTCP(0, self.wrapper, interface="127.0.0.1")
        self.portno = self.port.getHost().port
        
    def tearDown(self):
        # If the test indicated it might leave some server-side connections
        # around, clean them up.
        connections = self.wrapper.protocols.keys()
        # If there are fewer server-side connections than requested,
        # that's okay.  Some might have noticed that the client closed
        # the connection and cleaned up after themselves.
        for n in range(min(len(connections), self.cleanupServerConnections)):
            proto = connections.pop()
            print "Closing %r" % (proto,)
            proto.transport.loseConnection()
        if connections:
            print "Some left-over connections; this test is probably buggy."
        return self.port.stopListening()
        
    def getURL(self, path='/'):
        return "http://127.0.0.1:%d%s" % (self.portno, path)
    
    def doRequest(self, *args, **kw_args):
        if isinstance(args[0], Request):
            r = args[0]
        else:
            if not args[0].startswith('http://'):
                args = list(args)
                args[0] = self.getURL(args[0])
            r = Request(*args, **kw_args)
        return threads.deferToThread(urlopen, r)