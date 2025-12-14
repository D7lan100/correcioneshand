# src/routes/videotutoriales.py
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.ModelProducto import ModelProducto
from src.models.ModelSuscripcion import ModelSuscripcion, suscripcion_requerida, premium_requerido

videotutoriales_bp = Blueprint('videotutoriales_bp', __name__, url_prefix="/videotutoriales")

# ==========================================================
# 📺 LISTA DE VIDEOTUTORIALES (PÁGINA PRINCIPAL)
# ==========================================================
@videotutoriales_bp.route('/')
def lista_videos():
    """Lista todos los videotutoriales (id_categoria = 4)"""
    db = current_app.db
    try:
        videotutoriales = ModelProducto.get_by_categoria(db, 4)
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


# ==========================================================
# ⭐ CALIFICAR UN VIDEO
# ==========================================================
@videotutoriales_bp.route('/calificar/<int:id_video>', methods=['POST'])
@login_required
def calificar_video(id_video):
    puntuacion = request.form.get('puntuacion')
    comentario = request.form.get('comentario')

    if not puntuacion:
        flash("Debes seleccionar una puntuación.", "danger")
        return redirect(url_for('videotutoriales_bp.detalle_video', id_video=id_video))

    db = current_app.db
    cur = db.connection.cursor()

    try:
        cur.execute("""
            SELECT id_calificacion FROM calificaciones
            WHERE id_usuario = %s AND id_producto = %s
        """, (current_user.id_usuario, id_video))
        existe = cur.fetchone()

        if existe:
            cur.execute("""
                UPDATE calificaciones
                SET puntuacion = %s, comentario = %s, fecha_calificacion = NOW()
                WHERE id_calificacion = %s
            """, (puntuacion, comentario, existe[0]))
            mensaje = "Tu calificación ha sido actualizada correctamente."
        else:
            cur.execute("""
                INSERT INTO calificaciones (id_usuario, id_producto, puntuacion, comentario)
                VALUES (%s, %s, %s, %s)
            """, (current_user.id_usuario, id_video, puntuacion, comentario))
            mensaje = "Gracias por calificar este videotutorial."

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
        flash(f"Error al guardar la calificación: {e}", "danger")

    finally:
        cur.close()

    return redirect(url_for('videotutoriales_bp.detalle_video', id_video=id_video))


# ==========================================================
# 🔐 VER VIDEO SEGÚN SUSCRIPCIÓN
# ==========================================================
@videotutoriales_bp.route('/ver/<int:id_video>')
@login_required
def ver_video(id_video):
    db = current_app.db
    cursor = db.connection.cursor()
    
    cursor.execute("""
        SELECT p.*, u.nombre_completo as autor,
               COALESCE(AVG(c.puntuacion), 0) as promedio_calificacion,
               COUNT(c.id_calificacion) as total_calificaciones
        FROM productos p
        LEFT JOIN usuarios u ON p.id_vendedor = u.id_usuario
        LEFT JOIN calificaciones c ON p.id_producto = c.id_producto
        WHERE p.id_producto = %s AND p.id_categoria = 4
        GROUP BY p.id_producto
    """, (id_video,))
    
    video = cursor.fetchone()
    cursor.close()
    
    if not video:
        flash('Video no encontrado', 'danger')
        return redirect(url_for('videotutoriales_bp.lista_videos'))
    
    tipo_video = video[11]

    puede_ver, razon = ModelSuscripcion.puede_ver_tutorial(
        db, current_user.id_usuario, tipo_video
    )
    
    if not puede_ver:
        flash(razon, 'warning')
        return render_template(
            'videotutoriales/acceso_restringido.html',
            video=video,
            razon=razon,
            tipo_video=tipo_video
        )
    
    suscripcion = ModelSuscripcion.obtener_suscripcion_activa(
        db, current_user.id_usuario
    )
    
    return render_template(
        'videotutoriales/ver_video.html',
        video=video,
        suscripcion=suscripcion,
        user=current_user
    )


