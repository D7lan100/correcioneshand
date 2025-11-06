class Suscripcion:
    def __init__(self, id_suscripcion=None, id_usuario=None, id_tipo_suscripcion=None,
                 fecha_inicio=None, fecha_fin=None, comprobante=None, estado=None):
        self.id_suscripcion = id_suscripcion
        self.id_usuario = id_usuario
        self.id_tipo_suscripcion = id_tipo_suscripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.comprobante = comprobante
        self.estado = estado

    def to_tuple(self):
        return (
            self.id_usuario,
            self.id_tipo_suscripcion,
            self.fecha_inicio,
            self.fecha_fin,
            self.comprobante,
            self.estado
        )
