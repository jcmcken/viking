import unittest
import shutil
import os

class TestCase(unittest.TestCase):
    def setUp(self):
        self._generated_files = set()

    def deferred_rm(self, filename):
        self._generated_files.add(filename)

    def tearDown(self):
        for f in self._generated_files:
            if not os.path.exists(f): continue

            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)

class Fixture(object):
    path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def __init__(self, path):
        self.path = path

    @property
    def uri(self):
        return 'file://' + self.path

    @classmethod
    def get(cls, identifier):
        path = os.path.join(cls.path, identifier)
        with open(path):
            pass
        return Fixture(os.path.abspath(path))
