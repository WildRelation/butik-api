import duckdb
import os

CATALOG_PATH = os.getenv("CATALOG_PATH", "./data/katalog.duckdb")
DATA_PATH    = os.getenv("DATA_PATH",    "./data/lake/")


def get_conn():
    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
    con = duckdb.connect()
    con.execute("LOAD ducklake")
    con.execute(f"ATTACH 'ducklake:{CATALOG_PATH}' AS butik (DATA_PATH '{DATA_PATH}')")
    return con


def init_db():
    con = get_conn()
    con.execute("""
        CREATE TABLE IF NOT EXISTS butik.kunder (
            id      INTEGER,
            namn    VARCHAR NOT NULL,
            email   VARCHAR NOT NULL,
            telefon VARCHAR
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS butik.produkter (
            id         INTEGER,
            namn       VARCHAR NOT NULL,
            pris       DOUBLE NOT NULL,
            lagersaldo INTEGER DEFAULT 0
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS butik.ordrar (
            id         INTEGER,
            kund_id    INTEGER,
            produkt_id INTEGER,
            antal      INTEGER NOT NULL,
            skapad     TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.close()


def next_id(table: str) -> int:
    con = get_conn()
    row = con.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM butik.{table}").fetchone()
    con.close()
    return row[0]
