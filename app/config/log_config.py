import sys
import logging.config


class _ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.WARNING


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'exclude_errors': {
            '()': _ExcludeErrorsFilter
        }
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(asctime)s: %(filename)s: %(lineno)d:\t %(funcName)s(): %(message)s'
        },
    },
    'handlers': {
        'console_stderr': {
            # Sends log messages with log level ERROR or higher to stderr
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'simple',
            'stream': sys.stderr
        },
        'console_stdout': {
            # Sends log messages with log level lower than ERROR to stdout
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filters': ['exclude_errors'],
            'stream': sys.stdout
        },
    },
    'loggers': {
        'asyncio': {
            'level': 'ERROR'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console_stderr', 'console_stdout'],
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING)
