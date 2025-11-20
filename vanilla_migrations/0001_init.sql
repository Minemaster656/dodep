PRAGMA user_version = 1;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    login TEXT UNIQUE,
    password_hash TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    last_online_at INTEGER DEFAULT (strftime('%s', 'now')),
    balance_hand REAL DEFAULT (100),
    balance_bank REAL DEFAULT (100),
    debt REAL DEFAULT (0)
);