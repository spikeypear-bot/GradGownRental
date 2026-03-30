"""
OrderRepository — thin data-access layer over PostgreSQL.
All SQL is isolated here so the service layer stays clean.
"""


import psycopg2
import json
from typing import Optional
from datetime import datetime
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
            cur.execute(sql, (damaged, json.dumps(damaged_items or []), datetime.utcnow(), order_id))
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
        sql = """
            INSERT INTO orders
                (order_id, student_name, email, phone, package_id, 
                 selected_items, rental_start_date, rental_end_date,
                 total_amount, deposit, fulfillment_method, status, confirmed_at,
                 created_at, updated_at, hold_id, payment_id)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        with self._conn.cursor() as cur:
            cur.execute(sql, (
                order.order_id,
                order.student_name,
                order.email,
                order.phone,
                order.package_id,
                json.dumps(order.selected_items),  # Convert list to JSON
                order.rental_start_date,
                order.rental_end_date,
                order.total_amount,
                order.deposit,
                order.fulfillment_method,
                order.status.value,
                order.confirmed_at,
                order.created_at,
                order.updated_at,
                order.hold_id,
                order.payment_id,
            ))
            order.id = cur.fetchone()[0]
            # autocommit=True in connection, so no explicit commit needed
        return order

    def update_status(self, order_id: str, new_status: OrderStatus) -> None:
        """Update order status and timestamps."""
        sql = """
            UPDATE orders
            SET status = %s, updated_at = %s
        """
        params = [new_status.value, datetime.utcnow()]
        
        # Also set status-specific timestamps
        if new_status == OrderStatus.ACTIVE:
            sql += ", activated_at = %s"
            params.append(datetime.utcnow())
        elif new_status == OrderStatus.RETURNED or new_status == OrderStatus.RETURNED_DAMAGED:
            sql += ", returned_at = %s"
            params.append(datetime.utcnow())
        elif new_status == OrderStatus.COMPLETED:
            sql += ", completed_at = %s"
            params.append(datetime.utcnow())
        
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
            cur.execute(sql, (payment_id, datetime.utcnow(), order_id))
            self._conn.commit()

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def find_by_order_id(self, order_id: str) -> Optional[Order]:
        """Fetch a single order by order_id."""
        sql = """
            SELECT id, order_id, student_name, email, phone, package_id,
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
            SELECT id, order_id, student_name, email, phone, package_id,
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
            SELECT id, order_id, student_name, email, phone, package_id,
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
            SELECT id, order_id, student_name, email, phone, package_id,
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

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _row_to_order(self, row) -> Order:
        """Convert a database row to an Order object."""
        # selected_items from JSONB column is already parsed as a list/dict
        selected_items = row[6]
        if isinstance(selected_items, str):
            selected_items = json.loads(selected_items)
        
        # damaged_items from JSONB column
        damaged_items = row[22] if len(row) > 22 else []
        if isinstance(damaged_items, str):
            damaged_items = json.loads(damaged_items)
        elif damaged_items is None:
            damaged_items = []
        
        # damaged is at index 21
        damaged = row[21] if len(row) > 21 else None
        
        return Order(
            id=row[0],
            order_id=row[1],
            student_name=row[2],
            email=row[3],
            phone=row[4],
            package_id=row[5],
            selected_items=selected_items,
            rental_start_date=row[7],
            rental_end_date=row[8],
            total_amount=row[9],
            deposit=row[10],
            fulfillment_method=row[11],
            status=OrderStatus(row[12]),
            created_at=row[13],
            updated_at=row[14],
            confirmed_at=row[15],
            activated_at=row[16],
            returned_at=row[17],
            completed_at=row[18],
            hold_id=row[19],
            payment_id=row[20],
            damaged=damaged,
            damaged_items=damaged_items,
        )
