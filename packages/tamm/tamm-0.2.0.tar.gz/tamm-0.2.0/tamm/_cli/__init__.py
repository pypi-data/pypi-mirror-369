"""
tamm._cli
---------

This module implements a command-line interface for tamm.

To add new commands, we use the :func:`command` and `argument` decorators.  Here is a
toy example of how we could add a command that prints a string:

.. code-block:: python

    @command("examples", "print")
    @argument("--uppercase", action="store_true")
    @argument("string")
    def print_string(string, uppercase):
        if uppercase:
            string = string.upper()
        print(string)


As long as this code is imported during ``tamm._cli`` import, we can run it as
follows:

::

    > tamm examples print my_string
    my_string
    > tamm examples print "new string" --uppercase
    NEW STRING


For each cli command, we have an argparse subparser and a function to run when the
user invokes the command.  The subparser defines arguments for the command as well as
a ``func`` default argument with the command function as the value.  To run the cli, we
parse the args and then call ``func`` with the arguments.
"""
from tamm._cli import clean, from_tamm, ls, show, to_tamm, version
from tamm._cli.common import argument, command
