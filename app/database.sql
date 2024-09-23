CREATE TABLE IF NOT EXISTS log_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATETIME NOT NULL,
    log_type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    last_modified DATETIME NOT NULL,
    creation_time DATETIME NOT NULL,
    file_size INTEGER NOT NULL,
    cursor_position INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS log_files_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER NOT NULL,
    log_file_id INTEGER NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (pattern_id) REFERENCES patterns (id),
    FOREIGN KEY (log_file_id) REFERENCES log_files (id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER NOT NULL,
    log_file_id INTEGER NOT NULL,
    log_file_type TEXT NOT NULL,
    log_date DATETIME NOT NULL,
    json_data TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (pattern_id) REFERENCES patterns (id),
    FOREIGN KEY (log_file_id) REFERENCES log_files (id)
);