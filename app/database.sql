CREATE TABLE IF NOT EXISTS log_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATETIME NOT NULL,  -- Data do nome do arquivo
    log_type TEXT NOT NULL,       -- Tipo de log
    file_name TEXT NOT NULL,      -- Nome completo do arquivo
    file_path TEXT NOT NULL,      -- Caminho completo do arquivo
    last_modified DATETIME NOT NULL,  -- Última modificação
    creation_time DATETIME NOT NULL,   -- Criação no sistema
    file_size INTEGER NOT NULL,        -- Tamanho em bytes
    cursor_position INTEGER DEFAULT 0,  -- Posição do cursor
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))  -- Criação na DB
);

CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),  -- Atualização
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))   -- Criação
);

CREATE TABLE IF NOT EXISTS log_files_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER NOT NULL,
    log_file_id INTEGER NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),  -- Atualização
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),  -- Criação
    FOREIGN KEY (pattern_id) REFERENCES patterns (id),
    FOREIGN KEY (log_file_id) REFERENCES log_files (id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER NOT NULL,
    log_file_id INTEGER NOT NULL,
    log_file_type TEXT NOT NULL,      -- Tipo do arquivo de log
    log_date DATETIME NOT NULL,       -- Data estampada na linha do log
    json_data TEXT NOT NULL,          -- Dados do log processados em JSON
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),  -- Criação na DB
    FOREIGN KEY (pattern_id) REFERENCES patterns (id),
    FOREIGN KEY (log_file_id) REFERENCES log_files (id)
);
