from db import db
from models import Usuario, Product, Order, OrderLine
from werkzeug.security import generate_password_hash

# Crear usuarios de prueba
user2 = Usuario(username="admin", password=generate_password_hash("admin"))
user1 = Usuario(username="sergio", password=generate_password_hash("sergio"))

db.session.add_all([user1, user2])
db.session.commit()

# Crear productos de prueba
product1 = Product(name="Camiseta", price=19.99, stock=50)
product2 = Product(name="Pantalón", price=39.99, stock=30)
product3 = Product(name="Zapatillas", price=59.99, stock=20)

db.session.add_all([product1, product2, product3])
db.session.commit()

# Crear órdenes de prueba
order1 = Order(user_id=user1.id)
order2 = Order(user_id=user2.id)

db.session.add_all([order1, order2])
db.session.commit()

# Crear líneas de orden (OrderLine)
line1 = OrderLine(order_id=order1.id, product_id=product1.id, quantity=2, price=product1.price * 2)
line2 = OrderLine(order_id=order1.id, product_id=product3.id, quantity=1, price=product3.price)
line3 = OrderLine(order_id=order2.id, product_id=product2.id, quantity=3, price=product2.price * 3)

db.session.add_all([line1, line2, line3])
db.session.commit()

print("Datos de prueba insertados correctamente!")
