# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 22/09/2024, 17:00 (UTC/GMT -03:00) 

import os
import logging
from logging import Logger, Formatter
from logging.handlers import RotatingFileHandler
from typing import Optional, Literal
from .globals import get_root_dir

LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

class StreamFormatter(Formatter):
    def format(self, record):
        s = super().format(record)

        colors = {
            'NOTSET': '\033[0m',      # Sem cor
            'DEBUG': '\033[94m',      # Azul
            'INFO': '\033[92m',       # Verde
            'WARNING': '\033[93m',    # Amarelo
            'ERROR': '\033[91m',      # Vermelho
            'CRITICAL': '\033[41;97m' # Vermelho no fundo branco
        }

        s = colors.get(record.levelname, '\033[0m') + s + '\033[0m'

        return s

class LoggerManager:
    @classmethod
    def setup_logger(cls, name: str, is_stream: bool = True, is_file: bool = False, filename: Optional[str] = None, *, level = logging.NOTSET, propagate: bool = True) -> Logger:
        logger = logging.getLogger(name)
        logger.propagate = propagate
        logger.setLevel(level)

        if is_stream:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(StreamFormatter(
                fmt='{asctime:<20} {levelname:<10} {name:<20} {message}',
                datefmt='%d/%m/%y %H:%M:%S',
                style='{'
            ))
            logger.addHandler(stream_handler)

        if is_file and isinstance(filename, str):
            logs_dir = os.path.join(get_root_dir(), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            log_path = os.path.join(logs_dir, f'{filename}.log')

            file_handler = RotatingFileHandler(
                filename=log_path, 
                mode="a",
                maxBytes=1024 * 1024 * 10, # 10 MB
                backupCount=2,
                encoding='utf-8'
            )
            file_handler.setFormatter(Formatter(
                fmt='{asctime:<20} {levelname:<10} {name:<20} {message}',
                datefmt='%d/%m/%y %H:%M:%S',
                style='{'
            ))
            logger.addHandler(file_handler)

        return logger