# ==========================================================
# 📋 LISTA CON INDICADORES DE ACCESO
# (ANTES era lista_videos DUPLICADA)
# ==========================================================
@videotutoriales_bp.route('/lista')
def lista_videos_indicadores():
    """Lista todos los videotutoriales con indicadores de acceso"""
    db = current_app.db
    cursor = db.connection.cursor()
    
    cursor.execute("""
        SELECT p.*, u.nombre_completo as autor,
               COALESCE(AVG(c.puntuacion), 0) as promedio_calificacion
        FROM productos p
        LEFT JOIN usuarios u ON p.id_vendedor = u.id_usuario
        LEFT JOIN calificaciones c ON p.id_producto = c.id_producto
        WHERE p.id_categoria = 4
        GROUP BY p.id_producto
        ORDER BY p.id_producto DESC
    """)
    
    videos = cursor.fetchall()
    cursor.close()
    
    videos_con_acceso = []
    for video in videos:
        tipo_video = video[11]

        info = {
            'datos': video,
            'puede_ver': False,
            'requiere_suscripcion': tipo_video in ['privado', 'premium'],
            'requiere_premium': tipo_video == 'premium',
            'es_publico': tipo_video == 'publico'
        }

        if tipo_video == 'publico':
            info['puede_ver'] = True
        elif current_user.is_authenticated:
            puede_ver, _ = ModelSuscripcion.puede_ver_tutorial(
                db, current_user.id_usuario, tipo_video
            )
            info['puede_ver'] = puede_ver

        videos_con_acceso.append(info)
    
    suscripcion = None
    if current_user.is_authenticated:
        suscripcion = ModelSuscripcion.obtener_suscripcion_activa(
            db, current_user.id_usuario
        )
    
    return render_template(
        'videotutoriales/lista.html',
        videos=videos_con_acceso,
        suscripcion=suscripcion
    )


# ==========================================================
# 🎯 VIDEOS PREMIUM
# ==========================================================
@videotutoriales_bp.route('/premium')
@login_required
@premium_requerido
def videos_premium():
    db = current_app.db
    cursor = db.connection.cursor()
    
    cursor.execute("""
        SELECT p.*, u.nombre_completo as autor,
               COALESCE(AVG(c.puntuacion), 0) as promedio_calificacion
        FROM productos p
        LEFT JOIN usuarios u ON p.id_vendedor = u.id_usuario
        LEFT JOIN calificaciones c ON p.id_producto = c.id_producto
        WHERE p.id_categoria = 4 AND p.tipo_video = 'premium'
        GROUP BY p.id_producto
        ORDER BY p.id_producto DESC
    """)
    
    videos = cursor.fetchall()
    cursor.close()
    
    suscripcion = ModelSuscripcion.obtener_suscripcion_activa(
        db, current_user.id_usuario
    )
    
    return render_template(
        'videotutoriales/premium.html',
        videos=videos,
        suscripcion=suscripcion
    )


# ==========================================================
# 📊 PROGRESO DEL USUARIO
# ==========================================================
@videotutoriales_bp.route('/mi-progreso')
@login_required
@suscripcion_requerida
def mi_progreso():
    db = current_app.db
    
    suscripcion = ModelSuscripcion.obtener_suscripcion_activa(
        db, current_user.id_usuario
    )
    
    limite = ModelSuscripcion.obtener_limite_tutoriales(
        db, current_user.id_usuario
    )
    vistos = ModelSuscripcion.tutoriales_vistos_este_mes(
        db, current_user.id_usuario
    )
    
    estadisticas = {
        'limite': limite if limite else 'Ilimitado',
        'vistos': vistos,
        'restantes': (limite - vistos) if limite else 'Ilimitado'
    }
    
    return render_template(
        'videotutoriales/mi_progreso.html',
        suscripcion=suscripcion,
        estadisticas=estadisticas
    )
