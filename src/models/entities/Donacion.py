class Donaciones:
    """Clase entidad para donaciones"""
    
    def _init_(self, id_usuario, monto, metodo_pago, datos_pago, estado):
        self.id_usuario = id_usuario
        self.monto = monto
        self.metodo_pago = metodo_pago
        self.datos_pago = datos_pago
        self.estado = estado