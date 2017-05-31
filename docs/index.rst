===========
aiodownload
===========
Asynchronous Downloads Made Easy
--------------------------------

.. image:: https://img.shields.io/pypi/l/aiodownload.svg
    :target: https://pypi.python.org/pypi/aiodownload

.. image:: https://img.shields.io/pypi/wheel/aiodownload.svg
    :target: https://pypi.python.org/pypi/aiodownload

-------------------

Basic Usage
:::::::::::

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

Out of the box, batteries included, you get two concurrent requests.  Any request returning a status greater than 400
(except 404) is tried every minute up to 5 times.  This is the default request strategy.  Your average web server is
expected to go down from time to time so let's give it a few minutes to recover.

The default download strategy is to take the content returned from the request and write it to a file relative to the
current working directory.  The relative path and filename are a transformation of the url path segments (the last
path segment being the filename).

Installation
::::::::::::

.. code-block:: shell-session

    $ pip install aiodownload
