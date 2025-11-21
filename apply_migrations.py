import sqlite3
import pathlib

MIGRATIONS_DIR = pathlib.Path(__file__).parent / "vanilla_migrations"
DB_PATH = pathlib.Path(__file__).parent / "db.sqlite3"


def get_current_version(conn: sqlite3.Connection) -> int:
    cur = conn.execute("PRAGMA user_version")
    (version,) = cur.fetchone()
    return version


def iter_migration_files():
    # ожидаем имена вида 0001_*.sql или 0001-*.sql
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    for f in files:
        # берем первые 4 цифры как номер миграции
        num = int(f.name[:4])
        yield num, f


def apply_migrations():
    conn = sqlite3.connect(DB_PATH)
    try:
        current = get_current_version(conn)

        migrations = list(iter_migration_files())
        for num, path in migrations:
            if num <= current:
                continue

            sql = path.read_text(encoding="utf-8")

            cur = conn.cursor()
            try:
                # одна транзакция на миграцию
                cur.executescript("BEGIN;\n" + sql + "\nCOMMIT;")
                print(f"Applied migration {path.name}")
            except Exception as e:
                cur.execute("ROLLBACK;")
                print(f"Failed migration {path.name}: {e}")
                raise
    finally:
        conn.close()


if __name__ == "__main__":
    apply_migrations()
