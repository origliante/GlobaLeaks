from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File


class FormPage(Resource):
    #isLeaf = True
    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        return file('./jskeycheck.html').read()

    def render_POST(self, request):
        response = '<p>File: %s</p>' % request.args['file1'][0]
        response += '<p>Content: %s</p>' % request.content.read()
        return '<html><body>You submitted: %s</body></html>' % (response)

root = FormPage()
root.putChild("static", File("./static"))

factory = Site(root)
reactor.listenTCP(8080, factory)
reactor.run()


