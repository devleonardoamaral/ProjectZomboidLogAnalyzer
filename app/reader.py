# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 22/09/2024, 17:00 (UTC/GMT -03:00) 

import os
import re
import time
import json
import logging
from datetime import datetime, timedelta
from .config import Config
from .database import Database
from dataclasses import dataclass

logger = logging.getLogger('app.reader')
config = Config()

@dataclass
class LogFile:
    name: str
    filename: str
    abspath: str
    size: int
    mtime: int
    isoformat: str
    timestamp: int

    def has_changed(self, other: 'LogFile') -> bool:
        """Compares the current LogFile instance with another to see if any attributes have changed."""
        
        filename_changed = self.filename != other.filename
        abspath_changed = self.abspath != other.abspath
        size_changed = self.size != other.size
        mtime_changed = abs(other.mtime - self.mtime) > 1
        isoformat_changed = self.isoformat != other.isoformat
        timestamp_changed = abs(other.timestamp - self.timestamp) > 1

        # Log each comparison
        """
        logger.debug(f"Comparing LogFiles:")
        logger.debug(f"  Filename changed: {filename_changed} (self: {self.filename}, other: {other.filename})")
        logger.debug(f"  Abspath changed: {abspath_changed} (self: {self.abspath}, other: {other.abspath})")
        logger.debug(f"  Size changed: {size_changed} (self: {self.size}, other: {other.size})")
        logger.debug(f"  Mtime changed: {mtime_changed} (self: {self.mtime}, other: {other.mtime})")
        logger.debug(f"  Isoformat changed: {isoformat_changed} (self: {self.isoformat}, other: {other.isoformat})")
        logger.debug(f"  Timestamp changed: {timestamp_changed} (self: {self.timestamp}, other: {other.timestamp})")
        """

        return (
            filename_changed or
            abspath_changed or
            size_changed or
            mtime_changed or
            isoformat_changed or
            timestamp_changed
        )

