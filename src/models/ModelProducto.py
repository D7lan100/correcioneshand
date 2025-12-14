# Archivo: src/models/ModelProducto.py
from src.models.entities.Productos import Producto
import math # Importar math para calcular el número total de páginas

# -----------------------------------------------------------------------
# 🛑 CLASE AUXILIAR PARA SIMULAR EL OBJETO DE PAGINACIÓN (PaginationDummy)
# -----------------------------------------------------------------------
class PaginationDummy:
    """
    Clase simple para simular la interfaz de un objeto de paginación
    de Flask-SQLAlchemy (lo que espera tu plantilla Jinja2).
    """
    def __init__(self, items, page, per_page, total):
        self.items = items      # Lista de objetos Producto para la página actual
        self.page = page        # Número de página actual
        self.per_page = per_page# Productos por página
        self.total = total      # Total de productos en la consulta completa
        self.pages = math.ceil(self.total / self.per_page) # Cálculo de páginas

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None

    # Simula iter_pages para los enlaces de paginación en Jinja2
    def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (self.page - left_current <= num <= self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
        
class ModelProducto:

    # ----------------------------------------
    # 🟩 CONSTRUCTOR GENERAL DE PRODUCTOS
    # ----------------------------------------
    @staticmethod
    def _build_producto(row):
        """
        Convierte una fila de BD en un objeto Producto
        ... (Índices de fila sin cambios)
        """

        return Producto(
            id_producto=row[0],
            nombre=row[1],
            descripcion=row[2],
            precio=row[3],
            imagen=row[4],
            id_categoria=row[5],
            id_vendedor=row[6],
            disponible=row[7],
            es_personalizable=row[8],
            calificacion_promedio=row[9],
            nivel_dificultad=row[10],
            duracion=row[11],
            herramientas=row[12],
            instrucciones=row[13],
            tipo_video=row[14],
            url_video=row[15],
            archivo_video=row[16]
        )

    # ----------------------------------------
    # 🔍 Obtener TODOS los productos (CON PAGINACIÓN)
    # ----------------------------------------
    @classmethod
    def get_all(cls, db, page=1, per_page=20):
        try:
            cursor = db.connection.cursor()
            offset = (page - 1) * per_page
            
            # 1. Obtener el total de productos (para calcular páginas)
            cursor.execute("SELECT COUNT(id_producto) FROM productos")
            total_productos = cursor.fetchone()[0]

            # 2. Obtener los productos para la página actual
            sql = f"""
                SELECT id_producto, nombre, descripcion, precio, imagen,
                       id_categoria, id_vendedor, disponible, es_personalizable,
                       calificacion_promedio, nivel_dificultad, duracion,
                       herramientas, instrucciones, tipo_video, url_video, archivo_video
                FROM productos
                ORDER BY id_producto DESC
                LIMIT {per_page} OFFSET {offset}
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            productos_list = [cls._build_producto(row) for row in rows]
            
            # 3. Devolver el objeto de paginación simulado
            return PaginationDummy(productos_list, page, per_page, total_productos)

        except Exception as ex:
            print(f"❌ Error ModelProducto.get_all: {ex}")
            # Devolver un objeto vacío en caso de error
            return PaginationDummy([], page, per_page, 0)


    # ----------------------------------------
    # 🔍 Obtener por ID (sin cambios)
    # ----------------------------------------
    @classmethod
    def get_by_id(cls, db, id_producto):
        try:
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT id_producto, nombre, descripcion, precio, imagen,
                       id_categoria, id_vendedor, disponible, es_personalizable,
                       calificacion_promedio, nivel_dificultad, duracion,
                       herramientas, instrucciones, tipo_video, url_video, archivo_video
                FROM productos
                WHERE id_producto = %s
                LIMIT 1
            """, (id_producto,))
            row = cursor.fetchone()
            cursor.close()

            return cls._build_producto(row) if row else None

        except Exception as ex:
            print(f"❌ Error ModelProducto.get_by_id: {ex}")
            return None


    # ----------------------------------------
    # 🎯 Productos por categoría (CON PAGINACIÓN)
    # ----------------------------------------
    @classmethod
    def get_by_categoria(cls, db, id_categoria, page=1, per_page=20):
        try:
            cursor = db.connection.cursor()
            offset = (page - 1) * per_page

            # 1. Obtener el total de productos en la categoría
            cursor.execute(
                "SELECT COUNT(id_producto) FROM productos WHERE id_categoria = %s", 
                (id_categoria,)
            )
            total_productos = cursor.fetchone()[0]

            # 2. Obtener los productos para la página actual
            sql = f"""
                SELECT id_producto, nombre, descripcion, precio, imagen,
                       id_categoria, id_vendedor, disponible, es_personalizable,
                       calificacion_promedio, nivel_dificultad, duracion,
                       herramientas, instrucciones, tipo_video, url_video, archivo_video
                FROM productos
                WHERE id_categoria = %s
                ORDER BY id_producto DESC
                LIMIT {per_page} OFFSET {offset}
            """
            cursor.execute(sql, (id_categoria,))
            rows = cursor.fetchall()
            cursor.close()

            productos_list = [cls._build_producto(row) for row in rows]
            
            # 3. Devolver el objeto de paginación simulado
            return PaginationDummy(productos_list, page, per_page, total_productos)

        except Exception as ex:
            print(f"❌ Error ModelProducto.get_by_categoria: {ex}")
            return PaginationDummy([], page, per_page, 0)


    # ----------------------------------------
    # 🔍 Buscar productos (CON PAGINACIÓN)
    # ----------------------------------------
    @classmethod
    def search(cls, db, termino, page=1, per_page=20):
        try:
            cursor = db.connection.cursor()
            offset = (page - 1) * per_page
            termino_like = f"%{termino}%"
            
            # 1. Obtener el total de productos que coinciden con la búsqueda
            cursor.execute(
                "SELECT COUNT(id_producto) FROM productos WHERE nombre LIKE %s OR descripcion LIKE %s", 
                (termino_like, termino_like)
            )
            total_productos = cursor.fetchone()[0]

            # 2. Obtener los productos para la página actual
            sql = f"""
                SELECT id_producto, nombre, descripcion, precio, imagen,
                       id_categoria, id_vendedor, disponible, es_personalizable,
                       calificacion_promedio, nivel_dificultad, duracion,
                       herramientas, instrucciones, tipo_video, url_video, archivo_video
                FROM productos
                WHERE nombre LIKE %s OR descripcion LIKE %s
                ORDER BY id_producto DESC
                LIMIT {per_page} OFFSET {offset}
            """
            cursor.execute(sql, (termino_like, termino_like))

            rows = cursor.fetchall()
            cursor.close()

            productos_list = [cls._build_producto(row) for row in rows]
            
            # 3. Devolver el objeto de paginación simulado
            return PaginationDummy(productos_list, page, per_page, total_productos)

        except Exception as ex:
            print(f"❌ Error ModelProducto.search: {ex}")
            return PaginationDummy([], page, per_page, 0)


    # ----------------------------------------
    # 🎥 Productos por vendedor (sin cambios)
    # ----------------------------------------
    @classmethod
    def get_by_usuario(cls, db, id_usuario):
        # ... (código sin cambios)
        try:
            cursor = db.connection.cursor()
            cursor.execute("""
                SELECT id_producto, nombre, descripcion, precio, imagen,
                       id_categoria, id_vendedor, disponible, es_personalizable,
                       calificacion_promedio, nivel_dificultad, duracion,
                       herramientas, instrucciones, tipo_video, url_video, archivo_video
                FROM productos
                WHERE id_vendedor = %s
                ORDER BY id_producto DESC
            """, (id_usuario,))

            rows = cursor.fetchall()
            cursor.close()

            return [cls._build_producto(row) for row in rows]

        except Exception as ex:
            print(f"❌ Error ModelProducto.get_by_usuario: {ex}")
            return []
    
    # ----------------------------------------
    # ⭐ Productos más vendidos (Destacados - sin cambios)
    # ----------------------------------------     
    @classmethod
    def get_mas_vendidos(cls, db, limit=9):
        # ... (código sin cambios)
        try:
            cursor = db.connection.cursor()

            sql = """
                SELECT 
                    p.id_producto, p.nombre, p.descripcion, p.precio, p.imagen,
                    p.id_categoria, p.id_vendedor, p.disponible, p.es_personalizable,
                    p.calificacion_promedio, p.nivel_dificultad, p.duracion,
                    p.herramientas, p.instrucciones, p.tipo_video,
                    p.url_video, p.archivo_video,
                    COUNT(dp.id_producto) AS total_vendidos
                FROM productos p
                LEFT JOIN detalle_pedido dp ON dp.id_producto = p.id_producto
                GROUP BY p.id_producto
                ORDER BY total_vendidos DESC
                LIMIT %s
            """

            cursor.execute(sql, (limit,))
            # Ajustamos el fetchall para ignorar la columna extra de total_vendidos
            rows_with_count = cursor.fetchall()
            cursor.close()

            # Descartar la última columna (total_vendidos) antes de construir el objeto Producto
            return [cls._build_producto(row[:-1]) for row in rows_with_count] 

        except Exception as ex:
            print(f"❌ Error ModelProducto.get_mas_vendidos: {ex}")
            return []