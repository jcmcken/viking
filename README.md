# viking

**WARNING**: This project is currently in an **ALPHA** state, you should really not
be using it in any production capacity yet.

``viking`` is a clean-room implementation of the ``jcmcken/parallel-ssh`` project.

The goals of ``viking`` are similar in many respects of ``parallel-ssh``, and
include:

* Agentless (in the sense that all you need is ``sshd`` on the remote end)
* Parallel execution
* Many options for managing connection output and status

But ``viking`` improves many things about ``parallel-ssh``, and includes:

* A stable, rich Python API. Integrate ``viking`` with other Python applications
* Usage of ``paramiko`` (native Python SSH implementation) rather than shelling
  out ``ssh`` clients.
* A plugin system. The following components can be extended and dynamically
  loaded:

  - Output processors, e.g. how to transform SSH output before storing it somewhere
  - Output storage backends, e.g. print the output to screen or store it in an RDBMS 
  - Command executors (including distributed executors)
  - User-provided "compound" commands that wrap specific execution and output
    processing into a single, reusable command.
  - Execution strategies, e.g. command retries, back-offs, etc.
  - Host enumeration

## Tutorial

### Local Execution

``viking`` is made up of a bunch of subcommands, but let's start with ``ssh``.

To execute a remote SSH command on a single host, ``somehost``, you can run:

```console
$ viking ssh somehost uptime
```

Say that you need to execute against multiple hosts. Just use the ``--hosts``
option:

```console
$ viking ssh --hosts file:///tmp/hosts uptime
```

The ``--hosts`` option controls what are termed 'host enumerators'. These
enumerators just return a list of hosts to ``viking`` so that it knows
where to SSH. Host enumerators are fully pluggable in ``viking`` (you can
provide your own!), but there are some useful ones already included.

Here's one, the ``script`` enumerator. This enumerator uses the output of
the given script as the list of hosts to execute against:

```console
$ viking ssh --hosts script:///tmp/hosts.sh uptime
```

### Remote Execution

Another useful execution primitive in ``viking`` is the concept of a
command queue. By default, ``viking ssh`` will launch SSH sessions from
your current host to your list of remote hosts, returning the results
locally to you as the commands complete.

Another way to think about this is that ``viking`` is queueing the commands
in memory, and then working off that queue until it is empty. But who says
that the process doing the queueing also has to be the process doing the
executing?

In ``viking``, you can queue SSH commands to a centralized place, and have
multiple remote workers pull tasks off the queue. This provides for nearly
limitless scalability (well, at least as scalable as your centralized queue
is).

In this example, we'll queue the commands to a ``redis`` backend, and then
have multiple workers popping tasks off that queue. 

First, queue up the tasks:

```console
[me@host1 ~]$ viking ssh --queue redis://viking --hosts file:///tmp/hosts.txt uptime
```

When you execute ``viking ssh`` with a non-default queue (the default being
the ``memory://`` queue), this indicates to ``viking`` that you just would
like to queue the tasks but not execute them.

On your worker hosts, consume the ``redis`` tasks:

```console
[me@host2 ~]$ viking ssh --queue redis://viking --storage /var/log/viking-worker.log
[me@host3 ~]$ viking ssh --queue redis://viking --storage /var/log/viking-worker.log
```

When ``viking ssh`` is run with ``--queue``, but has no command provided (``uptime``
in previous examples), ``viking`` assumes that you're starting a worker process.
Additionally, if you supply the ``--storage`` option (which tells ``viking`` where
to store the results), and it's set to anything other than ``terminal://`` (the
default), ``viking`` assumes that you want to daemonize the process.

And again, everything here is pluggable. The ``--queue`` implementation (``redis``
in this example) can be swapped out for arbitrary implementations. Same thing with
``--storage``.

One common pattern is to use a queue for both the tasks and their results. So you
might do something like:

```console
[me@host2 ~]$ viking ssh --queue redis://viking-input --storage redis://viking-output
```

Then you can use some other process for retrieving the results from the centralized
queue and persisting or processing them.


### Execution Strategies

Communicating with remote computers is always fraught with a certain kind of peril,
All sorts of things can go wrong, and often these things are difficult to debug.
This is why it's almost always adviseable to have some sort of strategy for dealing
with network or other failures.

The most common method for dealing with failures is to implement a way to retry
a failed task. Also, usually, it's adviseable to implement some sort of backoff
on retried tasks to avoid "thundering herd" scenarios.

``viking`` provides these retry/backoff facilities by default. And again, like 
other components, you can swap your own strategies into place if these don't fit
the bill.

Let's execute against a single host for simplicity:

```console
$ viking ssh --strategy backoff:sleep=1,scaling=exponential \
>            --strategy retry:forever somehost uptime
```

Let's take a closer look.

First notice that you can pass multiple strategies. Each strategy is executed against
the task in the order it was invoked. In this example, when a task fails, the
following happens:

* The ``backoff`` strategy causes the execution to sleep for ``1`` second.
* The ``retry`` strategy causes the execution to retry the task.

Let's say the task fails again. The following would happen:

* The ``backoff`` strategy would notice that we're invoking a 2nd time. The base
  sleep value is ``1``. Since ``scaling`` is set to ``exponential``, the base
  sleep value is multiplied by ``e^(2-1) = e^1`` to give a sleep value of approx.
  ``2.718``. The execution sleeps for ``2.718`` seconds.
* The ``retry`` strategy attempts to retry the task.

Handling failed tasks is just one use-case for execution strategies. They can
also be used to tell a task when to start in the first place. For example, 
say that you have some condition you want met before execution starts. You can
design a strategy to enforce this condition.
