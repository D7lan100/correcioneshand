from datetime import datetime

class ModelEstadisticas:

    @classmethod
    def total_ingresos(cls, db):
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT SUM(precio_total) AS total
            FROM detalle_pedido
        """)
        result = cursor.fetchone()
        cursor.close()
        return result["total"] or 0

    @classmethod
    def total_pedidos(cls, db):
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM pedidos")
        result = cursor.fetchone()
        cursor.close()
        return result["total"] or 0
    
    @classmethod
    def total_usuarios(cls, db):
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
        result = cursor.fetchone()
        cursor.close()
        return result["total"] or 0

    @classmethod
    def ingresos_por_mes(cls, db):
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT 
                MONTH(p.fecha_pedido) AS mes,
                SUM(dp.precio_total) AS ingresos
            FROM detalle_pedido dp
            INNER JOIN pedidos p ON dp.id_pedido = p.id_pedido
            GROUP BY MONTH(p.fecha_pedido)
            ORDER BY mes
        """)
        rows = cursor.fetchall()
        cursor.close()

        datos = [0] * 12
        for r in rows:
            datos[r["mes"] - 1] = float(r["ingresos"])
        return datos
