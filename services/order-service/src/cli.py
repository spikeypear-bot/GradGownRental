"""
Flask CLI commands for order-service maintenance tasks.
"""

import json
import logging
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.error import URLError

import click

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Order service CLI commands."""
    pass


def _fetch_item_details(model_id, inventory_api_url):
    """Fetch item details from inventory API using urllib."""
    try:
        url = f"{inventory_api_url}/api/inventory/models/{model_id}"
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


@cli.command()
@click.option('--inventory-api-url', default='http://localhost:8080', help='Inventory API base URL')
@click.pass_context
def migrate_sizes(ctx, inventory_api_url):
    """Migrate orders to include size information from inventory API."""
    from .app import create_app
    
    app = create_app()
    with app.app_context():
        repo = app.extensions.get("order_repo")
        if not repo:
            click.echo("Error: OrderRepository not found in app context")
            return
        
        conn = repo.conn
        cursor = conn.cursor()
        
        try:
            # Fetch all orders
            cursor.execute("SELECT id, order_id, selected_items FROM orders WHERE selected_items IS NOT NULL")
            orders = cursor.fetchall()
            
            click.echo(f"Found {len(orders)} orders to process")
            
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for order in orders:
                order_id, order_uuid, selected_items_str = order
                
                try:
                    selected_items = json.loads(selected_items_str) if isinstance(selected_items_str, str) else selected_items_str
                    
                    # Check if already has size
                    if selected_items and len(selected_items) > 0 and "size" in selected_items[0]:
                        click.echo(f"✓ Order {order_uuid} already has size information, skipping")
                        skipped_count += 1
                        continue
                    
                    # Enrich each item with size and other details
                    enriched_items = []
                    for item in selected_items:
                        model_id = item.get("modelId")
                        if not model_id:
                            enriched_items.append(item)
                            continue
                        
                        # Fetch details from inventory
                        details = _fetch_item_details(model_id, inventory_api_url)
                        if details:
                            # Merge inventory details with existing item data
                            enriched_item = {
                                **item,
                                "size": item.get("size") or details.get("size"),
                                "itemName": item.get("itemName") or details.get("itemName"),
                                "itemType": item.get("itemType") or details.get("itemType"),
                            }
                            enriched_items.append(enriched_item)
                            click.echo(f"  → Enriched item {model_id} with size: {details.get('size')}")
                        else:
                            click.echo(f"  ⚠ Could not fetch details for {model_id}, keeping original item")
                            enriched_items.append(item)
                    
                    # Update the order
                    cursor.execute(
                        """UPDATE orders 
                           SET selected_items = %s, updated_at = %s
                           WHERE id = %s""",
                        (json.dumps(enriched_items), datetime.now(timezone.utc), order_id)
                    )
                    updated_count += 1
                    click.echo(f"✓ Updated order {order_uuid}")
                    
                except Exception as e:
                    error_count += 1
                    click.echo(f"✗ Error processing order {order_uuid}: {e}")
            
            conn.commit()
            click.echo(f"\nMigration complete!")
            click.echo(f"  Updated: {updated_count}")
            click.echo(f"  Skipped: {skipped_count}")
            click.echo(f"  Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            conn.rollback()
            click.echo(f"Error: {e}")
        finally:
            cursor.close()
