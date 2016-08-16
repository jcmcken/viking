from viking.core import Plugin
import logging

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

class Result(dict):
    @property
    def success(self):
        """
        Whether the execution result should be considered a success
        """
        return True

    @property
    def description(self):
        """
        A human-readable description of the result. Usually, if the result is 
        successful, it should be okay to return ``None``.
        """
        return None

class SSHResult(Result):
    @property
    def success(self):
        return self.get('returncode') == 0

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
        return SSHResult(stdout=stdout, stderr=stderr, returncode=proc.returncode)

# TODO: paramiko-based 'internal-ssh' executor
# TODO: SSH client options, etc.
