#!/usr/bin/env python3
"""
migrate.py — SQL migration runner.

Applies every *.sql file inside db/migrations/ that has not been applied yet,
in strict filename order (alphabetical = chronological given the YYYYMMDD prefix).

A lightweight schema_migrations table is maintained in the same database to
track which files have already been run.  Running this script multiple times is
safe: already-applied migrations are silently skipped.
"""
import glob
import os
import sys

import psycopg2

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "migrations")


def _connect():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def run():
    print("[migrate] connecting to database...")
    conn = _connect()
    conn.autocommit = False

    with conn.cursor() as cur:
        # Bootstrap the tracking table (idempotent)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename   TEXT        PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        conn.commit()

        cur.execute("SELECT filename FROM schema_migrations")
        applied = {row[0] for row in cur.fetchall()}

    files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.sql")))
    if not files:
        print("[migrate] no migration files found — nothing to do")
        conn.close()
        return

    pending = [f for f in files if os.path.basename(f) not in applied]
    if not pending:
        print(f"[migrate] all {len(files)} migration(s) already applied")
        conn.close()
        return

    for path in pending:
        name = os.path.basename(path)
        print(f"[migrate] applying {name} ...")
        sql = open(path).read()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s)", (name,)
                )
            conn.commit()
            print(f"[migrate] {name} OK")
        except Exception as exc:
            conn.rollback()
            print(f"[migrate] FAILED on {name}: {exc}", file=sys.stderr)
            conn.close()
            sys.exit(1)

    conn.close()
    print("[migrate] all migrations applied")


if __name__ == "__main__":
    run()
