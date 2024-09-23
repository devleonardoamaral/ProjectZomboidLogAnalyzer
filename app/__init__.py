import logging
from .logger import LoggerManager

LoggerManager.setup_logger('', True, True, 'console') # Configura o logger padrão

logger = logging.getLogger('app')

logger.info('Seja bem-vindo ao Project Zomboid Log Analyzer!')
logger.info('Feito com ♥ por Leonardo Amaral!')
logger.info('-------------------------------------------------')

from .config import Config
Config() # Inicializa o singleton e carrega as configurações antes dos outros módulos

from .database import Database
Database().setup_database() # Carrega a database a partir do script SQL "app/database.sql"

from .reader import Reader
reader = Reader() # Instância o Reader no escopo global do app