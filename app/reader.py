# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 23/09/2024

import os
import re
import time
import json
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .config import Config
from .database import Database, LogFile, LogFilePatterns, Log, Pattern

logger = logging.getLogger('app.reader')
config = Config()
database = Database()

class Reader:
    def __init__(self):
        self.keyboard_interrupt = False
        self.cached_logfiles = {}

    def check_exit(self) -> bool:
        return self.keyboard_interrupt

    def update_cached_logsfiles(self) -> None:
        logger.debug(f'Verificando se os logfiles em cache precisam de atualização.')
        if not os.path.exists(config.path_zomboid_logs):
            logger.error(f'O diretório "{config.path_zomboid_logs}" não foi encontrado.')
            return
        
        for f_name in os.listdir(config.path_zomboid_logs):
            f_fullpath = os.path.join(config.path_zomboid_logs, f_name)

            if f_name.endswith('.txt'):
                f_match = re.match(r'^(\d{2}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(.+)\.txt$', f_name)
                
                if f_match:
                    f_datetime = datetime.strptime(f_match.group(1), '%d-%m-%y_%H-%M-%S')
                    f_type = f_match.group(2)

                    f_mtime = datetime.fromtimestamp(os.path.getmtime(f_fullpath))
                    f_ctime = datetime.fromtimestamp(os.path.getctime(f_fullpath))
                    f_size = os.path.getsize(f_fullpath)

                    logfile = LogFile(
                        log_date=f_datetime,
                        log_type=f_type,
                        file_name=f_name,
                        file_path=f_fullpath,
                        last_modified=f_mtime,
                        creation_time=f_ctime,
                        file_size=f_size
                    )

                    if logfile.log_type in self.cached_logfiles:
                        cached_logfile: LogFile = self.cached_logfiles[logfile.log_type]
                        if cached_logfile.is_older_than(logfile):
                            logger.debug(f'Logfile {cached_logfile.log_type} está desatualizado. Substituindo pelo logfile mais atual.')
                            self.cached_logfiles[logfile.log_type] = logfile
                    else:
                        logger.debug(f'Logfile {logfile.log_type} não está em cache. Adicionando ao cache.')
                        self.cached_logfiles[logfile.log_type] = logfile

        logger.debug('Verificação e atualização dos logfiles em cache concluída.')

    def update_database_logfiles(self, db: Session) -> None:
        logger.debug('Verificando se os logfiles da database presisam de atualização.')
        try:
            db_logfiles: list[LogFile] = db.query(LogFile).all()
            db_logfiles_map = {db_logfile.log_type: db_logfile for db_logfile in db_logfiles}

            for cached_logfile in self.cached_logfiles.values():
                if cached_logfile.log_type in db_logfiles_map:
                    db_logfile: LogFile = db_logfiles_map[cached_logfile.log_type]
                    if cached_logfile.has_changed(db_logfile):
                        logger.debug(f'Logfile {db_logfile.log_type} está desatualizado. Atualizando informações.')
                        db_logfile.update_from_dict(cached_logfile.to_dict())
                else:
                    logger.debug(f'Logfile {cached_logfile.log_type} não encontrado na database. Adicionando à database.')
                    db.add(cached_logfile)

            db.commit()

        except KeyboardInterrupt:
                db.rollback()
                self.keyboard_interrupt = True
                logger.warning('Combinação CTRL + C pressionada. Preparando para encerrar com segurança...')
        except Exception as error:
            logger.exception(f'Erro ao tentar atualizar logfiles na database: {error}')
            db.rollback()

        finally:
            logger.debug('Verificação e atualização dos logfiles da database concluída.')

    def read_logs(self, db: Session) -> None:
        logger.debug('Iniciando leitura dos arquivos de log.')
        # Lógica de leitura
        logger.debug('Leitura dos arquivos de log concluída.')

    def run_mainloop(self) -> None:
        logger.debug('Looping principal iniciado.')
        logger.info('Pressione CTRL + C para encerrar a aplicação com segurança.')

        with database.create_session() as db:
            try:
                while True:
                    logger.debug('Iniciando looping...')

                    if self.check_exit(): # Verifica se está tudo pronto para encerrar de forma segura
                        logger.debug('Encerramento seguro aprovado, aplicação encerrada. Até mais!')
                        return
                    
                    self.update_cached_logsfiles()
                    self.update_database_logfiles(db)
                    self.read_logs(db)

                    if config.app_expiration_time and config.app_expiration_time > 0:
                        pass
                        # self.clean_database()

                    frequency = config.app_reading_frequency
                    logger.debug(f'Aguardando {frequency} segundos antes de iniciar o próximo looping.')
                    time.sleep(frequency)

            except KeyboardInterrupt:
                logger.warning('Combinação CTRL + C pressionada. Você encerrou a aplicação com segurança.')
            except Exception as e:
                logger.critical(f'Um erro crítico encerrou a aplicação: {e}', exc_info=True, stack_info=True)
                db.rollback()
            finally:
                try:
                    if db.dirty or db.new or db.deleted:
                        db.commit()
                except Exception as error:
                    logger.exception(f'Erro ao commitar alterações pendentes antes de encerrar a aplicação: {error}')
                    db.rollback()
                logger.debug('Looping principal finalizado e sessão de database encerrada.')