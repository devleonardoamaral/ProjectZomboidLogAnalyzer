# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 23/09/2024

import os
import logging
from sqlalchemy import create_engine, Column, Integer, Text, func, DateTime, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
from typing import Generator, Any
from .globals import get_root_dir
from .config import Config

logger = logging.getLogger('app.database')

config = Config()
Base = declarative_base()

class LogFile(Base):
    __tablename__ = 'log_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_date = Column(DateTime, nullable=False)  # Data do nome do arquivo
    log_type = Column(Text, nullable=False)  # Tipo de log
    file_name = Column(Text, nullable=False)  # Nome completo do arquivo
    file_path = Column(Text, nullable=False)  # Caminho completo do arquivo
    last_modified = Column(DateTime, nullable=False)  # Última modificação
    creation_time = Column(DateTime, nullable=False)  # Criação no sistema
    file_size = Column(Integer, nullable=False)  # Tamanho em bytes
    cursor_position = Column(Integer, default=0)  # Posição do cursor
    created_at = Column(DateTime, nullable=False, default=func.now())  # Criação na DB

class Pattern(Base):
    __tablename__ = 'patterns'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, nullable=False, default=func.now())

class LogFilePatterns(Base):
    __tablename__ = 'log_files_patterns'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_id = Column(Integer, ForeignKey('patterns.id'), nullable=False)  # Referência à tabela patterns
    log_file_id = Column(Integer, ForeignKey('log_files.id'), nullable=False)  # Referência à tabela log_files
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, nullable=False, default=func.now())

class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_id = Column(Integer, ForeignKey('patterns.id'), nullable=False)  # Referência à tabela patterns
    log_file_id = Column(Integer, ForeignKey('log_files.id'), nullable=False)  # Referência à tabela log_files
    log_file_type = Column(Text, nullable=False)  # Tipo do arquivo de log
    log_date = Column(DateTime, nullable=False)  # Data estampada na linha do log
    json_data = Column(Text, nullable=False)  # Dados do log processados em JSON
    created_at = Column(DateTime, nullable=False, default=func.now())  # Data de registro na DB

class Database:
    _instance = None

    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_already_initialized'):
            self.engine = create_engine(f'sqlite://{config.path_database}', echo=True)
            self._already_initialized = True

    def setup_database(self) -> None:
        with self.engine.connect() as connection:
            database_sql = ''
            try:
                try:
                    with open(os.path.join(get_root_dir(), 'app', 'database.sql')) as f:
                        database_sql = f.read()
                except PermissionError as error:
                    logger.critical(f'Permissões insufucientes para ler o arquivo com o script de inicialização SQL: {error}')
                    return
                except Exception as error:
                    logger.critical(f'Erro ao ler arquivo com o script de inicialização SQL: {error}')
                    return
                try:
                    connection.execute(database_sql)
                    connection.commit()
                except SQLAlchemyError as error:
                    logger.critical(f'Erro durante a inicialização do banco de dados através do script SQL: {error}')
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
                if session.dirty or session.new:
                    session.commit()
            except SQLAlchemyError as error:
                logger.exception(f'Erro ao commitar a sessão: {error}')
                session.rollback()
            finally:
                session.close()
                logger.debug('Sessão encerrada.')
