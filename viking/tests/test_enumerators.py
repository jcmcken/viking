from viking.tests import TestCase, Fixture
from viking.core import Plugin
from viking.enumerators import FileEnumerator, ScriptEnumerator
import tempfile
import os

class TestEnumerators(TestCase):
    def test_clean_file(self):
        enum = FileEnumerator(Fixture.get('enumerators/clean-hosts.txt').uri)

        self.assertEquals(list(enum), ['host1', 'host2', 'host3', 'host4'])

    def test_dirty_file(self):
        enum = FileEnumerator(Fixture.get('enumerators/dirty-hosts.txt').uri)
        
        self.assertEquals(list(enum), 
            ['host1', 'host4', 'host5', 'host6', 'host7'])

    def test_empty_file(self):
        enum = FileEnumerator(Fixture.get('enumerators/empty-hosts.txt').uri)
        
        self.assertEquals(list(enum), [])

    def test_empty_script(self):
        enum = ScriptEnumerator(Fixture.get('enumerators/empty-hosts.sh').uri)
        
        self.assertEquals(list(enum), [])

    def test_failing_script(self):
        enum = ScriptEnumerator(Fixture.get('enumerators/error-hosts.sh').uri)

        self.assertRaises(RuntimeError, lambda: list(enum))

    def test_successful_script(self):
        enum = ScriptEnumerator(Fixture.get('enumerators/clean-hosts.sh').uri)

        self.assertEquals(list(enum), ['host1', 'host3', 'host4', 'host5'])

    def test_null_enumerator(self):
        self.assertEquals(list(Plugin.load('enumerators', 'null://')), [])

    def test_single_enumerator(self):
        self.assertEquals(list(Plugin.load('enumerators', 'single://foo')), ['foo'])

    def test_list_enumerator(self):
        self.assertEquals(list(Plugin.load('enumerators', 'list://foo,bar,baz')),
          ['foo', 'bar', 'baz'])
