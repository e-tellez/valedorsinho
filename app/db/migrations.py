"""Lightweight SQL migration runner.

Scans the ``migrations/`` directory at the project root for ``*.sql`` files,
applies any that have not yet been recorded in the ``_migrations`` tracking
table, and marks them as applied.  Safe to run on every startup — already-
applied migrations are skipped in O(1) via a primary-key lookup.

Usage (called automatically from ``app.main`` lifespan)::

    from app.db.migrations import run_pending_migrations
    run_pending_migrations(database_url)
"""

from __future__ import annotations

import glob
import logging
import os

import psycopg2

logger = logging.getLogger(__name__)

_MIGRATIONS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "migrations"
)

_ENSURE_TRACKING_TABLE = """
CREATE TABLE IF NOT EXISTS _migrations (
    name       TEXT        PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def run_pending_migrations(database_url: str) -> None:
    """Apply all pending ``*.sql`` migrations in order.

    Connects to the database, ensures the ``_migrations`` tracking table
    exists, then applies each SQL file whose basename is not yet recorded.
    The connection is always closed before returning, even on error.
    """
    connection = psycopg2.connect(database_url)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(_ENSURE_TRACKING_TABLE)

                cursor.execute("SELECT name FROM _migrations")
                already_applied: set[str] = {row[0] for row in cursor.fetchall()}

                migration_files = sorted(
                    glob.glob(os.path.join(_MIGRATIONS_DIR, "*.sql"))
                )

                for filepath in migration_files:
                    migration_name = os.path.basename(filepath)
                    if migration_name in already_applied:
                        logger.debug("Migration %s already applied, skipping", migration_name)
                        continue

                    with open(filepath) as file_handle:
                        sql = file_handle.read()

                    cursor.execute(sql)
                    cursor.execute(
                        "INSERT INTO _migrations (name) VALUES (%s)", (migration_name,)
                    )
                    logger.info("Applied migration: %s", migration_name)

    except Exception:
        logger.exception("Migration runner failed")
        raise
    finally:
        connection.close()
