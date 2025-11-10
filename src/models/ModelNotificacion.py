# src/models/ModelNotificacion.py
from datetime import datetime

class ModelNotificacion:
    @classmethod
    def crear(cls, db, id_usuario, titulo, mensaje):
        """Crea una nueva notificación."""
        try:
            cursor = db.connection.cursor()
            cursor.execute("""
                INSERT INTO notificaciones (id_usuario, titulo, mensaje, fecha_envio)
                VALUES (%s, %s, %s, NOW())
            """, (id_usuario, titulo, mensaje))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            print(f"❌ Error al crear notificación: {ex}")
            return False

    @classmethod
    def obtener_por_usuario(cls, db, id_usuario):
        """Obtiene todas las notificaciones de un usuario."""
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_notificacion, titulo, mensaje, fecha_envio, leida
            FROM notificaciones
            WHERE id_usuario = %s
            ORDER BY fecha_envio DESC
        """, (id_usuario,))
        data = cursor.fetchall()
        cursor.close()
        return data

    @classmethod
    def marcar_como_leida(cls, db, id_notificacion):
        """Marca una notificación como leída."""
        try:
            cursor = db.connection.cursor()
            cursor.execute("UPDATE notificaciones SET leida = TRUE WHERE id_notificacion = %s", (id_notificacion,))
            db.connection.commit()
            cursor.close()
        except Exception as ex:
            db.connection.rollback()
            print(f"⚠ Error al marcar notificación como leída: {ex}")