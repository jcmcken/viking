from viking.core import Plugin
from viking.tests import TestCase

class TestPluginLoading(TestCase):
    def test_builtins(self):
        self.assertTrue(bool(Plugin.registry))
        self.assertEquals(set(Plugin.registry.keys()),
            set(['queues', 'executors', 'enumerators', 'serializers', 'storage']))
