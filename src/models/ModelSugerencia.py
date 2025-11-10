# src/models/ModelSugerencia.py
from datetime import datetime
import MySQLdb.cursors  # ✅ Necesario para usar DictCursor

class ModelSugerencia:

    # -----------------------------------------------------
    # Crear nueva sugerencia
    # -----------------------------------------------------
    @classmethod
    def crear_sugerencia(cls, db, data):
        try:
            id_usuario = data.get('id_usuario')
            titulo = data.get('titulo', '').strip()
            descripcion = data.get('descripcion', '').strip()

            if not titulo or not descripcion:
                return {"success": False, "message": "Título y descripción son obligatorios."}

            if len(descripcion) > 1500:
                return {"success": False, "message": "La sugerencia supera los 1500 caracteres."}

            palabras_prohibidas = ["tonto", "idiota", "imbecil", "estupido", "grosero"]
            if any(p in descripcion.lower() for p in palabras_prohibidas):
                return {"success": False, "message": "Tu sugerencia contiene lenguaje ofensivo."}

            cursor = db.connection.cursor()
            sql = """
                INSERT INTO sugerencias (id_usuario, titulo, descripcion, fecha_envio, estado, likes, dislikes)
                VALUES (%s, %s, %s, NOW(), 'pendiente', 0, 0)
            """
            cursor.execute(sql, (id_usuario, titulo, descripcion))
            db.connection.commit()
            cursor.close()
            return {"success": True, "message": "Tu sugerencia ha sido enviada exitosamente."}
        except Exception as ex:
            db.connection.rollback()
            return {"success": False, "message": f"Error interno: {ex}"}

    # -----------------------------------------------------
    # Obtener todas las sugerencias (para admin)
    # -----------------------------------------------------
    @classmethod
    def obtener_todas(cls, db):
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = """
            SELECT s.id_sugerencia, s.titulo, s.descripcion, s.fecha_envio, s.estado, s.retroalimentacion,
                   s.likes, s.dislikes, u.nombre_completo AS nombre_usuario
            FROM sugerencias s
            LEFT JOIN usuarios u ON s.id_usuario = u.id_usuario
            ORDER BY s.fecha_envio DESC
        """
        cursor.execute(sql)
        sugerencias = cursor.fetchall()
        cursor.close()
        return sugerencias

    # -----------------------------------------------------
    # Obtener sugerencias pendientes (para dashboard admin)
    # -----------------------------------------------------
    @classmethod
    def obtener_pendientes(cls, db):
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT s.id_sugerencia, s.titulo, s.descripcion, s.fecha_envio, u.nombre_completo AS nombre_usuario
            FROM sugerencias s
            LEFT JOIN usuarios u ON s.id_usuario = u.id_usuario
            WHERE s.estado = 'pendiente'
            ORDER BY s.fecha_envio DESC
        """)
        data = cursor.fetchall()
        cursor.close()
        return data

    # -----------------------------------------------------
    # Cambiar estado de sugerencia (aceptar / rechazar)
    # -----------------------------------------------------
    @classmethod
    def cambiar_estado(cls, db, id_sugerencia, nuevo_estado, retroalimentacion=None):
        try:
            if nuevo_estado not in ['pendiente', 'aceptada', 'rechazada']:
                raise ValueError(f"Estado inválido: {nuevo_estado}")

            cursor = db.connection.cursor()
            sql = """
                UPDATE sugerencias 
                SET estado = %s, retroalimentacion = %s
                WHERE id_sugerencia = %s
            """
            cursor.execute(sql, (nuevo_estado, retroalimentacion, id_sugerencia))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"❌ Error al cambiar estado: {ex}")
            return False

    # -----------------------------------------------------
    # Obtener sugerencias aceptadas (para vista pública)
    # -----------------------------------------------------
    @classmethod
    def obtener_aceptadas(cls, db):
        try:
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = """
                SELECT s.id_sugerencia, s.titulo, s.descripcion, s.fecha_envio, 
                       s.likes, s.dislikes, u.nombre_completo AS autor
                FROM sugerencias s
                LEFT JOIN usuarios u ON s.id_usuario = u.id_usuario
                WHERE s.estado = 'aceptada'
                ORDER BY s.fecha_envio DESC
            """
            cursor.execute(sql)
            sugerencias = cursor.fetchall()
            cursor.close()
            return sugerencias
        except Exception as ex:
            print(f"❌ Error al obtener sugerencias aceptadas: {ex}")
            return []

    # -----------------------------------------------------
    # Contador total (para dashboard)
    # -----------------------------------------------------
    @classmethod
    def contar_total(cls, db):
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM sugerencias")
        total = cursor.fetchone()[0]
        cursor.close()
        return total

    # -----------------------------------------------------
    # Obtener retroalimentaciones de un usuario (para su perfil)
    # -----------------------------------------------------
    @classmethod
    def obtener_por_usuario(cls, db, id_usuario):
        """Obtiene las sugerencias y sus retroalimentaciones del usuario."""
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT id_sugerencia, titulo, descripcion, estado, retroalimentacion, fecha_envio, likes, dislikes
            FROM sugerencias
            WHERE id_usuario = %s
            ORDER BY fecha_envio DESC
        """, (id_usuario,))
        data = cursor.fetchall()
        cursor.close()
        return data

    # -----------------------------------------------------
    # Registrar voto (like o dislike)
    # -----------------------------------------------------
    @classmethod
    def registrar_voto(cls, db, id_sugerencia, id_usuario, tipo_voto):
        """
        Registra un 'like' o 'dislike' del usuario. 
        Evita votos duplicados (un usuario solo puede votar una vez por sugerencia).
        """
        try:
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

            # Verificar si el usuario ya votó esa sugerencia
            cursor.execute("""
                SELECT tipo FROM sugerencias_votos 
                WHERE id_sugerencia = %s AND id_usuario = %s
            """, (id_sugerencia, id_usuario))
            voto_existente = cursor.fetchone()

            if voto_existente:
                return False  # Ya votó antes

            # Insertar nuevo voto
            cursor.execute("""
                INSERT INTO sugerencias_votos (id_sugerencia, id_usuario, tipo, fecha_voto)
                VALUES (%s, %s, %s, NOW())
            """, (id_sugerencia, id_usuario, tipo_voto))

            # Actualizar contador en sugerencias
            if tipo_voto == 'like':
                cursor.execute("""
                    UPDATE sugerencias SET likes = likes + 1 WHERE id_sugerencia = %s
                """, (id_sugerencia,))
            elif tipo_voto == 'dislike':
                cursor.execute("""
                    UPDATE sugerencias SET dislikes = dislikes + 1 WHERE id_sugerencia = %s
                """, (id_sugerencia,))

            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"❌ Error al registrar voto: {ex}")
            return False