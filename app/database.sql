CREATE TABLE IF NOT EXISTS log_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patterns TEXT DEFAULT '{}',
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

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    log_file_id INTEGER NOT NULL REFERENCES log_files (id) ON DELETE CASCADE ON UPDATE CASCADE,
    log_file_type TEXT NOT NULL REFERENCES log_files (log_type) ON DELETE CASCADE ON UPDATE CASCADE,
    log_date DATETIME NOT NULL,
    json_data TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (log_file_id) REFERENCES log_files (id)
);