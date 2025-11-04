class Order:
    def __init__(self, order_id: str, items: list, total_price: float, status: str, customer_phone: str, delivery_address: str):
        self.order_id = order_id
        self.items = items
        self.total_price = total_price
        self.status = status
        self.customer_phone = customer_phone
        self.delivery_address = delivery_address