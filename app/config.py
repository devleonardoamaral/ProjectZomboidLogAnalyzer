# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 23/09/2024

import os
import sys
import logging
from configparser import ConfigParser
from .globals import get_root_dir

logger = logging.getLogger('app.config')

class EmptyConfigurationError(ValueError):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)

class Config:
    _instance = None
    ROOT_DIR = get_root_dir()

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            logger.info('Carregando configurações...')

            self._config = ConfigParser()
            self.setup_default_values()
            self.load_config()
            self.process_configs()

            self._initialized = True
            logger.info('Configurações: OK!')

    def load_config(self) -> None:
        config_file = os.path.join(self.ROOT_DIR, 'config.ini')

        if not os.path.exists(config_file):
            logger.error(f'O arquivo de configuração "{config_file}" não foi encontrado.')

            try:
                with open(config_file, 'w', encoding='utf-8') as f1:
                    with open(os.path.join(self.ROOT_DIR, 'app', 'config'), 'rb') as f2:
                        content = f2.read().decode(encoding='utf-8')
                        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
                        f1.write(normalized_content)
                    logger.critical(f'Um novo arquivo de configuração foi gerado no diretório "{self.ROOT_DIR}". Preencha-o corretamente e inicie a aplicação novamente.')
                    sys.exit()
                
            except PermissionError as error:
                logger.exception(error)
                logger.critical(f'Permissões insuficientes para criar o arquivo de configuração. Verifique as permisões e tente novamente.')
                sys.exit()
            except Exception as error:
                logger.exception(error)
                logger.critical(f'Erro ao criar arquivo de configuração.')
                sys.exit()

        files_read = self._config.read(config_file)

        if not files_read:
            logger.critical(f'O arquivo de configuração "{config_file}" não pôde ser carregado. Verifique o as permissões e tente novamente.')
            sys.exit()

    def setup_default_values(self) -> None:
        self.default_reading_frequency = 10
        self.default_expiration_time = 0
        self.default_pattern = {}
    
    def process_configs(self) -> None:
        try:
            path_zomboid = self._config.get('path', 'zomboid', fallback=None)
            path_database = self._config.get('path', 'database', fallback=None)
            app_reading_frequency = self._config.get('app', 'reading_frequency', fallback=None)
            app_expiration_time = self._config.get('app', 'expiration_time', fallback=None)
            default_pattern = self._config.get('default', 'pattern', fallback=None)

            patterns = {}
            if 'patterns' in self._config.sections():
                for option_name, value in self._config.items('patterns'):
                    option_name_split = option_name.split('__')

                    if option_name_split[0] in patterns:
                        patterns[option_name_split[0]][option_name_split[1]] = value
                    else:
                        patterns[option_name_split[0]] = {option_name_split[1]: value}
                    
                    logger.debug(f'Pattern carregado: log: {option_name_split[0]} name: {option_name_split[1]}: {value}')

            self.patterns = patterns

            if path_zomboid is None:
                raise EmptyConfigurationError('O caminho para o diretório do Project Zomboid não pôde ser carregado. Verifique o arquivo de configuração e tente novamente.')
            if path_database is None:
                raise EmptyConfigurationError('O caminho para o caminho para o arquivo do banco de dados SQL não pôde ser carregado. Verifique o arquivo de configuração e tente novamente.')
            if app_reading_frequency is None:
                logger.warning(f'A frequência de leitura não foi configurada corretamente. Utilizando um valor padrão {self.default_reading_frequency}.')
                app_reading_frequency = self.default_reading_frequency
            if app_expiration_time is None:
                logger.warning(f'O tempo de expiração dos logs no banco de dados não foi configurado corretamente. Os logs não serão removidos automaticamente.')
                app_expiration_time = self.default_expiration_time
            if default_pattern is None:
                raise EmptyConfigurationError(f'O pattern default não foi configurado corretamente.')

            path_zomboid = os.path.normpath(path_zomboid.format(user=os.environ.get('USER') or os.environ.get('USERNAME')))
            if not os.path.exists(path_zomboid):
                raise FileNotFoundError('Caminho para o diretório do Project Zomboid não encontrado.')
            
            path_zomboid_logs = os.path.join(path_zomboid, 'Logs')
            logger.info(f'Diretório para a pasta "Logs" do Project Zomboid definida como: "{path_zomboid_logs}"')
            if not os.path.exists(path_zomboid_logs):
                raise FileNotFoundError('Caminho para a pasta "Logs" do Project Zomboid não encontrado.')
            
            path_database = path_database.format(app_path=get_root_dir())
            path_database = os.path.normpath(path_database)
            logger.info(f'Caminho para o arquivo da base de dados definido como: "{path_database}"')
            if not os.path.exists(os.path.dirname(path_database)):
                raise FileNotFoundError('Caminho para o arquivo da base de dados não encontrado.')

            try:
                self.app_reading_frequency = float(app_reading_frequency)
                self.app_expiration_time = int(app_expiration_time)
            except ValueError as error:
                raise error(f'Tipo inválido na configuração: {error}')
            
            self.path_zomboid = path_zomboid
            self.path_zomboid_logs = path_zomboid_logs
            self.path_database = path_database
            self.default_pattern = {'default': default_pattern}

        except EmptyConfigurationError as error:
            logger.critical(f'Parece que você não definiu uma configuração obrigatória: {error}')
            sys.exit()
        except Exception as error:
            logger.critical(f'Erro ao carregar configurações: {error}')
            sys.exit()