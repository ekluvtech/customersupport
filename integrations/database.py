"""Database Integration"""

import logging
from typing import Dict, Any, Optional, List
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

#export DATABASE_URL="postgresql://ordr_user1:Admin123@localhost/ordr_mgmnt"


# create database ordr_mgmnt;

# create role ordr_user1 with LOGIN password 'Admin123';

# grant connect on
# database ordr_mgmnt to ordr_user1;

# alter default privileges in schema public grant
# select
# 	,
# 	insert
# 	,
# 	update
# 	,
# 	delete
# 	on
# 	tables to ordr_user1;

class DatabaseIntegration:
    """Integration with order database"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv("DATABASE_URL")
        if self.connection_string:
            self.engine = create_engine(
                self.connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10
            )
        else:
            self.engine = None
            logger.warning("No database connection string provided")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a database tool"""
        if parameters is None:
            parameters = {}
        
        if tool_name == "query_orders":
            return await self.query_orders(
                parameters.get("order_id"),
                parameters.get("customer_email"),
                parameters.get("status")
            )
        elif tool_name == "get_order_details":
            order_id = parameters.get("order_id")
            if not order_id:
                # Provide helpful error message with available parameters
                received_params = list(parameters.keys()) if parameters else []
                error_msg = (
                    f"get_order_details requires 'order_id' parameter. "
                    f"Received parameters: {received_params}. "
                    f"Please provide 'order_id' as a string."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            return await self.get_order_details(order_id)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def query_orders(
        self,
        order_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query orders from the database"""
        print(f"Querying orders from the database with connection string: {self.connection_string}")
        if not self.engine:
            raise ValueError(
                "Database not configured. Please set DATABASE_URL environment variable "
                "or provide connection_string parameter. "
                "Example: postgresql://user:password@localhost/dbname"
            )
        
        try:
            # Build query (this is a placeholder - adapt to your schema)
            query = "SELECT * FROM orders WHERE 1=1"
            params = {}
            
            if order_id:
                query += " AND order_id = :order_id"
                params["order_id"] = order_id
            
            if customer_email:
                query += " AND customer_email = :customer_email"
                params["customer_email"] = customer_email
            
            if status:
                query += " AND status = :status"
                params["status"] = status
            
            query += " LIMIT 100"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                rows = result.fetchall()
                
                # Convert to list of dicts, handling JSONB and other complex types
                columns = result.keys()
                orders = []
                for row in rows:
                    order_dict = {}
                    for col, val in zip(columns, row):
                        # Handle JSONB columns (already parsed by psycopg2)
                        if val is None:
                            order_dict[col] = None
                        elif isinstance(val, (dict, list)):
                            # Already a Python dict/list from JSONB
                            order_dict[col] = val
                        elif hasattr(val, 'isoformat'):  # datetime/date objects
                            order_dict[col] = val.isoformat()
                        else:
                            order_dict[col] = val
                    orders.append(order_dict)
                #print(f"orders: {orders}")
                return orders
        
        except Exception as e:
            logger.error(f"Error querying orders: {e}")
            raise
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get detailed order information"""
        orders = await self.query_orders(order_id=order_id)
        if not orders:
            raise ValueError(f"Order {order_id} not found")
        return orders[0]

