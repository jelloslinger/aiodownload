:orphan:

.. include:: ../README.rst

Examples
--------

See the *example* package for more basic usages and different ways to configure base objects.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   api
   changelog

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Acknowledgements
----------------

This library leverages |aiohttp_link| to make requests and manage the HTTP session.  *aiodownload* is a lean wrapper
designed to abstract the asynchronous programming paradigm and to cut down on the coding of repetitive request
functions.

.. |aiohttp_link| raw:: html

   <a href="http://aiohttp.readthedocs.io/en/stable/client.html" target="_blank">aiohttp.ClientSession</a>

The public function API for this project was adapted from |simple_requests_link| which utilizes |gevent_link| and
|requests_link|.  The motivation for reimplementation was to use the native event loop introduced in Python 3.  No
monkey patching required.

.. |simple_requests_link| raw:: html

   <a href="http://pythonhosted.org/simple-requests/" target="_blank">simple-requests</a>

.. |gevent_link| raw:: html

   <a href="http://www.gevent.org/" target="_blank">gevent</a>

.. |requests_link| raw:: html

   <a href="http://docs.python-requests.org/en/latest" target="_blank">requests</a>
