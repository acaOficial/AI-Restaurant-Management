from infrastructure.database.sql_connection import query, execute
from core.domain.order_repository import OrderRepository as IOrderRepository
import json

class SQLOrderRepository(IOrderRepository):

    def insert(self, order) -> None:
        """Insert a new order into the database."""
        execute("""
            INSERT INTO orders (order_id, items, total_price, status, customer_phone, delivery_address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (order.order_id, json.dumps(order.items), order.total_price, order.status, order.customer_phone, order.delivery_address))