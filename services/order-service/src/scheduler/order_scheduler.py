"""
OrderScheduler — scheduled jobs for automatic order processing.

Jobs:
  • activate_delivery_orders: Auto-activate DELIVERY orders on rental_start_date
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class OrderScheduler:
    """Manages scheduled jobs for order service."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.order_service = None
    
    def init_app(self, app, order_service):
        """
        Initialize scheduler with Flask app and OrderService.
        
        :param app: Flask application instance
        :param order_service: OrderService instance to use for job execution
        """
        self.order_service = order_service
        
        # Add job: auto-activate DELIVERY orders daily at 6 AM
        self.scheduler.add_job(
            self._activate_delivery_orders_job,
            CronTrigger(hour=6, minute=0),  # Every day at 6:00 AM
            id='activate_delivery_orders',
            name='Activate DELIVERY orders for today',
            replace_existing=True,
        )
        
        # Start scheduler
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Order scheduler started")
            
            # Graceful shutdown
            app.teardown_appcontext(self._shutdown_scheduler)
    
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
    
    def _shutdown_scheduler(self, exception=None):
        """Graceful shutdown of scheduler on app teardown."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Order scheduler shut down")


# Singleton instance
_scheduler = OrderScheduler()


def get_scheduler():
    """Get the singleton scheduler instance."""
    return _scheduler
