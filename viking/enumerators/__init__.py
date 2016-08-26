from viking.core import Plugin
from viking.util import Script
import subprocess
import logging

LOG = logging.getLogger(__name__)

class Enumerator(Plugin):
    plugin_namespace = 'enumerators'
    abstract_plugin = True

    def __iter__(self): # pragma: no cover
        raise NotImplementedError 

def get_hosts(line):
    line = line.strip()

    if not line or line.startswith('#'):
        raise StopIteration

    for item in line.split():
        yield item

class NullEnumerator(Enumerator):
    plugin_name = 'null'

    def __iter__(self):
        return
        yield

class SingleEnumerator(Enumerator):
    plugin_name = 'single'

    def __iter__(self):
        yield self.uri.location

class ListEnumerator(Enumerator):
    plugin_name = 'list'

    def __iter__(self):
        for host in self.uri.location.split(','):
            yield host.strip()

class FileEnumerator(Enumerator):
    plugin_name = 'file'

    def __iter__(self):
        with open(self.uri.location, 'rb') as fd:
            for line in fd:
                for host in get_hosts(line):
                    yield host

class ScriptEnumerator(Enumerator):
    plugin_name = 'script'

    def __iter__(self):
        script = Script(self.uri.location)
        proc = subprocess.Popen(
            script.full_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError('script did not return successfully')

        for line in stdout.splitlines():
            for host in get_hosts(line):
                yield host
