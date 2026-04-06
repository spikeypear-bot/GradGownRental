"""
OrderScheduler — scheduled jobs for automatic order processing and reminders.

Jobs:
  • activate_delivery_orders: Auto-activate DELIVERY orders on rental_start_date
  • publish_reminders: publish pickup_reminder and return_reminder events to Kafka
"""

import logging
import atexit
from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from ..model.order import OrderStatus

logger = logging.getLogger(__name__)


class OrderScheduler:
    """Manages scheduled jobs for order service."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.order_service = None
        self.publisher = None
    
    def init_app(self, app, order_service, publisher=None):
        """
        Initialize scheduler with Flask app and OrderService.
        
        :param app: Flask application instance
        :param order_service: OrderService instance to use for job execution
        """
        self.order_service = order_service
        self.publisher = publisher
        
        # Add job: auto-activate DELIVERY orders daily at 6 AM
        self.scheduler.add_job(
            self._activate_delivery_orders_job,
            CronTrigger(hour=6, minute=0),  # Every day at 6:00 AM
            id='activate_delivery_orders',
            name='Activate DELIVERY orders for today',
            replace_existing=True,
        )

        # Add job: publish next-day pickup and return reminders daily at 9 AM
        self.scheduler.add_job(
            self._publish_reminders_job,
            CronTrigger(hour=9, minute=0),  # Every day at 9:00 AM
            id='publish_reminders',
            name='Publish pickup/return reminders for next day',
            replace_existing=True,
        )
        
        # Start scheduler
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Order scheduler started")
            # Graceful shutdown once process exits.
            atexit.register(self._shutdown_scheduler)
    
    def _activate_delivery_orders_job(self):
        """
        Job function: activate all DELIVERY orders with rental_start_date = today.
        Called daily at 6 AM.
        """
        try:
            activated = self.order_service.activate_orders_for_today()
            logger.info(f"Auto-activated {len(activated)} DELIVERY orders for today")
            for order in activated:
                logger.info(f"  ✓ {order.order_id} ({order.student_name})")
        except Exception as e:
            logger.error(f"Error in auto-activate job: {e}", exc_info=True)

    def _publish_reminders_job(self):
        """
        Job function: publish reminder events for orders due in the next 24 hours.
                - pickup_reminder for COLLECTION orders with rental_start_date = tomorrow (CONFIRMED)
                    OR same-day start_date when order was created today
                - return_reminder for rental_end_date = tomorrow (ACTIVE)
        """
        if self.publisher is None:
            logger.warning("Reminder publisher not configured; skipping reminder job")
            return

        target_date = (date.today() + timedelta(days=1)).isoformat()
        try:
            pickup_orders = self.order_service.get_orders_by_rental_date(target_date)
            return_orders = self.order_service.get_orders_by_return_date(target_date)

            pickup_count = 0
            for order in pickup_orders:
                if order.status != OrderStatus.CONFIRMED:
                    continue
                if (order.fulfillment_method or "").upper() != "COLLECTION":
                    continue
                payload = {
                    "order_id": order.order_id,
                    "student_name": order.student_name,
                    "phone": order.phone,
                    "email": order.email,
                    "fulfillment_date": order.rental_start_date,
                    "return_date": order.rental_end_date,
                    "fulfillment_method": order.fulfillment_method,
                }
                self.publisher.publish_pickup_reminder(payload)
                pickup_count += 1

            today_str = date.today().isoformat()
            same_day_orders = self.order_service.get_orders_by_rental_date(today_str)
            for order in same_day_orders:
                if order.status != OrderStatus.CONFIRMED:
                    continue
                if (order.fulfillment_method or "").upper() != "COLLECTION":
                    continue

                created_iso = (
                    order.created_at.date().isoformat()
                    if hasattr(order.created_at, "date")
                    else str(order.created_at)[:10]
                )
                if created_iso != today_str:
                    continue

                payload = {
                    "order_id": order.order_id,
                    "student_name": order.student_name,
                    "phone": order.phone,
                    "email": order.email,
                    "fulfillment_date": order.rental_start_date,
                    "return_date": order.rental_end_date,
                    "fulfillment_method": order.fulfillment_method,
                }
                self.publisher.publish_pickup_reminder(payload)
                pickup_count += 1

            return_count = 0
            for order in return_orders:
                if order.status != OrderStatus.ACTIVE:
                    continue
                payload = {
                    "order_id": order.order_id,
                    "student_name": order.student_name,
                    "phone": order.phone,
                    "email": order.email,
                    "return_date": order.rental_end_date,
                }
                self.publisher.publish_return_reminder(payload)
                return_count += 1

            logger.info(
                "Reminder publish job complete | target_date=%s | pickup=%s | return=%s",
                target_date,
                pickup_count,
                return_count,
            )
        except Exception as e:
            logger.error(f"Error in reminder publish job: {e}", exc_info=True)
    
    def _shutdown_scheduler(self, exception=None):
        """Graceful shutdown of scheduler on app teardown."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Order scheduler shut down")
        if self.publisher:
            self.publisher.close()


# Singleton instance
_scheduler = OrderScheduler()


def get_scheduler():
    """Get the singleton scheduler instance."""
    return _scheduler
