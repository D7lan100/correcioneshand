# src/routes/videotutoriales.py
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.ModelProducto import ModelProducto

videotutoriales_bp = Blueprint('videotutoriales_bp', __name__, url_prefix="/videotutoriales")

# ==========================================================
# 📺 LISTA DE VIDEOTUTORIALES
# ==========================================================
@videotutoriales_bp.route('/')
def lista_videos():
    """Lista todos los videotutoriales (id_categoria = 4)"""
    db = current_app.db
    try:
        videotutoriales = ModelProducto.get_by_categoria(db, 4)  # Usa el modelo
        return render_template('videotutoriales/videotutoriales.html', videotutoriales=videotutoriales)
    except Exception as e:
        return render_template('videotutoriales/videotutoriales.html', error=f"Error al cargar los videotutoriales: {e}")

# ==========================================================
# 🎥 DETALLE DE UN VIDEOTUTORIAL
# ==========================================================
@videotutoriales_bp.route('/detalle/<int:id_video>')
def detalle_video(id_video):
    """Muestra el detalle de un videotutorial individual"""
    db = current_app.db
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.descripcion, p.precio, p.imagen,
                p.id_categoria, p.id_vendedor,
                p.instrucciones, p.tipo_video, p.url_video, p.archivo_video,
                p.calificacion_promedio, p.nivel_dificultad, p.duracion, p.herramientas,
                u.nombre_completo
            FROM productos p
            LEFT JOIN usuarios u ON p.id_vendedor = u.id_usuario
            WHERE p.id_producto = %s AND p.id_categoria = 4
        """, (id_video,))
        row = cursor.fetchone()

        cursor.execute("""
            SELECT c.puntuacion, c.comentario, c.fecha_calificacion, u.nombre_completo
            FROM calificaciones c
            LEFT JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE c.id_producto = %s
            ORDER BY c.fecha_calificacion DESC
        """, (id_video,))
        comentarios = [
            {
                'puntuacion': r[0],
                'comentario': r[1],
                'fecha_calificacion': r[2].strftime("%d-%m-%Y %H:%M"),
                'nombre_usuario': r[3] or "Anónimo"
            } for r in cursor.fetchall()
        ]
        cursor.close()

        if not row:
            return render_template("videotutoriales/videotutorial_detalle.html", error="Videotutorial no encontrado")

        # Mapeo al formato que espera tu plantilla actual (usa 'video')
        video = {
            'id_producto': row[0],
            'nombre': row[1],
            'descripcion': row[2],
            'precio': row[3],
            'imagen': row[4],
            'id_categoria': row[5],
            'id_vendedor': row[6],
            'instrucciones': row[7],
            'tipo_video': row[8],
            'url_video': row[9],
            'archivo_video': row[10],
            'calificacion_promedio': row[11],
            'nivel_dificultad': row[12],
            'duracion': row[13],
            'herramientas': row[14],
            'nombre_usuario': row[15] or "Administrador",
            'comentarios': comentarios
        }
        
        return render_template("videotutoriales/videotutorial_detalle.html", video=video)

    except Exception as e:
        return render_template(
            "videotutoriales/videotutorial_detalle.html",
            video=None,
            error=f"Error al cargar el videotutorial: {e}"
        )


@videotutoriales_bp.route('/calificar/<int:id_video>', methods=['POST'])
@login_required
def calificar_video(id_video):
    """Permite que un usuario califique un videotutorial"""
    puntuacion = request.form.get('puntuacion')
    comentario = request.form.get('comentario')

    if not puntuacion:
        flash("Debes seleccionar una puntuación.", "danger")
        return redirect(url_for('videotutoriales_bp.detalle_video', id_video=id_video))

    db = current_app.db
    cur = db.connection.cursor()

    try:
        # Verificar si el usuario ya calificó este video
        cur.execute("""
            SELECT id_calificacion FROM calificaciones
            WHERE id_usuario = %s AND id_producto = %s
        """, (current_user.id_usuario, id_video))
        existe = cur.fetchone()

        if existe:
            # Si ya calificó, actualiza su calificación
            cur.execute("""
                UPDATE calificaciones
                SET puntuacion = %s, comentario = %s, fecha_calificacion = NOW()
                WHERE id_calificacion = %s
            """, (puntuacion, comentario, existe[0]))
            mensaje = "Tu calificación ha sido actualizada correctamente. ⭐"
        else:
            # Si no existe, inserta una nueva
            cur.execute("""
                INSERT INTO calificaciones (id_usuario, id_producto, puntuacion, comentario)
                VALUES (%s, %s, %s, %s)
            """, (current_user.id_usuario, id_video, puntuacion, comentario))
            mensaje = "¡Gracias por calificar este videotutorial! 💫"

        # ✅ Recalcular el promedio inmediatamente después
        cur.execute("""
            UPDATE productos
            SET calificacion_promedio = (
                SELECT ROUND(AVG(puntuacion), 2)
                FROM calificaciones
                WHERE id_producto = %s
            )
            WHERE id_producto = %s
        """, (id_video, id_video))

        db.connection.commit()
        flash(mensaje, "success")

    except Exception as e:
        db.connection.rollback()
        flash(f"❌ Error al guardar la calificación: {e}", "danger")

    finally:
        cur.close()

    return redirect(url_for('videotutoriales_bp.detalle_video', id_video=id_video))

