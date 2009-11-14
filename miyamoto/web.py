import os
from twisted.python.util import sibpath
from twisted.web import client, error, http, static
from twisted.web.resource import Resource
from twisted.internet import task

from miyamoto import pubsub, stream
from hookah import dispatch

class MiyamotoResource(Resource):
    isLeaf = False
    
    def getChild(self, name, request):
        if name == '':
            return self
        elif name == 'hub':
            mode = request.args.get('hub.mode', [None])[0]
            if mode in ['subscribe', 'unsubscribe']:
                print "HELLO"
                return pubsub.SubscribeResource()
            elif mode == 'publish':
                return pubsub.PublishResource()
        return Resource.getChild(self, name, request)

    def render(self, request):
        path = '/'.join(request.prepath)
        
        if path in ['favicon.ico', 'robots.txt']:
            return

        return self.index()

    def index(self):
        
        def subscriberRow(url, topic):
            return '''
              <div>
                <a href="%(url)s">%(url)s</a>
                <form method="post" action="subscribe">
                  <input type="hidden" name="hub.callback" value="%(url)s"/>
                  <input type="hidden" name="hub.topic" value="%(topic)s"/>
                  <input type="hidden" name="hub.mode" value="unsubscribe"/>
                  <input type="hidden" name="hub.verify" value="sync"/>
                  <input type="submit" value="Unsub"/>
                  <div class="submitResult"> </div>
                </form>
              </div>''' % vars()

        subscriptionList = "\n".join(
            '''<dt>Topic: <span class="topic">%s</span></dt>
               <dd>%s</dd>
               ''' % (
                topic, '\n'.join(subscriberRow(s, topic) for s in subscribers))
            for topic, subscribers in
            sorted(pubsub.subscriptions.items()))

        return open(os.path.join(os.path.dirname(__file__),
                                 "template/index.html")).read() % vars()

    
    @classmethod
    def setup(cls):
        r = cls()
        r.putChild('dispatch', dispatch.DispatchResource())
        r.putChild('subscribe', pubsub.SubscribeResource())
        r.putChild('publish', pubsub.PublishResource())
        r.putChild('stream', stream.StreamResource())
        r.putChild('style.css', static.File(sibpath(__file__, 'static/styles.css')))
        return r
