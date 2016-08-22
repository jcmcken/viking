from viking.core import Plugin
import sys

class Storage(Plugin):
    plugin_namespace = 'storage'
    abstract_plugin = True

    def store(self, result):
        raise NotImplementedError

class NullStorage(Storage):
    plugin_name = 'null'

    def store(self, result):
        return

class TerminalStorage(Storage):
    plugin_name = 'terminal'

    def store(self, result):
        sys.stdout.write(result + '\n')
