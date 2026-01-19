class OrderLine(db.Model):
    __tablename__ = "order_lines"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def get_order_id(self):
        return self.order_id

    def get_product_id(self):
        return self.product_id
    
    def get_quantity(self):
        return self.quantity
    
    def get_price(self):
        return self.price

    def set_quantity(self, quantity):
        self.quantity = quantity
    
    def set_price(self, price):
        self.price = price
    
    def set_order_id(self, order_id):
        self.order_id = order_id
    
    def set_product_id(self, product_id):
        self.product_id = product_id
    
    
