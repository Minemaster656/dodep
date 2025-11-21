from sqlite3 import connect
from flask import g

# conn = connect("data.db")
# cur = conn.cursor()

DB_PATH = "data.db"

def get_db():
    if "db" not in g:
        g.db = connect(DB_PATH)
        # g.db.row_factory = sqlite3.Row  # по желанию
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()