from sqlite3 import connect
from colorama import Fore, Style
conn = connect('data.db')
cursor = conn.cursor()

cursor.execute("PRAGMA user_version")
version = cursor.fetchone()[0]

print(f"{Fore.GREEN}DB SCHEMA VERSION: {Style.BRIGHT}{Fore.BLUE}{version}{Style.RESET_ALL}")

if version == 0:
    version += 1
    cursor.execute(f"PRAGMA user_version = {version}")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deleted INTEGER DEFAULT 0,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
        session_uuid TEXT,
        avatar TEXT DEFAULT '🤑',
        avatarcolor1 TEXT DEFAULT 'slate-600',
        avatarcolor2 TEXT DEFAULT 'slate-900',
        avatargradientvar INTEGER DEFAULT 0,
        color1 TEXT DEFAULT 'neutral-50',
        color2 TEXT DEFAULT 'neutral-700',
        about TEXT,
        top3_wins TEXT DEFAULT '0 0 : 0 0 : 0 0',
        balance REAL DEFAULT 100,
        debt REAL DEFAULT 0,
        top_balance REAL DEFAULT 0,
        top_debt REAL DEFAULT 0,
        works_count INTEGER DEFAULT 0,
        casino_count INTEGER DEFAULT 0
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target INTEGER NOT NULL,
        sender INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'bet', 'win', 'work', 'debt_change', 'transfer'
        amount REAL NOT NULL,
        balance_after REAL NOT NULL,
        activity_type TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (target) REFERENCES users(id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fav_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        activity_type TEXT,
        weight INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requester_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        STATE INTEGER DEFAULT 0, -- -1:BLOCK 0:REQUEST_FRIENDS 1:FRIENDS,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,  
        FOREIGN KEY (requester_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )
    """)
    conn.commit()