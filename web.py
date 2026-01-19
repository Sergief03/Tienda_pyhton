from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from db import db
from models.User import Usuario
from models.Product import Product
from models.Order import Order
from models.OrderLine import OrderLine


app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/tienda_python'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔹 Inicializar SQLAlchemy con la app
db.init_app(app)

# -------------------
# FUNCIONES AUXILIARES
# -------------------

def usuario_actual():
    if 'user' in session:
        return Usuario.query.get(session['user'])
    return None

def login_requerido():
    return usuario_actual() is not None

def admin_requerido():
    usuario = usuario_actual()
    return usuario and 'admin' in usuario.roles

def obtener_producto(id):
    return Product.query.get(id)

# -------------------
# RUTAS PRINCIPALES
# -------------------

@app.route('/')
def index():
    q = request.args.get('q', '')
    if q:
        productos = Product.query.filter(Product.name.ilike(f'%{q}%')).all()
    else:
        productos = Product.query.all()
    return render_template('index.html', productos=productos, usuario=usuario_actual())

@app.route('/productos/<int:id>')
def detalle_producto(id):
    producto = obtener_producto(id)
    if not producto:
        return "Producto no encontrado", 404
    return render_template('detalle_producto.html', producto=producto, usuario=usuario_actual())

# -------------------
# CRUD PRODUCTOS (SOLO ADMIN)
# -------------------

@app.route('/productos/nuevo')
def nuevo_producto():
    if not admin_requerido():
        return redirect(url_for('index'))
    return render_template('form_add.html', usuario=usuario_actual())

@app.route('/productos/agregar', methods=['POST'])
def agregar_producto():
    if not admin_requerido():
        return redirect(url_for('index'))

    archivo = request.files.get('imagen')
    filename = None
    if archivo and archivo.filename:
        filename = secure_filename(archivo.filename)
        os.makedirs('static/uploads', exist_ok=True)
        archivo.save(os.path.join('static/uploads', filename))

    try:
        nuevo = Product(
            name=request.form['nombre'],
            price=float(request.form['precio']),
            stock=int(request.form['stock'])
        )
        if filename:
            nuevo.img = filename
        db.session.add(nuevo)
        db.session.commit()
    except ValueError:
        return "Datos inválidos", 400

    return redirect(url_for('index'))

@app.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
def editar_producto(id):
    if not admin_requerido():
        return redirect(url_for('index'))
    producto = obtener_producto(id)
    if not producto:
        return "Producto no encontrado", 404

    if request.method == 'POST':
        try:
            producto.name = request.form['nombre']
            producto.price = float(request.form['precio'])
            producto.stock = int(request.form['stock'])
            db.session.commit()
        except ValueError:
            return "Datos inválidos", 400
        return redirect(url_for('detalle_producto', id=id))

    return render_template('form_edit.html', producto=producto, usuario=usuario_actual())

@app.route('/productos/<int:id>/eliminar', methods=['POST'])
def eliminar_producto(id):
    if not admin_requerido():
        return redirect(url_for('index'))
    producto = obtener_producto(id)
    if not producto:
        return "Producto no encontrado", 404
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('index'))

# -------------------
# USUARIOS / AUTENTICACIÓN
# -------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.id
            return redirect(url_for('index'))
        return "Credenciales inválidas", 401
    return render_template('login.html', usuario=usuario_actual())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        nuevo = Usuario(username=username, password=password, roles=['cliente'])
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', usuario=usuario_actual())

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ------------------- # CARRITO DE LA SESIÓN (LÓGICA COMPLETA) # -------------------
@app.route('/carrito') 
def ver_carrito(): 
    if not login_requerido(): 
        return redirect(url_for('login')) 
    
    carrito = session.get('carrito', {}) 
    productos_en_carrito = [] 
    total = 0 
    
    for producto_id, quantity in carrito.items(): 
        producto = obtener_producto(int(producto_id)) 
        if producto: 
            subtotal = producto.price * quantity 
            total += subtotal 
            productos_en_carrito.append({ 'producto': producto, 'cantidad': quantity, 'subtotal': subtotal }) 
    # Si no tienes 'carrito.html', asegúrate de crearlo. 
    # Por ahora lo redirijo a una plantilla de carrito.
    return render_template( 'carrito.html', productos_carrito=productos_en_carrito, total=total, usuario=usuario_actual() ) 

@app.route('/carrito/agregar/<int:producto_id>', methods=['POST']) 
def agregar_al_carrito(producto_id): 
    if not login_requerido(): 
        return redirect(url_for('login')) 
        
    producto = obtener_producto(producto_id) 
    if not producto: 
        return "Producto no encontrado", 404 
        
    # Obtener el carrito actual o crear uno vacío 
    carrito = session.get('carrito', {}) 
    # Añadir o incrementar cantidad 
    id_str = str(producto_id) 
    if id_str in carrito: 
        carrito[id_str] += 1 
    else: carrito[id_str] = 1 
    
    session['carrito'] = carrito 
    session.modified = True # Importante para que Flask detecte cambios en dicts 
    
    return redirect(request.referrer or url_for('index')) 
@app.route('/carrito/quitar/<int:producto_id>', methods=['POST']) 
def quitar_del_carrito(producto_id): 
    if not login_requerido(): 
        return redirect(url_for('login')) 
    carrito = session.get('carrito', {}) 
    id_str = str(producto_id) 
    if id_str in carrito: 
        carrito.pop(id_str) 
        session['carrito'] = carrito 
        session.modified = True 
    return redirect(url_for('ver_carrito')) 

@app.route('/carrito/vaciar', methods=['POST']) 
def vaciar_carrito(): 
    if not login_requerido(): 
        return redirect(url_for('login')) 
    session.pop('carrito', None) 
    return redirect(url_for('ver_carrito'))

# -------------------
# ARRANQUE DE LA APP
# -------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 🔹 Crear tablas si no existen
    app.run(debug=True)
