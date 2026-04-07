"""
OrderRepository — thin data-access layer over PostgreSQL.
All SQL is isolated here so the service layer stays clean.
"""


import psycopg2
import json
from typing import Optional
from datetime import datetime, timezone
import logging


from ..model.order import Order, OrderStatus
logger = logging.getLogger(__name__)


class OrderRepository:

    def set_damage(self, order_id: str, damaged: bool, damaged_items: list = None) -> None:
        """Set the damaged flag and damaged items list for an order."""
        sql = """
            UPDATE orders
            SET damaged = %s, damaged_items = %s, updated_at = %s
            WHERE order_id = %s
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (damaged, json.dumps(damaged_items or []), datetime.now(timezone.utc), order_id))
            self._conn.commit()

    def __init__(self, conn):
        """
        :param conn: a psycopg2 connection object
        """
        self._conn = conn

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def save(self, order: Order) -> Order:
        """Insert a new order and return it with the generated id."""
        confirmed_at_value = order.confirmed_at or order.created_at

        sql = """
            INSERT INTO orders
                (order_id, student_name, email, package_id,
                 selected_items, rental_start_date, rental_end_date,
                 total_amount, deposit, fulfillment_method, status, confirmed_at,
                 created_at, updated_at, hold_id, payment_id)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            order.order_id,
            order.student_name,
            order.email,
            order.package_id,
            json.dumps(order.selected_items),
            order.rental_start_date,
            order.rental_end_date,
            order.total_amount,
            order.deposit,
            order.fulfillment_method,
            order.status.value,
            confirmed_at_value,
            order.created_at,
            order.updated_at,
            order.hold_id,
            order.payment_id,
        )
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            order.id = cur.fetchone()[0]
        return order

    def update_status(self, order_id: str, new_status: OrderStatus) -> None:
        """Update order status and timestamps."""
        sql = """
            UPDATE orders
            SET status = %s, updated_at = %s
        """
        params = [new_status.value, datetime.now(timezone.utc)]

        # Also set status-specific timestamps
        if new_status == OrderStatus.CONFIRMED:
            sql += ", confirmed_at = %s"
            params.append(datetime.now(timezone.utc))
        elif new_status == OrderStatus.ACTIVE:
            sql += ", activated_at = %s"
            params.append(datetime.now(timezone.utc))
        elif new_status == OrderStatus.RETURNED or new_status == OrderStatus.RETURNED_DAMAGED:
            sql += ", returned_at = %s"
            params.append(datetime.now(timezone.utc))
        elif new_status == OrderStatus.COMPLETED:
            sql += ", completed_at = %s"
            params.append(datetime.now(timezone.utc))

        sql += " WHERE order_id = %s"
        params.append(order_id)

        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            self._conn.commit()

    def update_payment_id(self, order_id: str, payment_id: str) -> None:
        """Attach payment reference to an existing order."""
        sql = """
            UPDATE orders
            SET payment_id = %s, updated_at = %s
            WHERE order_id = %s
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (payment_id, datetime.now(timezone.utc), order_id))
            self._conn.commit()

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def find_by_order_id(self, order_id: str) -> Optional[Order]:
        """Fetch a single order by order_id."""
        sql = """
            SELECT id, order_id, student_name, email, package_id,
                   selected_items, rental_start_date, rental_end_date,
                   total_amount, deposit, fulfillment_method, status,
                   created_at, updated_at, confirmed_at, activated_at,
                   returned_at, completed_at, hold_id, payment_id, damaged, damaged_items
            FROM orders
            WHERE order_id = %s
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (order_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_order(row)

    def find_by_email(self, email: str) -> list:
        """Fetch all orders for a student by email."""
        sql = """
            SELECT id, order_id, student_name, email, package_id,
                   selected_items, rental_start_date, rental_end_date,
                   total_amount, deposit, fulfillment_method, status,
                   created_at, updated_at, confirmed_at, activated_at,
                   returned_at, completed_at, hold_id, payment_id, damaged, damaged_items
            FROM orders
            WHERE email = %s
            ORDER BY created_at DESC
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (email,))
            return [self._row_to_order(row) for row in cur.fetchall()]

    def find_by_status(self, status: OrderStatus) -> list:
        """Fetch all orders with a given status."""
        sql = """
            SELECT id, order_id, student_name, email, package_id,
                   selected_items, rental_start_date, rental_end_date,
                   total_amount, deposit, fulfillment_method, status,
                   created_at, updated_at, confirmed_at, activated_at,
                   returned_at, completed_at, hold_id, payment_id, damaged, damaged_items
            FROM orders
            WHERE status = %s
            ORDER BY created_at DESC
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (status.value,))
            return [self._row_to_order(row) for row in cur.fetchall()]

    def find_by_rental_start_date(self, date: str) -> list:
        """Fetch all orders with rental starting on a specific date."""
        sql = """
            SELECT id, order_id, student_name, email, package_id,
                   selected_items, rental_start_date, rental_end_date,
                   total_amount, deposit, fulfillment_method, status,
                   created_at, updated_at, confirmed_at, activated_at,
                   returned_at, completed_at, hold_id, payment_id, damaged, damaged_items
            FROM orders
            WHERE rental_start_date = %s
            ORDER BY created_at DESC
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (date,))
            return [self._row_to_order(row) for row in cur.fetchall()]

    def find_by_rental_end_date(self, date: str) -> list:
        """Fetch all orders with rental ending on a specific date."""
        sql = """
            SELECT id, order_id, student_name, email, package_id,
                   selected_items, rental_start_date, rental_end_date,
                   total_amount, deposit, fulfillment_method, status,
                   created_at, updated_at, confirmed_at, activated_at,
                   returned_at, completed_at, hold_id, payment_id, damaged, damaged_items
            FROM orders
            WHERE rental_end_date = %s
            ORDER BY created_at DESC
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (date,))
            return [self._row_to_order(row) for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _row_to_order(self, row) -> Order:
        """Convert a database row to an Order object."""
        # selected_items from JSONB column is already parsed as a list/dict
        selected_items = row[5]
        if isinstance(selected_items, str):
            selected_items = json.loads(selected_items)

        # damaged_items from JSONB column
        damaged_items = row[21] if len(row) > 21 else []
        if isinstance(damaged_items, str):
            damaged_items = json.loads(damaged_items)
        elif damaged_items is None:
            damaged_items = []

        # damaged is at index 20
        damaged = row[20] if len(row) > 20 else None

        # Convert naive datetimes from database to timezone-aware UTC
        created_at = row[12]
        if created_at and isinstance(created_at, datetime) and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        updated_at = row[13]
        if updated_at and isinstance(updated_at, datetime) and updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        confirmed_at = row[14]
        if confirmed_at and isinstance(confirmed_at, datetime) and confirmed_at.tzinfo is None:
            confirmed_at = confirmed_at.replace(tzinfo=timezone.utc)

        activated_at = row[15]
        if activated_at and isinstance(activated_at, datetime) and activated_at.tzinfo is None:
            activated_at = activated_at.replace(tzinfo=timezone.utc)

        returned_at = row[16]
        if returned_at and isinstance(returned_at, datetime) and returned_at.tzinfo is None:
            returned_at = returned_at.replace(tzinfo=timezone.utc)

        completed_at = row[17]
        if completed_at and isinstance(completed_at, datetime) and completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)

        return Order(
            id=row[0],
            order_id=row[1],
            student_name=row[2],
            email=row[3],
            package_id=row[4],
            selected_items=selected_items,
            rental_start_date=row[6],
            rental_end_date=row[7],
            total_amount=row[8],
            deposit=row[9],
            fulfillment_method=row[10],
            status=OrderStatus(row[11]),
            created_at=created_at,
            updated_at=updated_at,
            confirmed_at=confirmed_at,
            activated_at=activated_at,
            returned_at=returned_at,
            completed_at=completed_at,
            hold_id=row[18],
            payment_id=row[19],
            damaged=damaged,
            damaged_items=damaged_items,
        )
