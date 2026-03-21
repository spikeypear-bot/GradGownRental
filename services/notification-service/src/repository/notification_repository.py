"""
NotificationRepository — thin data-access layer over PostgreSQL.
All SQL is isolated here so the service layer stays clean.
"""

import psycopg2
import psycopg2.extras
from typing import Optional

from model.notification_log import NotificationLog, NotificationChannel, NotificationEvent, NotificationStatus


class NotificationRepository:
    def __init__(self, conn):
        """
        :param conn: a psycopg2 connection object (injected at startup via db.connection)
        """
        self._conn = conn

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def save(self, log: NotificationLog) -> NotificationLog:
        """Insert a new notification log row and return it with the generated id."""
        sql = """
            INSERT INTO notification_logs
                (order_id, event_type, channel, recipient, message_body,
                 status, external_id, error_message, created_at)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (
                log.order_id,
                log.event_type.value,
                log.channel.value,
                log.recipient,
                log.message_body,
                log.status.value,
                log.external_id,
                log.error_message,
                log.created_at,
            ))
            log.id = cur.fetchone()[0]
            self._conn.commit()
        return log

    def update_status(
        self,
        log_id: int,
        status: NotificationStatus,
        external_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Update status (and optionally external_id / error_message) after send attempt."""
        sql = """
            UPDATE notification_logs
            SET status = %s,
                external_id = COALESCE(%s, external_id),
                error_message = COALESCE(%s, error_message)
            WHERE id = %s
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (status.value, external_id, error_message, log_id))
            self._conn.commit()

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def find_by_order_id(self, order_id: str) -> list[NotificationLog]:
        sql = """
            SELECT id, order_id, event_type, channel, recipient, message_body,
                   status, external_id, error_message, created_at
            FROM notification_logs
            WHERE order_id = %s
            ORDER BY created_at DESC
        """
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (order_id,))
            rows = cur.fetchall()
        return [self._row_to_model(r) for r in rows]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_model(row: dict) -> NotificationLog:
        return NotificationLog(
            id=row["id"],
            order_id=row["order_id"],
            event_type=NotificationEvent(row["event_type"]),
            channel=NotificationChannel(row["channel"]),
            recipient=row["recipient"],
            message_body=row["message_body"],
            status=NotificationStatus(row["status"]),
            external_id=row["external_id"],
            error_message=row["error_message"],
            created_at=row["created_at"],
        )
