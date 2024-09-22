CREATE TABLE IF NOT EXISTS readers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    abspath TEXT NOT NULL,
    pattern TEXT,
    size INTEGER NOT NULL,
    cursor_position INTEGER NOT NULL DEFAULT (0),
    mtime INTEGER NOT NULL,
    isoformat INTEGER EXT NOT NULL,
    timestamp INTEGER EXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reader_id INTEGER REFERENCES readers (id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
    pattern_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    isoformat TEXT NOT NULL, 
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

