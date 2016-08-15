import urlparse
import logging

class PluginMeta(type):
    def __init__(cls, name, bases, namespace):
        super(PluginMeta, cls).__init__(name, bases, namespace)

        is_abstract = name == 'Plugin' or \
          (getattr(cls, 'abstract_plugin', False) is True and Plugin in bases)

        if is_abstract: return

        if not getattr(cls, 'plugin_namespace', None) or not getattr(cls, 'plugin_name', None):
            raise TypeError('plugin %s is incorrectly defined, must have both a '
                            '"plugin_name" and "plugin_namespace" defined' % name)

        Plugin.map.setdefault(cls.plugin_namespace, {})
        Plugin.map[cls.plugin_namespace][cls.plugin_name] = cls

class Plugin(object):
    __metaclass__ = PluginMeta

    map = {}
    abstract_plugin = True

    def __init__(self, uri):
        self.uri = urlparse.urlparse(uri)

    @classmethod
    def get_class(cls, namespace, name):
        return cls.map.get(namespace, {}).get(name, None)

    @classmethod
    def load(cls, namespace, uri, **settings):
        parsed_uri = urlparse.urlparse(uri)
        klass = cls.get_class(namespace, parsed_uri.scheme)
        return klass(uri, **settings)
