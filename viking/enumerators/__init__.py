from viking.core import Plugin
from viking.util import Script
import subprocess

class Enumerator(Plugin):
    def __iter__(self): # pragma: no cover
        raise NotImplementedError 

def get_hosts(line):
    line = line.strip()

    if not line or line.startswith('#'):
        raise StopIteration

    for item in line.split():
        yield item

class FileEnumerator(Enumerator):
    def __iter__(self):
        with open(self.uri.path, 'rb') as fd:
            for line in fd:
                for host in get_hosts(line):
                    yield host

class ScriptEnumerator(Enumerator):
    def __iter__(self):
        script = Script(self.uri.path)
        proc = subprocess.Popen(
            script.full_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError('script did not return successfully')

        for line in stdout.splitlines():
            for host in get_hosts(line):
                yield host
