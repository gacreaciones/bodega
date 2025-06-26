from extensions import db 
from flask_login import UserMixin
from datetime import datetime

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    es_admin = db.Column(db.Boolean, default=True)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apodo = db.Column(db.String(50), unique=True, nullable=False)  # Nuevo campo

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Deuda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente_apodo = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')
    productos = db.relationship('ProductoDeuda', backref='deuda', lazy=True)
    cliente = db.relationship('Cliente', backref='deudas')
    
    # Añade esta relación
    pagos_parciales = db.relationship('PagoParcial', backref='deuda', lazy=True)
    
    @property
    def total(self):
        try:
            if not self.productos:
                return 0.0
            return sum(item.subtotal for item in self.productos)
        except (TypeError, ValueError):
            return 0.0

    @property
    def saldo_pendiente(self):
        try:
            pagado = sum(pago.monto_usd for pago in self.pagos_parciales)
            return self.total - pagado
        except (TypeError, ValueError):
            return 0.0
    
    def get_total(self):
        try:
            return round(self.total, 2)
        except (TypeError, ValueError):
            return 0.00
    
    def get_saldo_pendiente(self):
        try:
            return round(self.saldo_pendiente, 2)
        except (TypeError, ValueError):
            return 0.00
    
class PagoParcial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deuda_id = db.Column(db.Integer, db.ForeignKey('deuda.id'), nullable=False)
    monto_usd = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(200))  # Descripción del pago/ajuste

class ProductoDeuda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deuda_id = db.Column(db.Integer, db.ForeignKey('deuda.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    producto = db.relationship('Producto')

    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deuda_id = db.Column(db.Integer, db.ForeignKey('deuda.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    referencia = db.Column(db.String(50), nullable=False)
    banco_origen = db.Column(db.String(50), nullable=False)
    monto_bs = db.Column(db.Float, nullable=False)
    monto_usd = db.Column(db.Float, nullable=False)
    es_parcial = db.Column(db.Boolean, default=False)