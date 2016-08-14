import urlparse

class Plugin(object):
    def __init__(self, uri):
        self.uri = urlparse.urlparse(uri)
