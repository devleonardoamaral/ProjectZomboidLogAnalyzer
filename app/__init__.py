import os
import re
import time
import logging
from datetime import datetime, timedelta
from .logger import LoggerManager
from typing import Any, TypedDict

LoggerManager.setup_logger('', True, True, 'console')

logger = logging.getLogger('app')

logger.info('Welcome to Zomboid Log Reader!')
logger.info('Made with ♥ by Leonardo Amaral!')
logger.info('-------------------------------')

from .config import Config

config = Config()

from .database import Database

Database.setup_database()

from .reader import Reader

reader = Reader()