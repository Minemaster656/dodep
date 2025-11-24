import sqlite3

def fetch_ddls(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Get table DDLs
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    ddl_statements = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        ddl = cursor.fetchone()[0]
        ddl_statements.append(ddl)

    conn.close()
    return ddl_statements

# Fetch DDLs from data.db
ddls = fetch_ddls('data.db')

with open("DDL.sql", encoding='utf-8', mode="w") as f:
    f.writelines(ddls)