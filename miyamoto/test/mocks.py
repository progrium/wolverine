from twisted.web import server, resource

class MockSubscriber(resource.Resource):
    isLeaf = True
    
    def render_GET(self, request):
        if request.path.endswith('/callback'):
            return request.args.get('hub.challenge', [''])[0]
        else:
            return "Huh?"
        

class MockPublisher(resource.Resource):
    isLeaf = True
    
    def render(self, request):
        host = '%s:%s' % (request.host.host, request.host.port)
        if request.path.endswith('/happycats.xml'):
            request.setHeader('content-type', 'application/atom+xml')
            return """<?xml version="1.0"?>
<feed>
  <!-- Normally here would be source, title, etc ... -->

  <link rel="hub" href="http://%s/" />
  <link rel="self" href="http://%s%s" />
  <updated>2008-08-11T02:15:01Z</updated>

  <!-- Example of a full entry. -->
  <entry>
    <title>Heathcliff</title>
    <link href="http://publisher.example.com/happycat25.xml" />
    <id>http://publisher.example.com/happycat25.xml</id>
    <updated>2008-08-11T02:15:01Z</updated>
    <content>
      What a happy cat. Full content goes here.
    </content>
  </entry>

  <!-- Example of an entity that isn't full/is truncated. This is implied
       by the lack of a <content> element and a <summary> element instead. -->
  <entry >
    <title>Heathcliff</title>
    <link href="http://publisher.example.com/happycat25.xml" />
    <id>http://publisher.example.com/happycat25.xml</id>
    <updated>2008-08-11T02:15:01Z</updated>
    <summary>
      What a happy cat!
    </summary>
  </entry>

  <!-- Meta-data only; implied by the lack of <content> and
       <summary> elements. -->
  <entry>
    <title>Garfield</title>
    <link rel="alternate" href="http://publisher.example.com/happycat24.xml" />
    <id>http://publisher.example.com/happycat25.xml</id>
    <updated>2008-08-11T02:15:01Z</updated>
  </entry>

  <!-- Context entry that's meta-data only and not new. Implied because the
       update time on this entry is before the //atom:feed/updated time. -->
  <entry>
    <title>Nermal</title>
    <link rel="alternate" href="http://publisher.example.com/happycat23s.xml" />
    <id>http://publisher.example.com/happycat25.xml</id>
    <updated>2008-07-10T12:28:13Z</updated>
  </entry>

</feed>""" % (host, host, request.path)
        else:
            return 'Huh?'