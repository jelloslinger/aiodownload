# -*- coding: utf-8 -*-
"""aiodownload API
"""

from .aiodownload import AioDownload, AioDownloadBundle
# from .api import close, one, swarm
from .strategy import BackOff, Lenient, RequestStrategy


__all__ = (
    'AioDownload',
    'AioDownloadBundle',
    'BackOff',
    'Lenient',
    'RequestStrategy',
    # 'close',
    # 'one',
    # 'swarm'
)
