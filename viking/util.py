import threading

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
