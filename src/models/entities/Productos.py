# Archivo: src/models/entities/Producto.py

class Producto:
    def __init__(self, id_producto, nombre, descripcion, precio, imagen,
                 id_categoria, id_vendedor,
                 disponible=True, es_personalizable=False,
                 calificacion_promedio=None, nivel_dificultad=None,
                 duracion=None, herramientas=None,
                 instrucciones=None, tipo_video=None,
                 url_video=None, archivo_video=None):
        """
        Clase Producto: representa tanto productos físicos como videotutoriales.

        Args:
            id_producto: ID del producto o videotutorial.
            nombre: Nombre del producto o videotutorial.
            descripcion: Descripción.
            precio: Precio (0 si es gratuito).
            imagen: Imagen o portada.
            id_categoria: Categoría (1=Ramo, 2=Carta, 3=Combo, 4=Tutorial, 5=Material).
            id_vendedor: ID del vendedor (si aplica).
            disponible: Si está disponible o visible.
            es_personalizable: Si el producto es personalizable (no aplica a videos).
            calificacion_promedio: Promedio de calificaciones.
            instrucciones: Instrucciones del videotutorial.
            tipo_video: Tipo de acceso (público, privado, premium).
            url_video: Enlace a YouTube.
            archivo_video: Archivo de video local.
            nivel_dificultad: Nivel de dificultad (básico, intermedio, avanzado).
            duracion: Duración del videotutorial.
            herramientas: Herramientas o materiales requeridos.
        """
        self.id_producto = id_producto
        self.id = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.imagen = imagen
        self.id_categoria = id_categoria
        self.id_vendedor = id_vendedor
        self.disponible = disponible
        self.es_personalizable = es_personalizable
        self.calificacion_promedio = calificacion_promedio
        self.nivel_dificultad = nivel_dificultad
        self.duracion = duracion
        self.herramientas = herramientas
        self.instrucciones = instrucciones
        self.tipo_video = tipo_video
        self.url_video = url_video
        self.archivo_video = archivo_video

    def __repr__(self):
        return f"<Producto id={self.id_producto}, nombre={self.nombre}>"

    def __str__(self):
        return self.nombre

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'imagen': self.imagen,
            'id_categoria': self.id_categoria,
            'id_vendedor': self.id_vendedor,
            'disponible': self.disponible,
            'es_personalizable': self.es_personalizable,
            'calificacion_promedio': self.calificacion_promedio,
            'instrucciones': self.instrucciones,
            'tipo_video': self.tipo_video,
            'url_video': self.url_video,
            'archivo_video': self.archivo_video,
            'nivel_dificultad': self.nivel_dificultad,
            'duracion': self.duracion,
            'herramientas': self.herramientas
        }

    def get_precio_formateado(self):
        return f"${self.precio:,.2f}"

    def esta_disponible(self):
        return bool(self.disponible)
