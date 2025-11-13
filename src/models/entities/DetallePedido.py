from app import db

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)

    cantidad = db.Column(db.Integer, default=1)
    precio_total = db.Column(db.Float, nullable=False)

    texto_personalizado = db.Column(db.String(255), nullable=True)
    plantilla_seleccionada = db.Column(db.String(255), nullable=True)
    imagen_personalizada = db.Column(db.String(255), nullable=True)
    formulario_seleccionado = db.Column(db.String(255), nullable=True)
