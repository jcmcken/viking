from Queue import Queue
import threading
import uuid
import logging
import time
from viking.executors import Executor
from viking.queues import MemoryQueue
from viking.core import Plugin, PluginLoadError
import datetime

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
        self.result = None
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    @property
    def elapsed(self):
        return self.updated_at - self.created_at

    @property
    def executed(self):
        return self.times_executed > 0

    @property
    def successful(self):
        return self.result and self.result.success

    def execute(self, raise_exception=False):
        self.log.debug('launching task')
        self.updated_at = datetime.datetime.now()
        self.running = True
        self.times_executed += 1
        try:
            self.result = self.executor.execute()
        except Exception as e:
            self.log.exception('encounted unknown exception')
            if raise_exception: raise e
        finally:
            self.updated_at = datetime.datetime.now()
            self.running = False
        if self.successful:
            self.log.debug('successfully completed task after %d execution(s)' % self.times_executed)

    def format(self, formatter):
        return self.result.formatter(formatter).format(self)

class Worker(threading.Thread):
    def __init__(self, work_queue, results_queue):
        super(Worker, self).__init__()

        self.work_queue = work_queue
        self.results_queue = results_queue
        self.daemon = True
        self.id = str(uuid.uuid4())

        # use this logger to log worker-specific information
        self.log = logging.getLogger('%s.worker.%s' % (__name__, self.id))

    def run(self):
        while True:
            try:
                task = self.work_queue.get()
            except Empty:
                time.sleep(0.1)
                continue

            self.log.debug('executing task %s' % task.id)
            try:
                task.execute()
            except Exception as e:
                self.log.exception('exception thrown by worker %s in task %s' % (self.id, task.id))
            finally:
                self.log.debug('done with task, queueing up result')
                self.work_queue.task_done()
                self.results_queue.put(task)

class ThreadPool(object):
    def __init__(self, work_queue=None, results_queue=None, num_threads=5):
        self.work_queue = work_queue or Queue()
        self.results_queue = results_queue or Queue()
        self.queued_tasks = 0
        self.finished_tasks = 0
        self.threads = []
        self.started = False
        for _ in range(num_threads):
            self.threads.append(Worker(self.work_queue, self.results_queue))

    def start(self):
        for thread in self.threads:
            thread.start()
        self.started = True

    def stop(self):
        self.work_queue.join()
        self.started = False

    def add_task(self, task):
        if not isinstance(task, Task):
            raise TypeError('you can only add tasks of type viking.tasking.Task')
        self.queued_tasks += 1
        self.work_queue.put(task)

class StorageWriter(threading.Thread):
    def __init__(self, storage, queue):
        super(StorageWriter, self).__init__()
        self.storage = storage
        self.queue = queue

    def run(self):
        pass

    stop = threading.Thread.join

class TaskManager(object):
    def __init__(self, threads=5, 
      enumerator='null://',
      queue='memory://',
      executor='external-ssh://',
      storage='terminal://'):

        self.work_queue = Plugin.load('queues', queue)
        self.results_queue = Queue()

        self.pool = ThreadPool(
          num_threads=threads,
          work_queue=self.work_queue,
          results_queue=self.results_queue,
        )

        self.executor_cls = Plugin.get_class('executors', executor)

        if not self.executor_cls:
            raise PluginLoadError('could not load executor "%s"' % executor)

        self.enumerator = Plugin.load('enumerators', enumerator)

        self.storage = Plugin.load('storage', storage)

        self.storage_writer = StorageWriter(self.storage, self.results_queue)

    def run(self, command=None):
        local_queue = self.work_queue.plugin_name == 'memory'

        queueing_enabled = command is not None

        execution_enabled = (command is not None and local_queue) or \
            (not local_queue and command is None)

        if execution_enabled:
            # start task results writer
            self.storage_writer.start()
            # start pool workers
            self.pool.start()

        if queueing_enabled:
            for host in self.enumerator:
                task = Task(self.executor_cls(host, command))
                self.pool.add_task(task)

        if execution_enabled:
            self.pool.stop()
            self.storage_writer.stop()
