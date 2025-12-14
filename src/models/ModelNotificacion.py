# src/models/ModelNotificacion.py
from datetime import datetime

class ModelNotificacion:
    # -----------------------------
    # Crear notificación
    # -----------------------------
    @classmethod
    def crear(cls, db, id_usuario, titulo, mensaje):
        """Crea una nueva notificación en la base de datos."""
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

    # Alias para mantener compatibilidad con admin.py
    @classmethod
    def crear_notificacion(cls, db, id_usuario, mensaje, titulo="Notificación del sistema"):
        """Alias compatible con admin.py"""
        return cls.crear(db, id_usuario, titulo, mensaje)

    # -----------------------------
    # Obtener notificaciones de un usuario
    # -----------------------------
    @classmethod
    def obtener_por_usuario(cls, db, id_usuario):
        """Obtiene todas las notificaciones de un usuario ordenadas por fecha."""
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

    # -----------------------------
    # Obtener solo no leídas
    # -----------------------------
    @classmethod
    def obtener_no_leidas(cls, db, id_usuario):
        """Obtiene solo las notificaciones no leídas de un usuario."""
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_notificacion, titulo, mensaje, fecha_envio
            FROM notificaciones
            WHERE id_usuario = %s AND leida = FALSE
            ORDER BY fecha_envio DESC
        """, (id_usuario,))
        data = cursor.fetchall()
        cursor.close()
        return data

    # -----------------------------
    # Marcar como leída
    # -----------------------------
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