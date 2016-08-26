import threading
import urlparse
import logging
import os

LOG = logging.getLogger(__name__)

class Script(object):
    def __init__(self, filename):
        self.filename = filename

    @property
    def runtime(self):
        with open(self.filename, 'rb') as fd:
            line = fd.readline().strip()
    
        if not line.startswith('#!'):
            return None
    
        return line.split('#!', 1)[-1]

    @property
    def full_command(self):
        runtime = self.runtime
        if runtime:
            return [self.runtime, self.filename]
        else:
            return [self.filename]

class StoppableThread(threading.Thread):
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._should_stop = threading.Event()

    @property
    def should_stop(self):
        return self._should_stop.is_set()

    def stop(self):
        self._should_stop.set()
        super(StoppableThread, self).join()

class URI(urlparse.ParseResult):
    @property
    def kwargs(self):
        kwargs = urlparse.parse_qs(self.query, keep_blank_values=True)

        for k,v in kwargs.items():
            value = v[0]
            kwargs[k] = value

            if not value:
                if k.startswith('!'):
                    kwargs[k[1:]] = False
                    del kwargs[k]
                else:
                    kwargs[k] = True

            if self._looks_inty(value):
                kwargs[k] = int(value)

        LOG.debug('converted query string "%s" to kwargs: %s' % (self.query, kwargs))

        return kwargs 

    @property
    def location(self):
        if self.netloc:
            if self.path:
                return os.path.join(self.netloc, self.path)
            else:
                return self.netloc
        else:
            return self.path

    def _looks_inty(self, value):
        try:
            int_value = int(value)
        except ValueError:
            return False
        if str(value) == str(int_value):
            return True
        return False

    @classmethod
    def parse(cls, uri):
        result = urlparse.urlparse(uri)
        if not result.scheme:
            result = urlparse.urlparse(uri.split(':')[0] + '://')
        return cls(*tuple(result))
