"""
URI Handlers
------------

|tamm| includes built-in URI handlers to facilitate checkpoint downloading with disk caching.
To support custom storage backends, plugin may extend URI handlers using the following process:

Register a custom URI Handler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a submodule named ``<plugin>.utils.uri`` and add your URI handler to this submodule.
For example, to implement ``Boto3URIHandler``, create a ``boto3.py``  under ``<my_tamm_plugin>/utils/uri``
with the following content:

.. code-block:: python

    from tamm.utils.uri._protocol import BaseURLHandler
    from pathlib import Path

    class Boto3URIHandler(BaseURLHandler):
        name = "boto3"

        def _map_to_local(self, uri: str, local_path: Path) -> Path:
            # Implement downloading w/ boto3. Return the downloaded (or cached) local path
            return local_path

.. admonition:: Tip

    submodule naming must be exactly ``<plugin>.utils.uri`` for the plugin system to recognize URI handlers

Register your URI handler by exporting ``available_handlers`` from ``<plugin>/utils/uri/__init__.py``.
``available_handlers`` should be a list of ``BaseURLHandler``, specifically, ``List[Type["BaseURLHandler"]]``

.. code-block:: python

    from my_tamm_plugin.utils.uri.boto3 import Boto3URIHandler

    available_handlers = [Boto3URIHandler]
    __all__ = [
        "Boto3URIHandler",
        "available_handlers",
    ]

.. admonition:: Tip

    Import statement ``from my_tamm_plugin.utils.uri import available_handlers`` **must** work for
    |tamm| plugin system to discover your custom URI handler.

URI Handler Base Classes
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: tamm.utils.uri.BaseURLHandler
.. autoclass:: tamm.utils.uri.AtomicDownloadURIHandler

"""

from tamm.utils.uri._protocol import AtomicDownloadURIHandler, BaseURLHandler
from tamm.utils.uri.uri_handler import _is_json_file, _is_uri, _URIHandler

__all__ = [
    "_URIHandler",
    "_is_uri",
    "_is_json_file",
    "BaseURLHandler",
    "AtomicDownloadURIHandler",
]
