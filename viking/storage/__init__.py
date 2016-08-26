from viking.core import Plugin
import sys

class Storage(Plugin):
    plugin_namespace = 'storage'
    abstract_plugin = True
    default_serializer = None

    def serialize(self, task, serializer=None):
        return task.serialize(serializer=serializer or self.default_serializer)

    def store(self, task, serializer=None):
        raise NotImplementedError

class NullStorage(Storage):
    plugin_name = 'null'

    def store(self, task, serializer=None):
        return

class TerminalStorage(Storage):
    plugin_name = 'terminal'

    def store(self, task, serializer=None):
        serialized = self.serialize(task, serializer)

        if serialized[-1] == '\n':
            serialized = serialized[0:-1]

        sys.stdout.write(serialized + '\n')

class FileStorage(Storage):
    plugin_name = 'file'
    default_serializer = 'json://'

    def store(self, task, serializer=None):
        with open(self.uri.location, 'a') as fd:
            fd.write(self.serialize(task, serializer))
