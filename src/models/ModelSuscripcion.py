from datetime import datetime

class ModelSuscripcion:

    # 📋 Listar todas las suscripciones con información de usuario y tipo
    @classmethod
    def listar_suscripciones(cls, db):
        try:
            cursor = db.connection.cursor(dictionary=True)
            sql = """
                SELECT 
                    s.id_suscripcion,
                    u.nombre_completo AS nombre_usuario,
                    ts.nombre_tipo AS tipo_suscripcion,
                    s.fecha_inicio,
                    s.fecha_fin,
                    s.comprobante,
                    s.estado
                FROM suscripciones s
                INNER JOIN usuarios u ON s.id_usuario = u.id_usuario
                INNER JOIN tipos_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
                ORDER BY s.fecha_inicio DESC
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as ex:
            raise Exception(f"Error al listar suscripciones: {ex}")

    # 📤 Actualizar comprobante de una suscripción
    @classmethod
    def actualizar_comprobante(cls, db, id_suscripcion, filename):
        try:
            cursor = db.connection.cursor()
            sql = "UPDATE suscripciones SET comprobante = %s, estado = 'Pendiente' WHERE id_suscripcion = %s"
            cursor.execute(sql, (filename, id_suscripcion))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(f"Error al actualizar comprobante: {ex}")

    # ✅ Cambiar estado de una suscripción (Aprobada / Rechazada)
    @classmethod
    def cambiar_estado(cls, db, id_suscripcion, nuevo_estado):
        try:
            cursor = db.connection.cursor()
            sql = "UPDATE suscripciones SET estado = %s WHERE id_suscripcion = %s"
            cursor.execute(sql, (nuevo_estado, id_suscripcion))
            db.connection.commit()
            cursor.close()
            return True
        except Exception as ex:
            db.connection.rollback()
            raise Exception(f"Error al cambiar estado: {ex}")

    # 💰 Calcular ingresos del mes (solo de suscripciones aprobadas)
    @classmethod
    def ingresos_mes(cls, db):
        try:
            cursor = db.connection.cursor(dictionary=True)
            sql = """
                SELECT IFNULL(SUM(ts.precio), 0) AS ingresos
                FROM suscripciones s
                INNER JOIN tipos_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
                WHERE s.estado = 'Aprobada'
                AND MONTH(s.fecha_inicio) = MONTH(CURDATE())
                AND YEAR(s.fecha_inicio) = YEAR(CURDATE())
            """
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            return result['ingresos'] if result else 0
        except Exception as ex:
            raise Exception(f"Error al obtener ingresos del mes: {ex}")

    # 🕒 Obtener suscripciones recientes (últimos 30 días)
    @classmethod
    def recientes(cls, db):
        try:
            cursor = db.connection.cursor(dictionary=True)
            sql = """
                SELECT 
                    u.nombre_completo AS usuario,
                    ts.nombre_tipo AS tipo,
                    s.fecha_inicio,
                    s.estado
                FROM suscripciones s
                INNER JOIN usuarios u ON s.id_usuario = u.id_usuario
                INNER JOIN tipos_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
                WHERE s.fecha_inicio >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                ORDER BY s.fecha_inicio DESC
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as ex:
            raise Exception(f"Error al obtener suscripciones recientes: {ex}")
