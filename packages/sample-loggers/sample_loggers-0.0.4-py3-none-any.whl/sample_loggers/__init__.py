import logging

from yacs.config import CfgNode

from .logger import create_logger
from .utils import summery_model, throughput
from .version import __version__ as __version__


LEVEL = CfgNode()
LEVEL.DEBUG = logging.DEBUG
LEVEL.INFO = logging.INFO
LEVEL.WARNING = logging.WARNING
LEVEL.WARN = logging.WARN
LEVEL.ERROR = logging.ERROR
LEVEL.CRITICAL = logging.CRITICAL

logger = create_logger(
    logger_name="logger",
    log_level=LEVEL.DEBUG,
)


__all__ = [
    '__version__',
    'create_logger',
    'logger',
    'summery_model',
    'throughput',
    'LEVEL',
]