import logging
from logging.config import dictConfig
import os

logging_config = dict(
    version=1,
    formatters={
        'brief': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(message)s',
            'datefmt': '%H:%M:%S'
        },
        'full': {
            'format': '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d  %(message)s',
            'datefmt': '%b %d %H:%M:%S'
        }
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
            'level': logging.DEBUG
        }
    },
    loggers={
        'aiodownload': {
            'handlers': ['console'],
            'level': logging.DEBUG,
            'propagate': False
        },
    },
    root={
        'handlers': ['console'],
        'level': logging.DEBUG,
    }
)

dictConfig(logging_config)

logger = logging.getLogger()

pid = 'N/A' if not hasattr(os, 'getpid') else os.getpid()
logger.info('[PID: {0}] Process spawned...'.format(pid))

del dictConfig, logging_config, pid
