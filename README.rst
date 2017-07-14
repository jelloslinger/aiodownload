===========
aiodownload
===========

.. rst-class:: header

+------------------------------------------------+----------------------------+
| |tagline|                                      |                            |
+------------------------------------------------+ |logo|                     |
| |badge1| |badge2| |badge3| |badge4|            |                            |
+------------------------------------------------+----------------------------+

.. |tagline| replace:: Asynchronous Requests and Downloads Without Thinking About It

.. |logo| image:: _static/tree-roots.svg

.. |badge1| image:: https://img.shields.io/pypi/l/aiodownload.svg
    :target: https://pypi.python.org/pypi/aiodownload

.. |badge2| image:: https://img.shields.io/pypi/wheel/aiodownload.svg
    :target: https://pypi.python.org/pypi/aiodownload

.. |badge3| image:: https://img.shields.io/travis/jelloslinger/aiodownload.svg
    :target: https://pypi.python.org/pypi/aiodownload

.. |badge4| image:: https://codecov.io/github/jelloslinger/aiodownload/coverage.svg?branch=master
    :target: https://codecov.io/github/jelloslinger/aiodownload
    :alt: codecov.io

----

Basic Usage
-----------

.. code-block:: shell-session

    >>> import aiodownload
    >>> urls = ['https://httpbin.org/links/{}'.format(i) for i in range(0, 5)]
    >>> bundles = aiodownload.swarm(urls)
    >>>
    >>> import pprint
    >>> pprint.pprint(dict((b.url, b.file_path, ) for b in bundles))
    {'https://httpbin.org/links/0': 'C:\\\\httpbin.org\\links\\0',
     'https://httpbin.org/links/1': 'C:\\\\httpbin.org\\links\\1',
     'https://httpbin.org/links/2': 'C:\\\\httpbin.org\\links\\2',
     'https://httpbin.org/links/3': 'C:\\\\httpbin.org\\links\\3',
     'https://httpbin.org/links/4': 'C:\\\\httpbin.org\\links\\4'}

Default Request Strategy (Lenient)
    - two concurrent requests with 0.25 s delay between requests
    - automatically retry unsuccessful requests up to 4 more times with 60 s between attempts
    - response statuses greater than 400 are considered unsuccessful requests
    - 404s are not retried (if they tell us it's not found, let's believe them)

Default Download Strategy
    - read and write 65536 byte chunks at a time
    - uses the current working directory as home path to write files
    - relative path and filename are a transformation of the url path segments (the last segment being the filename)

Customizable Strategies
    - Want *aiodownload* to behave differently? Configure the underlying classes to create your own strategies.

Installation
------------

.. code-block:: shell-session

    $ pip install aiodownload
