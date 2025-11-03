from core.domain.order import Order

class OrderService:
    
    def __init__(self, order_repo, menu_repo=None):

        self.order_repo = order_repo
        self.menu_repo = menu_repo

    def create_order(self, order_id: str, items: list, total_price: float, status: str, customer_phone: str, delivery_address: str):
        order = Order(order_id, items, total_price, status, customer_phone, delivery_address)
        self.order_repo.insert(order)

    def cancel_order():
        pass

    def pay_order():
        pass
