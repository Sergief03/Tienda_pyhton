from app_test import app, db, Usuario, Producto
from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

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
    return usuario and usuario.rol == 'admin'

def obtener_producto(id):
    return Producto.query.get(id)

# -------------------
# RUTAS PRINCIPALES
# -------------------

@app.route('/')
def index():
    q = request.args.get('q', '')

    if q:
        productos = Producto.query.filter(
            Producto.nombre.ilike(f'%{q}%')
        ).all()
    else:
        productos = Producto.query.all()

    return render_template(
        'index.html', 
        productos=productos,
        usuario=usuario_actual()
    )

@app.route('/productos/<int:id>')
def detalle_producto(id):
    producto = obtener_producto(id)
    if not producto:
        return "Producto no encontrado", 404

    return render_template(
        'detalle_producto.html',
        producto=producto,
        usuario=usuario_actual()
    )

# -------------------
# CRUD PRODUCTOS (SOLO ADMIN)
# -------------------

@app.route('/productos/nuevo')
def nuevo_producto():
    if not admin_requerido():
        return redirect(url_for('index'))

    return render_template(
        'form_add.html',
        usuario=usuario_actual()
    )

@app.route('/productos/agregar', methods=['POST'])
def agregar_producto():
    if not admin_requerido():
        return redirect(url_for('index'))

    archivo = request.files.get('imagen')
    filename = None

    if archivo and archivo.filename:
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join('static/uploads', filename))

    try:
        nuevo = Producto(
            nombre=request.form['nombre'],
            precio=float(request.form['precio']),
            stock=request.form['stock'],
            img=filename
        )
        db.session.add(nuevo)
        db.session.commit()
    except ValueError:
        return "Datos inválidos", 400

    return redirect(url_for('index'))

@app.route('/productos/<int:id>/editar')
def editar_producto(id):
    if not admin_requerido():
        return redirect(url_for('index'))

    producto = obtener_producto(id)
    if not producto:
        return "Producto no encontrado", 404

    return render_template(
        'form_edit.html',
        producto=producto,
        usuario=usuario_actual()
    )

@app.route('/productos/<int:id>/editar', methods=['POST'])
def actualizar_producto(id):
    if not admin_requerido():
        return redirect(url_for('index'))

    producto = obtener_producto(id)
    if not producto:
        return "Producto no encontrado", 404

    try:
        producto.nombre = request.form['nombre']
        producto.precio = float(request.form['precio'])
        producto.stock = request.form['stock']
        db.session.commit()
    except ValueError:
        return "Datos inválidos", 400

    return redirect(url_for('detalle_producto', id=id))

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

        if user and check_password_hash(user.contrasena, password):
            session['user'] = user.id
            return redirect(url_for('index'))

        return "Credenciales inválidas", 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        nuevo = Usuario(
            username=username,
            contrasena=password,
            rol='cliente'
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('carrito', None) # Opcional: limpiar carrito al salir
    return redirect(url_for('login'))

# -------------------
# CARRITO DE LA SESIÓN (LÓGICA COMPLETA)
# -------------------

@app.route('/carrito')
def ver_carrito():
    if not login_requerido():
        return redirect(url_for('login'))

    carrito = session.get('carrito', {})
    productos_en_carrito = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = obtener_producto(int(producto_id))
        if producto:
            subtotal = producto.precio * cantidad
            total += subtotal
            productos_en_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })

    # Si no tienes 'carrito.html', asegúrate de crearlo. 
    # Por ahora lo redirijo a una plantilla de carrito.
    return render_template(
        'carrito.html', 
        productos_carrito=productos_en_carrito,
        total=total,
        usuario=usuario_actual()
    )

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
    else:
        carrito[id_str] = 1

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
        db.create_all()
    app.run(debug=True)