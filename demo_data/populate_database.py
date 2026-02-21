"""Script to populate database with sample orders for demo purposes"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.database import DatabaseIntegration
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Numeric, Date, JSON


def create_orders_table(engine):
    """Create orders table if it doesn't exist"""
    with engine.connect() as conn:
        # Check if table exists (PostgreSQL)
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'orders'
            );
        """))
        
        table_exists = result.scalar()
        
        if not table_exists:
            print("Creating orders table...")
            conn.execute(text("""
                CREATE TABLE orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    customer_email VARCHAR(255) NOT NULL,
                    customer_name VARCHAR(255),
                    order_date DATE,
                    status VARCHAR(50),
                    shipping_address TEXT,
                    total_amount NUMERIC(10, 2),
                    items JSONB,
                    tracking_number VARCHAR(100),
                    estimated_delivery DATE,
                    delivery_date DATE,
                    cancellation_date DATE,
                    refund_status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
            print("✓ Orders table created")
        else:
            print("Orders table already exists")


async def populate_database():
    """Populate database with sample orders"""
    
    # Check for database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables.")
        print("Please set: DATABASE_URL")
        print("Example: postgresql://user:password@localhost/dbname")
        return
    
    # Load sample data
    data_file = Path(__file__).parent / "sample_data.json"
    with open(data_file, "r") as f:
        data = json.load(f)
    
    # Initialize database connection
    try:
        engine = create_engine(database_url)
        
        # Create table if needed
        create_orders_table(engine)
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    print("=" * 60)
    print("Populating Database with Sample Orders")
    print("=" * 60)
    print()
    
    integration = DatabaseIntegration(database_url)
    
    inserted_orders = []
    
    for order_data in data["orders"]:
        try:
            print(f"Inserting order: {order_data['order_id']}")
            
            # Prepare insert statement
            insert_sql = text("""
                INSERT INTO orders (
                    order_id, customer_email, customer_name, order_date, status,
                    shipping_address, total_amount, items, tracking_number,
                    estimated_delivery, delivery_date, cancellation_date, refund_status
                ) VALUES (
                    :order_id, :customer_email, :customer_name, :order_date, :status,
                    :shipping_address, :total_amount, :items, :tracking_number,
                    :estimated_delivery, :delivery_date, :cancellation_date, :refund_status
                )
                ON CONFLICT (order_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            import json as json_lib
            params = {
                "order_id": order_data["order_id"],
                "customer_email": order_data["customer_email"],
                "customer_name": order_data["customer_name"],
                "order_date": order_data.get("order_date"),
                "status": order_data["status"],
                "shipping_address": order_data.get("shipping_address"),
                "total_amount": order_data["total_amount"],
                "items": json_lib.dumps(order_data.get("items", [])),
                "tracking_number": order_data.get("tracking_number"),
                "estimated_delivery": order_data.get("estimated_delivery"),
                "delivery_date": order_data.get("delivery_date"),
                "cancellation_date": order_data.get("cancellation_date"),
                "refund_status": order_data.get("refund_status")
            }
            
            with engine.connect() as conn:
                conn.execute(insert_sql, params)
                conn.commit()
            
            inserted_orders.append(order_data["order_id"])
            print(f"  ✓ Inserted order {order_data['order_id']}")
            
        except Exception as e:
            print(f"  ✗ Error inserting order {order_data['order_id']}: {e}")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Successfully inserted/updated {len(inserted_orders)} orders:")
    print()
    for order_id in inserted_orders:
        print(f"  Order #{order_id}")
    print()
    
    # Verify data
    print("Verifying data...")
    try:
        orders = await integration.query_orders()
        print(f"✓ Found {len(orders)} orders in database")
    except Exception as e:
        print(f"Warning: Could not verify data: {e}")


if __name__ == "__main__":
    asyncio.run(populate_database())

