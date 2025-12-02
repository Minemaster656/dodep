PRAGMA user_version = 1;
PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deleted INTEGER DEFAULT 0,
    name TEXT NOT NULL,
    login TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at INTEGER DEFAULT (strftime('%s', 'now')) NOT NULL,
    last_online_at INTEGER DEFAULT (strftime('%s', 'now')) NOT NULL,
    balance_hand REAL DEFAULT 100,
    balance_bank REAL DEFAULT 100,
    balance_casino REAL DEFAULT 0,
    debt REAL DEFAULT 0,
    about TEXT

);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL, --WORK DODEP DEP WIN GRANDWIN
    description TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
