# src/routes/fabricacion.py

from flask import Blueprint, render_template
from src.models.ModelProducto import ModelProducto

fabricacion_bp = Blueprint('fabricacion_bp', __name__, url_prefix="/fabricacion")

@fabricacion_bp.route('/')
def mostrar_fabricacion():
    db = current_app.db
    try:
        cursor = db.connection.cursor()
        sql = """
        SELECT p.id_producto, p.nombre, p.descripcion, p.precio, p.imagen,
               p.id_usuario, p.disponible, p.es_personalizable,
               c.nombre AS nombre_categoria
        FROM productos p
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        WHERE p.id_usuario IS NOT NULL AND p.disponible = 1
        ORDER BY p.id_producto DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()

        videotutoriales = []
        for row in rows:
            videotutoriales.append({
                'id_producto': row[0],
                'nombre': row[1],
                'descripcion': row[2],
                'precio': float(row[3]),
                'imagen': row[4],
                'id_usuario': row[5],
                'es_personalizable': row[7],
                'categoria': row[8]  # ✅ Aquí tienes el nombre de la categoría
            })

        return render_template('fabricacion.html', videotutoriales=videotutoriales)

    except Exception as e:
        print(f"Error al cargar sección de fabricación: {e}")
        return render_template('fabricacion.html', videotutoriales=[], error=str(e))