class Reader:
    def __init__(self):
        self.log_file_data = {}

    def _update_log_file_data(self, logfile: LogFile) -> None:
        """Updates the stored log file data if it has changed or if the new logfile is more recent."""
        log_file_data = self.log_file_data.get(logfile.name)

        if log_file_data:
            # Verifica se o novo logfile é mais recente
            if logfile.timestamp > log_file_data.timestamp:
                self.log_file_data[logfile.name] = logfile
                logger.info(f"Log file updated: {logfile.name} (timestamp: {logfile.timestamp})")
        else:
            self.log_file_data[logfile.name] = logfile
            logger.info(f"Log file added: {logfile.name}")

    def update_valid_logs(self) -> None:
        """Updates the list of valid log files based on timestamps and types."""
        if not os.path.exists(config.path_zomboid_logs):
            logger.error(f"The directory {config.path_zomboid_logs} was not found.")
            return

        for log_file in os.listdir(config.path_zomboid_logs):
            log_file_fullpath = os.path.join(config.path_zomboid_logs, log_file)

            if log_file.endswith('.txt'):
                log_file_match = re.match(r'^(\d{2}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(.+)\.txt$', log_file)

                if log_file_match:
                    log_file_raw_time = log_file_match.group(1)
                    log_file_type = log_file_match.group(2)

                    log_file_datetime = datetime.strptime(log_file_raw_time, '%d-%m-%y_%H-%M-%S')
                    log_file_isoformat = log_file_datetime.isoformat()
                    log_file_timestamp = int(log_file_datetime.timestamp())
                    log_file_mtime = int(os.path.getmtime(log_file_fullpath))
                    log_file_size = os.path.getsize(log_file_fullpath)

                    logfile =  LogFile(
                        name=log_file_type,
                        filename=log_file,
                        abspath=log_file_fullpath,
                        size=log_file_size,
                        mtime=log_file_mtime,
                        isoformat=log_file_isoformat,
                        timestamp=log_file_timestamp
                    )

                    self._update_log_file_data(logfile)

    def update_readers(self) -> None:
        with Database.create_session() as (conn, cursor):
            for logfile in self.log_file_data.values():
                logfile: LogFile = logfile
                cursor.execute('SELECT * FROM readers WHERE name = ?', (logfile.name,))
                reader_row = cursor.fetchone()

                if not reader_row:

                    cursor.execute(
                        'INSERT INTO readers (name, filename, abspath, pattern, size, cursor_position, mtime, isoformat, timestamp, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (logfile.name, logfile.filename, logfile.abspath, None, logfile.size, 0, logfile.mtime, logfile.isoformat, logfile.timestamp, int(datetime.now().timestamp()))
                    )
                    logger.info(f"New reader added: {logfile.name}")
                else:
                    existing_logfile = LogFile(
                        name=reader_row[1],
                        filename=reader_row[2],
                        abspath=reader_row[3],
                        size=reader_row[5],
                        mtime=reader_row[7],
                        isoformat=reader_row[8],
                        timestamp=reader_row[9]
                    )

                    if existing_logfile.has_changed(logfile):
                        cursor.execute(
                            'UPDATE readers SET filename = ?, abspath = ?, pattern = ?, size = ?, cursor_position = ?, mtime = ?, isoformat = ?, timestamp = ?, created_at = ? WHERE id = ?',
                            (logfile.filename, logfile.abspath, reader_row[4], logfile.size, reader_row[6], logfile.mtime, logfile.isoformat, logfile.timestamp, int(datetime.now().timestamp()), reader_row[0])
                        )
                        logger.info(f"Reader updated: {logfile.name}")

            conn.commit()

    def clean_database(self) -> None:
        """Removes old log entries from the database based on the expiration time."""
        threshold_datetime = datetime.now() - timedelta(seconds=config.app_expiration_time)
        
        with Database.create_session() as (conn, cursor):
            query_delete = 'DELETE FROM logs WHERE created_at < ?'
            cursor.execute(query_delete, (threshold_datetime.timestamp(),))
            
            deleted_rows = cursor.rowcount
            conn.commit()
            
            if deleted_rows > 0:
                logger.info(f"{deleted_rows} old log entries cleaned from the database.")
            else:
                logger.debug("No old log entries found to delete.")

    def read_logs(self) -> None:
        with Database.create_session() as (conn, cursor):
            for logfile in self.log_file_data.values():
                logfile: LogFile = logfile
                cursor.execute('SELECT * FROM readers WHERE name = ?', (logfile.name,))
                reader_row = cursor.fetchone()

                if reader_row:
                    if reader_row[6] == os.path.getsize(reader_row[3]):
                        continue

                    logger.info(f'Reading {reader_row[2]}')

                    line_string = None
                    try:
                        with open(reader_row[3], 'rb') as f:
                            f.seek(reader_row[6])
                            line_bin = f.readline()
                            line_string = line_bin.decode(encoding='utf-8', errors='ignore')

                    except FileNotFoundError:
                        logger.error(f"File not found: {reader_row[3]}")
                        continue
                    except Exception as e:
                        logger.exception(f"An error occurred while reading the log file: {e}")
                        continue

                    if line_bin and line_string:
                        line_string = line_string.strip()               
                        logger.info(f'Reading {reader_row[2]}, pos: {reader_row[6]}/{reader_row[5]}, line: {line_string}')

                        try:
                            regex_list = json.loads(str(reader_row[4]))
                        except json.decoder.JSONDecodeError as e:
                            #logger.exception(f'Pattern not found: ID "{reader_row[0]}" reader name "{reader_row[1]}". Error: {e}')
                            regex_list = config.pattern_default

                        new_position = reader_row[6] + len(line_bin)
                        cursor.execute(
                            'UPDATE readers SET cursor_position = ? WHERE id = ?',
                            (new_position, reader_row[0])
                        )
                        conn.commit()

                        match_found = False  # Adicionado para rastrear se uma correspondência foi encontrada

                        pattern_id = 0
                        for regex in regex_list:
                            # logger.debug(f"Using regex: '{regex}' on line: {line_string}")
                            try:
                                match: re.Match = re.match(regex, line_string)
                            except re.error as e:
                                logger.error(f"Invalid regex '{regex}': {e}")
                                continue

                            if match:
                                match_list = list(match.groups())

                                log_datetime = datetime.strptime(match.group(1), '%d-%m-%y %H:%M:%S.%f')
                                log_isoformat = log_datetime.isoformat()
                                log_timestamp = int(log_datetime.timestamp())

                                try:
                                    match_str = json.dumps(match_list)
                                except json.decoder.JSONDecodeError:
                                    match_str = None

                                if match_str:
                                    cursor.execute(
                                        'INSERT INTO logs (reader_id, pattern_id, data, isoformat, timestamp, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                                        (reader_row[0], pattern_id, match_str, log_isoformat, log_timestamp, int(datetime.now().timestamp()))
                                    )
                                    match_found = True  # Atualiza a flag para indicar que uma correspondência foi encontrada
                                    conn.commit()
                                    break
                                else:
                                    logger.error("Failed to serialize match_list to JSON.")
                            pattern_id = pattern_id + 1

                        if not match_found:
                            logger.error(f"No match found for reader: {reader_row[2]}, pos: {reader_row[6]}/{reader_row[5]}, line: {line_string}")
                    else:
                        logger.warning(f"Empty line read from log file. File: {reader_row[3]}")
                else:
                    logger.warning(f"No reader found for logfile: {logfile.name}")


    def run_mainloop(self):
        logger.info('Press CTRL + C to close the application.')
        try:
            while True:
                logger.debug('New looping!')
                self.update_valid_logs()
                self.update_readers()
                try:
                    self.read_logs()
                except Exception as e:
                    logger.exception(f'Exeption: {e}')

                if config.app_expiration_time and config.app_expiration_time > 0:
                    self.clean_database()

                time.sleep(config.app_reading_frequency)
    
        except KeyboardInterrupt:
            logger.warning('You have stopped the application.')
        except Exception as e:
            logger.exception(e)
            logger.critical('An error stopped the application.')
