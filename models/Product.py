from db import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    img = db.Column(db.String(255))

    # 🔹 Usa string para evitar import circular
    order_lines = db.relationship("OrderLine", backref="product", lazy=True)

    def __init__(self, name, price, stock=0, img=None):
        self.name = name
        self.price = price
        self.stock = stock
        self.img = img


    def get_id(self):
        return self.id

    def get_name(self):
        return self.name   
    
    def get_price(self):
        return self.price
    
    def get_stock(self):
        return self.stock
    
    def set_stock(self, stock):
        self.stock = stock
    
    def set_price(self, price):
        self.price = price
    
    def set_name(self, name):
        self.name = name

    