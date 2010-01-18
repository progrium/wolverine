from twisted.web import client, error, http
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet import defer, reactor

import urllib
import time

from miyamoto import queue
#from miyamoto import stream

# TODO: Make these configurable
RETRIES = 3
DELAY_MULTIPLIER = 5

subscriptions = dict() # Key: topic, Value: list of subscriber callback URLs

@defer.inlineCallbacks
def post_and_retry(url, data, retry=0, content_type='application/x-www-form-urlencoded'):
    if type(data) is dict:
        print "Posting [%s] to %s with %s" % (retry, url, data)
        data = urllib.urlencode(data)
    else:
        print "Posting [%s] to %s with %s bytes of postdata" % (retry, url, len(data))
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(len(data)),
    }
    try:    
        page = yield client.getPage(url, method='POST' if len(data) else 'GET', headers=headers, postdata=data if len(data) else None)
    except error.Error, e:
        if e.status in ['301', '302', '303']:
            return # Not really a fail
        print e
        if retry < RETRIES:
            retry += 1
            reactor.callLater(retry * DELAY_MULTIPLIER, post_and_retry, url, data, retry, content_type)
    

@defer.inlineCallbacks
def publish(url):
    subscribers = subscriptions.get(url, None)
    if len(subscribers):
        print "Fetching %s for %s subscribers" % (url, len(subscribers))
        try:
            page = yield client.getPage(url, headers={'X-Hub-Subscribers': len(subscribers)})
            for subscriber in subscribers:
                post_and_retry(subscriber, page, content_type='application/atom+xml')
        except error.Error, e:
            print e


@defer.inlineCallbacks
def subscribe(to_verify):
    print "Verifying %s as a subscriber to %s" % (to_verify['callback'], to_verify['topic'])
    challenge = baseN(abs(hash(time.time())), 36)
    verify_token = to_verify.get('verify_token', None)
    payload = {'hub.mode': to_verify['mode'], 'hub.topic': to_verify['topic'], 'hub.challenge': challenge}
    if verify_token:
        payload['hub.verify_token'] = verify_token
    url = '?'.join([to_verify['callback'], urllib.urlencode(payload)])
    try:
        page = yield client.getPage(url)
        if challenge in page:
            if to_verify['mode'] == 'subscribe':
                if not to_verify['topic'] in subscriptions:
                    subscriptions[to_verify['topic']] = []
                subscriptions[to_verify['topic']].append(to_verify['callback'])
            else:
                subscriptions[to_verify['topic']].remove(to_verify['callback'])
            defer.returnValue(page)
        else:
            raise Exception("Verification challenge failed")
    except Exception:
        raise Exception("Verification failed")
    


def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyz"): 
    return ((num == 0) and  "0" ) or (baseN(num // b, b).lstrip("0") + numerals[num % b])

class SubscribeResource(Resource):
    isLeaf = True
    
    def render_POST(self, request):
        mode        = request.args.get('hub.mode', [None])[0]
        callback    = request.args.get('hub.callback', [None])[0]
        topic       = request.args.get('hub.topic', [None])[0]
        verify      = request.args.get('hub.verify', [None])
        verify_token = request.args.get('hub.verify_token', [None])[0]
        
        if not mode or not callback or not topic or not verify:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Expected 'hub.mode', 'hub.callback', 'hub.topic', and 'hub.verify'"
        
        if not mode in ['subscribe', 'unsubscribe']:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Unrecognized mode"
        
        verify = verify[0] # For now, only using the first preference of verify mode
        if not verify in ['sync', 'async']:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Unsupported verification mode"
            
        to_verify = {'mode': mode, 'callback': callback, 'topic': topic, 'verify_token': verify_token}
        if verify == 'sync':
            def finish_success(request):
                request.setResponseCode(http.NO_CONTENT)
                request.write("204 Subscription created")
                request.finish()
            def finish_failed(request):
                request.setResponseCode(http.CONFLICT)
                request.write("409 Subscription verification failed")
                request.finish()
            subscribe(to_verify).addCallbacks(lambda x: finish_success(request), lambda x: finish_failed(request))
            return NOT_DONE_YET
            
        elif verify == 'async':
            subscribe(to_verify)
            request.setResponseCode(http.ACCEPTED)
            return "202 Scheduled for verification"


class PublishResource(Resource):
    isLeaf = True
    
    def render_POST(self, request):
        mode = request.args.get('hub.mode', [None])[0]
        url = request.args.get('hub.url', [None])[0]
        
        if not mode or not url:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Expected 'hub.mode' and 'hub.url'"
        
        if mode == 'publish':
            publish(url)
            request.setResponseCode(http.NO_CONTENT)
            return "204 Published"
        else:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Unrecognized mode"
