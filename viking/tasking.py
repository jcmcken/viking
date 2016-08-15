import subprocess
import logging
import cPickle as pickle
from viking.executors import Executor
import uuid

class Task(object):
    def __init__(self, executor):
        if not isinstance(executor, Executor):
            raise TypeError('tasks must be initialized with an object of type '
                            'viking.executors.Executor.')
        self.executor = executor
        self.id = str(uuid.uuid4())
        self.running = False
        self.times_executed = 0
        self.log = logging.getLogger('%s.task.%s' % (__name__, self.id))

    @property
    def executed(self):
        return self.times_executed > 0

    @property
    def successful(self):
        raise NotImplementedError

    def launch(self, raise_exception=False):
        self.running = True
        self.times_executed += 1
        try:
            self.result = self.executor.execute()
        except Exception as e:
            self.log.exception('encounted unknown exception')
            if raise_exception: raise e
        finally:
            self.running = False
