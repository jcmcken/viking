from viking.core import Plugin

class Storage(Plugin):
    plugin_namespace = 'storage'
    abstract_plugin = True

    def store(self, task):
        raise NotImplementedError

class TerminalStorage(Storage):
    plugin_name = 'terminal'
