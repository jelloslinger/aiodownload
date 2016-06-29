# -*- coding: utf-8 -*-
"""aiodownload API
"""

from .aiodownload import AioDownload, UrlBundle
from .strategy import BackOff, Lenient, RequestStrategy


__all__ = (
    'AioDownload',
    'BackOff',
    'Lenient',
    'RequestStrategy',
    'UrlBundle'
)