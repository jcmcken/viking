from viking.core import Plugin
import subprocess
import logging
import json
from viking.util import URI

LOG = logging.getLogger(__name__)

class Executor(Plugin):
    plugin_namespace = 'executors'
    abstract_plugin = True

    def __init__(self, host, command):
        self.host = host
        self.command = command

    def execute(self): # pragma: no cover
        """
        Execute some sort of computation against a remote host
        """
        raise NotImplementedError

class ResultError(RuntimeError): pass
class Result(dict):
    def __init__(self, *args, **kwargs):
        super(Result, self).__init__(*args, **kwargs)

        self.serializers = {}

        self.register_serializers()

    @property
    def success(self):
        """
        Whether the execution result should be considered a success
        """
        return True

    def serialize_json(self, task, indent=None, sort_keys=None):
        return json.dumps(dict(self), indent=indent, sort_keys=sort_keys)

    def register_serializers(self):
        self.register_serializer('json', self.serialize_json)

    def register_serializer(self, name, callable):
        self.serializers[name] = callable

    def serializer(self, serializer):
        uri = URI.parse(serializer)

        serializer = self.serializers.get(uri.scheme)

        if not serializer:
            raise ResultError('no such serializer "%s"' % serializer)

        return lambda task: serializer(task, **uri.kwargs)

class SSHResult(Result):
    @property
    def success(self):
        return self.get('returncode') == 0

    def serialize_pssh(self, task):
        if self.success:
            success_msg = 'SUCCESS'
        else:
            success_msg = 'FAILURE'

        context = {
          'index': task.metadata['index'],
          'timestamp': task.updated_at.strftime('%H:%M:%S'),
          'success': success_msg,
          'host': self['host'],
          'returncode': self['returncode'],
          'stdout': self['stdout'],
          'stderr': self['stderr'],
        }

        result = "[%(index)d] %(timestamp)s [%(success)s] %(host)s"
        
        if not self.success:
            result += " Exited with error code %(returncode)d"

        result += "\n%(stdout)s"

        if self.get('stderr'):
            result += '\nStderr: %(stderr)s'

        return result % context

    def register_serializers(self):
        super(SSHResult, self).register_serializers()

        self.register_serializer('pssh', self.serialize_pssh)

class NullExecutor(Executor):
    plugin_name = 'null'

    def execute(self):
        return Result(host=self.host, command=self.command)

class ExternalSSHExecutor(Executor):
    plugin_name = 'external-ssh'

    def execute(self):
        full_command = ['ssh', '-q', '-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', self.host] + list(self.command)
        LOG.debug("executing subprocess command: %s" % full_command)
        proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        truncated_stdout, truncated_stderr = stdout[:20], stderr[:20]

        if len(stdout) > len(truncated_stdout):
            truncated_stdout += '...'
        if len(stderr) > len(truncated_stderr):
            truncated_stderr += '...'

        LOG.debug('command results: returncode=%d, stdout="%s", stderr="%s"' % \
          (proc.returncode, truncated_stdout, truncated_stderr))

        return SSHResult(
          stdout=stdout,
          stderr=stderr,
          returncode=proc.returncode,
          host=self.host,
          command=self.command,
        )

# TODO: paramiko-based 'internal-ssh' executor
# TODO: SSH client options, etc.
