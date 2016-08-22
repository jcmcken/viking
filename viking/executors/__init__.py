from viking.core import Plugin
from urlparse import urlparse
import subprocess
import logging
import json

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

        self.formatters = {}

        self.register_formatters()

    @property
    def success(self):
        """
        Whether the execution result should be considered a success
        """
        return True

    def format_json(self, task):
        return json.dumps(dict(self))

    def register_formatters(self):
        self.register_formatter('json', self.format_json)

    def register_formatter(self, name, callable):
        self.formatters[name] = callable

    def formatter(self, formatter):
        uri = urlparse(formatter)

        formatter = self.formatters.get(uri.scheme)

        if not formatter:
            raise ResultError('no such formatter "%s"' % formatter)

        return formatter

class SSHResult(Result):
    @property
    def success(self):
        return self.get('returncode') == 0

    def format_pssh(self, task):
        pass

    def register_formatters(self):
        super(SSHResult, self).register_formatters()

        self.register_formatter('pssh', self.format_pssh)

class NullExecutor(Executor):
    plugin_name = 'null'

    def execute(self):
        return Result(host=self.host, command=self.command)

class ExternalSSHExecutor(Executor):
    plugin_name = 'external-ssh'

    def execute(self):
        full_command = ['ssh', self.host, self.command]
        proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return SSHResult(
          stdout=stdout,
          stderr=stderr,
          returncode=proc.returncode,
          host=self.host,
          command=self.command,
        )

# TODO: paramiko-based 'internal-ssh' executor
# TODO: SSH client options, etc.
