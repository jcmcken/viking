from viking.core import Plugin

class Executor(Plugin):
    plugin_namespace = 'executors'
    abstract_plugin = True

    def execute(self):
        """
        Execute some sort of computation against a remote host
        """
        raise NotImplementedError

class Result(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

class ExternalSSHExecutor(Executor):
    plugin_name = 'external-ssh'

    def __init__(self, host, command):
        self.host = host
        self.command = command

    def execute(self):
        full_command = ['ssh', self.host, self.command]
        proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return Result(stdout=stdout, stderr=stderr, returncode=proc.returncode)

# TODO: paramiko-based 'internal-ssh' executor
# TODO: SSH client options, etc.
