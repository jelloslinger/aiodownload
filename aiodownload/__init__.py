"""aiodownload API
"""

from .aiodownload import AioDownload, AioDownloadBundle
from .api import one, each, swarm
from .strategy import BackOff, DownloadStrategy, Lenient, RequestStrategy


__all__ = (
    'AioDownload',
    'AioDownloadBundle',
    'BackOff',
    'DownloadStrategy',
    'Lenient',
    'RequestStrategy',
    'one',
    'each',
    'swarm'
)
