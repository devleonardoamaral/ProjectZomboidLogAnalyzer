# ┓ ┏┓┏┓┳┓┏┓┳┓┳┓┏┓  ┏┓┳┳┓┏┓┳┓┏┓┓ 
# ┃ ┣ ┃┃┃┃┣┫┣┫┃┃┃┃  ┣┫┃┃┃┣┫┣┫┣┫┃ 
# ┗┛┗┛┗┛┛┗┛┗┛┗┻┛┗┛  ┛┗┛ ┗┛┗┛┗┛┗┗┛
# Modified: 22/09/2024, 17:00 (UTC/GMT -03:00) 

import os
import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator, Any
from .globals import get_root_dir
from .config import Config

logger = logging.getLogger('app.database')

class Database:
    @staticmethod
    def setup_database() -> None:
        try:
            with open(os.path.join(get_root_dir(), 'app', 'database.sql')) as f:
                database_sql = f.read()

            with Database.create_session() as (conn, cursor):
                cursor.executescript(database_sql)
                conn.commit()

        except Exception as e:
            logger.exception(f'An error occurred while setting up the database: {e}')

    @contextmanager
    @staticmethod
    def create_session() -> Generator[tuple[sqlite3.Connection, sqlite3.Cursor], Any, None]:
        conn: sqlite3.Connection = sqlite3.connect(Config().path_database)
        cursor: sqlite3.Cursor = conn.cursor()
        
        try:
            yield conn, cursor
        except sqlite3.Error as e:
            logger.exception(f'Error during database session: {e}')
            if conn.in_transaction:
                conn.rollback()
        finally:
            cursor.close()
            conn.close()
