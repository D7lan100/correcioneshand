from app import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = 'pedido'

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='pendiente')
    total = db.Column(db.Float, default=0.0)

    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)
