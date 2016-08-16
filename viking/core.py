import urlparse
import logging

class PluginLoadError(RuntimeError): pass

class PluginMeta(type):
    def __init__(cls, name, bases, namespace):
        super(PluginMeta, cls).__init__(name, bases, namespace)

        is_abstract = name == 'Plugin' or \
          (getattr(cls, 'abstract_plugin', False) is True and Plugin in bases)

        if is_abstract: return

        if not getattr(cls, 'plugin_namespace', None) or not getattr(cls, 'plugin_name', None):
            raise TypeError('plugin %s is incorrectly defined, must have both a '
                            '"plugin_name" and "plugin_namespace" defined' % name)

        Plugin.registry.setdefault(cls.plugin_namespace, {})
        Plugin.registry[cls.plugin_namespace][cls.plugin_name] = cls

class Plugin(object):
    __metaclass__ = PluginMeta

    registry = {}
    abstract_plugin = True

    def __init__(self, uri):
        self.uri = urlparse.urlparse(uri)

    @classmethod
    def get_class(cls, namespace, uri):
        parsed_uri = urlparse.urlparse(uri)
        return cls.registry.get(namespace, {}).get(parsed_uri.scheme, None)

    @classmethod
    def load(cls, namespace, uri, **settings):
        klass = cls.get_class(namespace, uri)
        if not klass:
            raise PluginLoadError(namespace, uri)
        return klass(uri, **settings)
