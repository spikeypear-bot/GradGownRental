"""
Migration script to enrich existing orders' selected_items with size information from inventory API.

This script:
1. Fetches all orders
2. For each order, fetches the inventory details for each item
3. Updates the order's selected_items to include size, itemName, itemType, etc.
"""

import os
import json
import logging
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.error import URLError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gown_rental")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

INVENTORY_API = os.getenv("INVENTORY_API_URL", "http://localhost:8080")


def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def fetch_item_details(model_id):
    """Fetch item details from inventory API using urllib."""
    try:
        url = f"{INVENTORY_API}/api/inventory/models/{model_id}"
        with urlopen(url, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if data.get("data"):
                    item_data = data["data"]
                    return {
                        "modelId": item_data.get("modelId"),
                        "size": item_data.get("size"),
                        "itemName": item_data.get("style", {}).get("itemName"),
                        "itemType": item_data.get("style", {}).get("itemType"),
                        "rentalFee": item_data.get("style", {}).get("rentalFee"),
                        "deposit": item_data.get("style", {}).get("deposit"),
                    }
            else:
                logger.warning(f"Inventory API returned {response.status} for model {model_id}")
    except URLError as e:
        logger.error(f"Error fetching item details for {model_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching item details for {model_id}: {e}")
    return None


def migrate_orders():
    """Migrate all orders to include size information."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Fetch all orders
        cur.execute("SELECT id, order_id, selected_items FROM orders WHERE selected_items IS NOT NULL")
        orders = cur.fetchall()
        
        logger.info(f"Found {len(orders)} orders to migrate")
        
        updated_count = 0
        for order in orders:
            selected_items = order["selected_items"]
            if isinstance(selected_items, str):
                selected_items = json.loads(selected_items)
            
            # Check if already has size
            if selected_items and len(selected_items) > 0 and "size" in selected_items[0]:
                logger.info(f"Order {order['order_id']} already has size information, skipping")
                continue
            
            # Enrich each item with size and other details
            enriched_items = []
            for item in selected_items:
                model_id = item.get("modelId")
                if not model_id:
                    enriched_items.append(item)
                    continue
                
                # Fetch details from inventory
                details = fetch_item_details(model_id)
                if details:
                    # Merge inventory details with existing item data
                    enriched_item = {
                        **item,
                        "size": item.get("size") or details.get("size"),
                        "itemName": item.get("itemName") or details.get("itemName"),
                        "itemType": item.get("itemType") or details.get("itemType"),
                    }
                    enriched_items.append(enriched_item)
                    logger.info(f"Enriched item {model_id} with size: {details.get('size')}")
                else:
                    logger.warning(f"Could not fetch details for {model_id}, keeping original item")
                    enriched_items.append(item)
            
            # Update the order
            cur.execute(
                """UPDATE orders 
                   SET selected_items = %s, updated_at = %s
                   WHERE id = %s""",
                (json.dumps(enriched_items), datetime.now(timezone.utc), order["id"])
            )
            updated_count += 1
            logger.info(f"Updated order {order['order_id']} with enriched items")
        
        conn.commit()
        logger.info(f"Migration complete. Updated {updated_count} orders")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    logger.info("Starting migration to add size information to orders...")
    migrate_orders()
    logger.info("Migration finished!")
