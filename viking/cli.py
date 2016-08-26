import click
from viking import tasking
import logging

@click.group()
@click.option('-d', '--debug', is_flag=True)
def main(debug):
    if debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

@main.command()
@click.argument('command', nargs=-1)
@click.option('--hosts')
@click.option('--queue')
@click.option('--storage')
@click.option('--serializer')
@click.option('--executor')
def ssh(command, hosts, queue, storage, serializer, executor):

    if command and not hosts:
        host, command = command[0], command[1:]
        hosts = 'list://%s' % host

    kwargs = {
      'enumerator': hosts,
      'queue': queue,
      'storage': storage,
      'serializer': serializer,
      'executor': executor,
    }

    for key, val in kwargs.items():
        if not val:
            del kwargs[key]

    manager = tasking.TaskManager(**kwargs)

    if command:
        manager.run(command)

if __name__ == '__main__':
    main.main(prog_name='viking')
