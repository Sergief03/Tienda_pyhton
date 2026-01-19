from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/tienda_python'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

likes = db.Table(
    'likes',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id')),
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id'))
)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default='cliente')

    likes = db.relationship(
        'Producto',
        secondary=likes,
        backref=db.backref('usuarios', lazy='dynamic')
    )

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(200))
