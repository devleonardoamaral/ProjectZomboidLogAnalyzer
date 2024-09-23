# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 23/09/2024

import os
import re
import json
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, Text, func, DateTime, ForeignKey, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
from typing import Generator, Any, Union
from .globals import get_root_dir
from .config import Config

logger = logging.getLogger('app.database')

config = Config()
Base = declarative_base()

class LogFile(Base):
    __tablename__ = 'log_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    patterns = Column(Text, default='{}') 
    log_date = Column(DateTime, nullable=False)  # Data do nome do arquivo
    log_type = Column(Text, nullable=False)  # Tipo de log
    file_name = Column(Text, nullable=False)  # Nome completo do arquivo
    file_path = Column(Text, nullable=False)  # Caminho completo do arquivo
    last_modified = Column(DateTime, nullable=False)  # Última modificação
    creation_time = Column(DateTime, nullable=False)  # Criação no sistema
    file_size = Column(Integer, nullable=False)  # Tamanho em bytes
    cursor_position = Column(Integer, default=0)  # Posição do cursor
    created_at = Column(DateTime, nullable=False, default=func.now())  # Criação na DB

    def __init__(
        self,
        log_date: datetime,
        log_type: str,
        file_name: str,
        file_path: str,
        last_modified: datetime,
        file_size: int,
        creation_time: datetime,
        cursor_position: int = 0,
        patterns: Union[dict, str] = '{}'
    ) -> None:
    
        self.log_date = log_date
        self.log_type = log_type
        self.file_name = file_name
        self.file_path = file_path
        self.last_modified = last_modified
        self.file_size = file_size
        self.creation_time = creation_time
        self.cursor_position = cursor_position
        self.set_patterns(patterns)

    def set_patterns(self, patterns: Union[dict, str]) -> None:
        if isinstance(patterns, dict):
            try:
                self.patterns = json.dumps(patterns)
            except Exception as error:
                logger.exception(f'Erro ao serializar pattern para JSON: {error}')
                self.patterns = '{}'
        else:
            self.patterns = patterns if isinstance(patterns, str) and re.match(r'^\{.*\}$', patterns) else '{}'

    def get_patterns(self) -> dict:
        try:
            return json.loads(self.patterns) if self.patterns else {}
        except json.JSONDecodeError as error:
            logger.exception(f'Erro ao desserializar pattern do JSON: {error}')
            return {}

    def has_changed(self, log_file: 'LogFile', time_tolerance: int = 1) -> bool:
        """Compara se houve mudanças em relação a outro LogFile."""
        return (log_file.log_date - self.log_date > timedelta(seconds=time_tolerance)) or \
               self.file_name != log_file.file_name or \
               self.file_path != log_file.file_path or \
               (log_file.last_modified - self.last_modified > timedelta(seconds=time_tolerance)) or \
               (log_file.creation_time - self.creation_time > timedelta(seconds=time_tolerance)) or \
               self.file_size != log_file.file_size or \
               self.cursor_position != log_file.cursor_position
    
    def is_older_than(self, log_file: 'LogFile') -> bool:
        """Verifica se o LogFile atual é mais antigo que o fornecido."""
        return self.log_date < log_file.log_date
    
    def to_dict(self, isoformat: bool = False) -> dict:
        return {
            'id': self.id,
            'log_date': self.log_date if not isoformat else self.log_date.isoformat(),
            'log_type': self.log_type,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'last_modified': self.last_modified if not isoformat else self.last_modified.isoformat(),
            'creation_time': self.creation_time if not isoformat else self.creation_time.isoformat(),
            'file_size': self.file_size,
            'cursor_position': self.cursor_position,
            'created_at': self.created_at if not isoformat else self.created_at.isoformat()
        }
    
    def __str__(self) -> str:
        try:
            return json.dumps(self.to_dict(isoformat=True))
        except Exception:
            return super().__str__()
class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_name = Column(Text, nullable=False)
    log_file_id = Column(Integer, ForeignKey('log_files.id'), nullable=False)  # Referência à tabela log_files
    log_file_type = Column(Text, nullable=False)  # Tipo do arquivo de log
    log_date = Column(DateTime, nullable=False)  # Data estampada na linha do log
    json_data = Column(Text, nullable=False)  # Dados do log processados em JSON
    created_at = Column(DateTime, nullable=False, default=func.now())  # Data de registro na DB

    def __init__(
        self, 
        pattern_name: str,
        log_file_id: int,
        log_file_type: str,
        log_date: datetime,
        json_data: str
    ) -> None:
        self.pattern_name = pattern_name
        self.log_file_id = log_file_id
        self.log_file_type = log_file_type
        self.log_date = log_date
        self.json_data = json_data

class Database:
    _instance = None

    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_already_initialized'):
            self.engine = create_engine(f'sqlite:///{config.path_database}')
            self._already_initialized = True

    def setup_database(self) -> None:
        with self.engine.connect() as connection:
            sql_script = ''
            try:
                try:
                    with open(os.path.join(get_root_dir(), 'app', 'database.sql')) as f:
                        sql_script = f.read()
                except PermissionError as error:
                    logger.critical(f'Permissões insufucientes para ler o arquivo com o script de inicialização SQL: {error}')
                    return
                except Exception as error:
                    logger.critical(f'Erro ao ler arquivo com o script de inicialização SQL: {error}')
                    return
                try:
                    for command in sql_script.split(';'):
                        command = command.strip()
                        if command:
                            connection.execute(text(command))
                    connection.commit()
                except SQLAlchemyError as error:
                    logger.critical(f'Erro durante a inicialização do banco de dados através do script SQL: {error}', exc_info=True, stack_info=True)
                    connection.rollback()
            finally:
                connection.close()
            
    @contextmanager
    def create_session(self) -> Generator[Session, Any, None]:
        session_maker = sessionmaker(self.engine)
        session: Session = session_maker()
        logger.debug('Uma nova sessão foi criada.')
        try:
            yield session
        except SQLAlchemyError as error:
            logger.exception(f'Erro durante a sessão: {error}')
            if session.dirty or session.new:
                session.rollback()
        finally:
            try:
                if session.dirty or session.new or session.deleted:
                    session.commit()
            except SQLAlchemyError as error:
                logger.exception(f'Erro ao commitar a sessão: {error}')
                session.rollback()
            finally:
                session.close()
                logger.debug('Sessão encerrada.')
