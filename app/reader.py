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
from typing import Optional
from .config import Config
from .database import Database, LogFile, Log

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
                        file_size=f_size,
                        patterns=config.patterns.get(f_type, '{}')
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

            for db_logfile in db_logfiles:
                if not os.path.exists(db_logfile.file_path):
                    logger.info(f'LogFile {db_logfile.log_type} removido, devido ao arquivo de log estar ausente: "{db_logfile.file_path}".')
                    db.delete(db_logfile)
                    db_logfiles.remove(db_logfile)
                if not db_logfile.patterns:
                    logger.warning(f'LogFile {db_logfile.log_type} estava com patterns vazio. Foi definido um novo pattern.')
                    db_logfile.set_patterns(config.patterns.get(db_logfile.log_type, '{}'))

            for cached_logfile in self.cached_logfiles.values():
                if cached_logfile.log_type in db_logfiles_map:
                    db_logfile: LogFile = db_logfiles_map[cached_logfile.log_type]
                    if cached_logfile.has_changed(db_logfile):
                        logger.debug(f'Logfile {db_logfile.log_type} está desatualizado. Atualizando informações.')
                        db_logfile.log_date = cached_logfile.log_date
                        db_logfile.log_type = cached_logfile.log_type
                        db_logfile.file_name = cached_logfile.file_name
                        db_logfile.file_path = cached_logfile.file_path
                        db_logfile.last_modified = cached_logfile.last_modified
                        db_logfile.file_size = cached_logfile.file_size
                        db_logfile.creation_time = cached_logfile.creation_time
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

    def _read_log(self, path: str, seek: int, encoding: str = 'utf-8') -> tuple[Optional[str], int]:
        try:
            with open(path, 'rb') as f:
                f.seek(seek)
                line_bytes = f.readline()
                return line_bytes.decode(encoding=encoding, errors='ignore'), seek + len(line_bytes)
            
        except UnicodeDecodeError as error:
            logger.exception(f'Erro ao tentar decodificar linha lida a partir do arquivo de log "{path}" com a posição do cursor iniciando em {seek}: {error}')
            return None, seek
        except PermissionError as error:
            logger.exception(f'Permissões insuficientes para ler arquivo de log: {error}')
            return None, seek
        except FileNotFoundError as error:
            logger.exception(f'Arquivo de log não encontrado: {error}')
            return None, seek
        except Exception as error:
            logger.exception(f'Erro ao ler arquivo de log: {error}')
            return None, seek
            

    def read_logs(self, db: Session) -> None:
        logger.debug('Iniciando leitura dos arquivos de log.')
        try:
            db_logfiles = db.query(LogFile).all()

            if not db_logfiles:
                logger.info('Nenhum logfile encontrado para leitura.')
                return

            for db_logfile in db_logfiles:
                if db_logfile.cursor_position == db_logfile.file_size:
                    logger.debug(f'Não existem novos logs para ler em "{db_logfile.log_type}".')
                    continue

                log_line, new_cursor_position = self._read_log(db_logfile.file_path, db_logfile.cursor_position)

                if log_line is not None:
                    log_line = log_line.strip()
                    logger.debug(f'Linha lida do logfile {db_logfile.log_type} de {db_logfile.cursor_position} até {new_cursor_position} de {db_logfile.file_size}: {log_line}')
                    
                    patterns = db_logfile.get_patterns() or config.default_pattern
                    logger.debug(f'LogFile {db_logfile.log_type} utilizando {patterns}.')

                    match_found = False
                    for pattern_name, pattern in patterns.items():
                        match = re.match(pattern, log_line)

                        if match:
                            match_found = True
                            groups_dict = match.groupdict()
                            logger.debug(groups_dict)

                            try:
                                json_data = json.dumps(groups_dict)
                            except Exception as error:
                                logger.exception(f'Erro ao serializar groups_dict para JSON: {error}')
                                json_data = '{}'

                            log = Log(
                                pattern_name=pattern_name,
                                log_file_id=db_logfile.id,
                                log_file_type=db_logfile.log_type,
                                log_date=datetime.strptime(match.group(1), '%d-%m-%y %H:%M:%S.%f'),
                                json_data=json_data
                            )

                            db.add(log)              

                    if not match_found:
                        logger.warning(f'Nenhum match para {db_logfile.log_type}, linha: {log_line}')

                db_logfile.cursor_position = new_cursor_position
                db.commit()

        except KeyboardInterrupt:
                db.rollback()
                self.keyboard_interrupt = True
                logger.warning('Combinação CTRL + C pressionada. Preparando para encerrar com segurança...')
        except Exception as error:
            logger.exception(f'Erro ao ler arquivos de log: {error}')
            db.rollback()
        finally:
            logger.debug('Leitura dos arquivos de log concluída.')

    def clean_logs(self, db: Session) -> None:
        if config.app_expiration_time and config.app_expiration_time > 0:
            logger.debug('Iniciando limpeza dos logs.')
            try:
                cutoff_time = datetime.now() - timedelta(seconds=config.app_expiration_time)
                deleted_logs_count = db.query(Log).filter(Log.created_at < cutoff_time).delete()
                db.commit()  

                if deleted_logs_count > 0:
                    logger.info(f'Limpeza concluída: {deleted_logs_count} logs deletados.')
                else:
                    logger.debug('Nenhum log a ser deletado.')
            except KeyboardInterrupt:
                db.rollback()
                self.keyboard_interrupt = True
                logger.warning('Combinação CTRL + C pressionada. Preparando para encerrar com segurança...')
            except Exception as error:
                logger.exception(f'Erro ao limpar logs: {error}')
                db.rollback()
            finally:
                logger.debug('Limpeza dos logs concluída.')

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
                    self.clean_logs(db)

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