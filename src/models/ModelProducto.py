# Archivo: src/models/ModelProducto.py

from src.models.entities.Productos import Producto

class ModelProducto:

    # ============================================================
    # Obtener todos los productos
    # ============================================================
    @classmethod
    def get_all(cls, db):
        """Obtiene todos los productos y videotutoriales"""
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id_producto, nombre, descripcion, precio, imagen, 
                            id_categoria, id_vendedor, disponible, 
                            es_personalizable, calificacion_promedio,
                            nivel_dificultad, duracion, herramientas, instrucciones,
                            tipo_video, url_video, archivo_video
                    FROM productos
                    ORDER BY nombre"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            productos = []
            for row in rows:
                if row[15] is None:  # tipo_video == None → producto normal
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        precio=row[3],
                        imagen=row[4],
                        id_categoria=row[5],
                        id_vendedor=row[6],
                        disponible=row[7],
                        es_personalizable=row[8],
                        calificacion_promedio=row[9]
                    )
                else:  # es un videotutorial
                    producto = Producto(
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
                productos.append(producto)
            return productos

        except Exception as ex:
            print(f"Error en get_all: {ex}")
            raise Exception(f"Error al obtener productos: {ex}")
        
    # ============================================================
    # Obtener productos destacados (para carrusel del index)
    # ============================================================
    @classmethod
    def obtener_mas_populares(cls, db, limit=9):
        """Obtiene los productos más destacados o populares"""
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id_producto, nombre, descripcion, precio, imagen, 
                            id_categoria, id_vendedor, disponible, 
                            es_personalizable, calificacion_promedio,
                            nivel_dificultad, duracion, herramientas, instrucciones,
                            tipo_video, url_video, archivo_video
                    FROM productos
                    WHERE disponible = 1 AND imagen IS NOT NULL
                    ORDER BY calificacion_promedio DESC, nombre ASC
                    LIMIT %s"""
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            cursor.close()

            productos = []
            for row in rows:
                producto = Producto(
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
                productos.append(producto)
            return productos

        except Exception as ex:
            print(f"Error en obtener_mas_populares: {ex}")
            return []

    # ============================================================
    # Obtener producto por ID
    # ============================================================
    @classmethod
    def get_by_id(cls, db, id_producto):
        """Obtiene un producto o videotutorial por su ID"""
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id_producto, nombre, descripcion, precio, imagen, 
                            id_categoria, id_vendedor, disponible, 
                            es_personalizable, calificacion_promedio,
                            nivel_dificultad, duracion, herramientas, instrucciones,
                            tipo_video, url_video, archivo_video
                    FROM productos
                    WHERE id_producto = %s
                    LIMIT 1"""
            id_producto = int(id_producto)
            cursor.execute(sql, (id_producto,))
            row = cursor.fetchone()
            cursor.close()

            if not row:
                return None

            # ✅ Detecta si es un producto normal o un videotutorial
            if row[15] is None:
                producto = Producto(
                    id_producto=row[0],
                    nombre=row[1],
                    descripcion=row[2],
                    precio=row[3],
                    imagen=row[4],
                    id_categoria=row[5],
                    id_vendedor=row[6],
                    disponible=row[7],
                    es_personalizable=row[8],
                    calificacion_promedio=row[9]
                )
            else:
                producto = Producto(
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

            return producto

        except Exception as ex:
            print(f"Error en get_by_id: {ex}")
            raise Exception(f"Error al obtener producto {id_producto}: {ex}")

    # ============================================================
    # Obtener productos por categoría
    # ============================================================
    @classmethod
    def get_by_categoria(cls, db, id_categoria):
        """Obtiene productos o videotutoriales filtrados por categoría"""
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id_producto, nombre, descripcion, precio, imagen, 
                            id_categoria, id_vendedor, disponible, 
                            es_personalizable, calificacion_promedio,
                            nivel_dificultad, duracion, herramientas, instrucciones,
                            tipo_video, url_video, archivo_video
                    FROM productos
                    ORDER BY nombre"""
            cursor.execute(sql, (id_categoria,))
            rows = cursor.fetchall()
            cursor.close()

            productos = []
            for row in rows:
                if row[15] is None:  # tipo_video == None → producto normal
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        precio=row[3],
                        imagen=row[4],
                        id_categoria=row[5],
                        id_vendedor=row[6],
                        disponible=row[7],
                        es_personalizable=row[8],
                        calificacion_promedio=row[9]
                    )
                else:  # es un videotutorial
                    producto = Producto(
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
                producto.nombre_usuario = row[7] or "Administrador"
                productos.append(producto)
            return productos

        except Exception as ex:
            print(f"Error en get_by_categoria: {ex}")
            raise Exception(f"Error al obtener productos de categoría {id_categoria}: {ex}")

    # ============================================================
    # Buscar productos
    # ============================================================
    @classmethod
    def search(cls, db, termino):
        """Busca productos o videotutoriales por nombre o descripción"""
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id_producto, nombre, descripcion, precio, imagen, 
                            id_categoria, id_vendedor, disponible, 
                            es_personalizable, calificacion_promedio,
                            nivel_dificultad, duracion, herramientas, instrucciones,
                            tipo_video, url_video, archivo_video
                    FROM productos
                    ORDER BY nombre"""
            termino_busqueda = f"%{termino}%"
            cursor.execute(sql, (termino_busqueda, termino_busqueda))
            rows = cursor.fetchall()
            cursor.close()

            productos = []
            for row in rows:
                if row[15] is None:  # tipo_video == None → producto normal
                    producto = Producto(
                        id_producto=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        precio=row[3],
                        imagen=row[4],
                        id_categoria=row[5],
                        id_vendedor=row[6],
                        disponible=row[7],
                        es_personalizable=row[8],
                        calificacion_promedio=row[9]
                    )
                else:  # es un videotutorial
                    producto = Producto(
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
                productos.append(producto)
            return productos

        except Exception as ex:
            print(f"Error en search: {ex}")
            raise Exception(f"Error al buscar productos: {ex}")

    # ============================================================
    # Crear un videotutorial
    # ============================================================
    @classmethod
    def create_video_tutorial(cls, db, nombre, descripcion, instrucciones, tipo_video, url_video, archivo_video, id_vendedor, es_personalizable=True):
        """Crea un nuevo videotutorial"""
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO productos
                     (nombre, descripcion, precio, imagen, id_categoria, id_vendedor,
                      disponible, es_personalizable, instrucciones, tipo_video,
                      url_video, archivo_video)
                     VALUES (%s, %s, %s, %s, 4, %s, 1, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                nombre, descripcion, 0.00, None, id_vendedor, es_personalizable,
                instrucciones, tipo_video, url_video, archivo_video
            ))
            db.connection.commit()
            cursor.close()
            return True

        except Exception as ex:
            print(f"Error al crear videotutorial: {ex}")
            db.connection.rollback()
            return False

    # ============================================================
    # Actualizar stock o disponibilidad
    # ============================================================
    @classmethod
    def update_stock(cls, db, id_producto, nuevo_stock):
        try:
            cursor = db.connection.cursor()
            cursor.execute("UPDATE productos SET disponible = %s WHERE id_producto = %s", (nuevo_stock, id_producto))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            print(f"Error al actualizar stock: {ex}")
            return False

    # ============================================================
    # Actualizar un producto o videotutorial
    # ============================================================
    @classmethod
    def update(cls, db, id_producto, nombre, descripcion, disponible, es_personalizable, id_categoria, imagen, instrucciones=None, tipo_video=None, url_video=None):
        try:
            cursor = db.connection.cursor()
            sql = """UPDATE productos
                     SET nombre=%s, descripcion=%s, disponible=%s, es_personalizable=%s,
                         id_categoria=%s, imagen=%s, instrucciones=%s, tipo_video=%s, url_video=%s
                     WHERE id_producto=%s"""
            cursor.execute(sql, (
                nombre, descripcion, disponible, es_personalizable, id_categoria,
                imagen, instrucciones, tipo_video, url_video, id_producto
            ))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            print(f"Error al actualizar producto: {ex}")
            db.connection.rollback()
            return False

    # ============================================================
    # Eliminar un producto o videotutorial
    # ============================================================
    @staticmethod
    def delete(db, id_producto):
        try:
            cursor = db.connection.cursor()
            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
            db.connection.commit()
            filas = cursor.rowcount
            cursor.close()
            return filas > 0
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            return False