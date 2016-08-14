from viking.tests import TestCase, Fixture
from viking.enumerators import FileEnumerator
import tempfile
import os

class TestEnumerators(TestCase):
    def setUp(self):
        super(TestEnumerators, self).setUp()

        self.fdno, self.filename = tempfile.mkstemp()

    def test_clean_file(self):
        enum = FileEnumerator(Fixture.get('enumerators/clean-hosts.txt').uri)

        self.assertEquals(list(enum), ['host1', 'host2', 'host3', 'host4'])

    def test_dirty_file(self):
        enum = FileEnumerator(Fixture.get('enumerators/dirty-hosts.txt').uri)
        
        self.assertEquals(list(enum), 
            ['host1', 'host4', 'host5', 'host6', 'host7'])

