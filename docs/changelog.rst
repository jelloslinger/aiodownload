Changelog
=========

v.0.2.4 - 2017-07-04
::::::::::::::::::::

* DownloadStrategy class introduced to break up configuration between the "download" and the "request"
* BoundedSemaphore implemented to control number of concurrent requests, removed PriorityQueue implementation
* AioDownload class reworked to feature two async methods:
    - main (entry point for task creation)
    - request_and_download (coordinates the logic implemented in RequestStrategy and DownloadStrategy)
* UrlBundle changed to AioDownloadBundle, some property changes to object
* added short hand functions one, swarm, and each to the API

v.0.1.1 - 2016-07-04
::::::::::::::::::::

* initial working code release
* Python 3.5
* built on top of aiohttp, no other 3rd party dependencies
* core classes / concepts: AioDownload, UrlBundle, RequestStrategy
* two request strategies:
    - Lenient (try two times with two two seconds between requests)
    - Backoff (exponential backoff up to 1 min.)
* largely undocumented