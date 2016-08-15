from viking.tests import TestCase, Fixture
from viking.util import Script

class TestUtils(TestCase):
    def test_script_no_runtime(self):
        script = Script(Fixture.get('util/script-noruntime.sh').path)
        self.assertEquals(script.runtime, None)
        self.assertEquals(len(script.full_command), 1)

    def test_script_runtime(self):
        script = Script(Fixture.get('util/script-runtime.sh').path)
        self.assertEquals(script.runtime, '/bin/sh')
        self.assertEquals(len(script.full_command), 2)
        self.assertEquals(script.full_command[0], '/bin/sh')
