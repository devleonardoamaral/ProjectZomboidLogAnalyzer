# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 22/09/2024, 17:00 (UTC/GMT -03:00) 

import os
import sys
import logging
from configparser import ConfigParser
from .globals import get_root_dir

logger = logging.getLogger('app.config')

DEFAULT_CONFIG = """[path]
zomboid=C:/Users/{user}/Zomboid
database={app_path}/database.db
[app]
reading_frequency=1
expiration_time=10
[pattern]
default=^\[(\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\](.+)\.?$
"""

class Config:
    _instance = None

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            logger.info('Starting settings...')
            self._config = ConfigParser()
            self.load_config()
            self._initialized = True
            logger.info('Settings: OK!')

    def load_config(self) -> None:
        app_dir = get_root_dir()
        config_file = os.path.join(app_dir, 'config.ini')

        if not os.path.exists(config_file):
            logger.error('Missing configuration file.')
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(DEFAULT_CONFIG)
                    logger.critical(f'A new configuration file has been generated in the {config_file} folder. Fill it in correctly and start the application again.')
                    sys.exit()
            except PermissionError as e:
                logger.exception(e)
                logger.critical(f'Insufficient permissions to create configuration file.')
                sys.exit()
            except Exception as e:
                logger.exception(e)
                logger.critical(f'Error creating configuration file.')
                sys.exit()

        files_read = self._config.read(config_file)

        if not files_read:
            logger.critical('The configuration file could not be loaded.')
            sys.exit()

        path_zomboid = self._config.get('path', 'zomboid', fallback=None)
        if not path_zomboid:
            logger.critical('The path to the Project Zomboid local files directory could not be loaded from the settings, please check the configured path and try again.')
            sys.exit()
        path_zomboid = path_zomboid.format(user=os.environ.get('USER') or os.environ.get('USERNAME'))
        path_zomboid = os.path.normpath(path_zomboid)
        logger.info(f'Path to the Zomboid folder defined as: {path_zomboid}')
        if not os.path.exists(path_zomboid):
            logger.critical('The path defined in the settings for the local Project Zomboid files could not be found, please check the configured path and try again.')
            sys.exit()

        self.path_zomboid = path_zomboid
        self.path_zomboid_logs = os.path.join(self.path_zomboid, 'Logs')
        logger.info('Path to Project Zomboid local files directory: OK!')

        path_database = self._config.get('path', 'database', fallback=None)
        if not path_database:
            logger.critical('The path to the database could not be loaded from the settings, please check the configured path and try again.')
            sys.exit()
        path_database = path_database.format(app_path=get_root_dir())
        path_database = os.path.normpath(path_database)
        logger.info(f'Path to database defined as: {path_database}')
        if not os.path.exists(os.path.dirname(path_database)):
            logger.critical('The path defined in the settings to the database could not be found, please check the configured path and try again.')
            sys.exit()

        self.path_database = path_database
        logger.info('Path to the database file: OK!')

        self.app_reading_frequency = self._config.getfloat('app', 'reading_frequency', fallback=1)
        self.app_expiration_time = self._config.getint('app', 'expiration_time', fallback=60)

        self.pattern_default = [self._config.get('pattern', 'default', fallback=None)]