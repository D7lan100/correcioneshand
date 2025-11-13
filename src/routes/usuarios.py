from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from src.models.ModelProducto import ModelProducto
from src.database.db import get_connection

# ======================================================
# 📁 BLUEPRINT USUARIOS
# ======================================================
usuarios_bp = Blueprint('usuarios_bp', __name__, url_prefix="/usuarios")

# ======================================================
# 👤 PERFIL DE USUARIO
# ======================================================
@usuarios_bp.route('/perfil')
@login_required
def perfil():
    return render_template('usuarios/perfil.html', user=current_user)


# ======================================================
# ⚙️ CONFIGURACIÓN DEL USUARIO
# ======================================================
@usuarios_bp.route('/perfil/configuracion')
@login_required
def configuracion():
    db = current_app.db
    try:
        cursor = db.connection.cursor()

        # 🔹 Categorías
        cursor.execute("""
            SELECT id_categoria, nombre 
            FROM categorias 
            WHERE nombre != 'Tutorial' 
            ORDER BY nombre
        """)
        categorias_raw = cursor.fetchall()
        categorias = [{'id_categoria': c[0], 'nombre': c[1]} for c in categorias_raw]

        # 🔹 Productos del usuario
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.descripcion, p.precio, p.imagen,
                   p.disponible, p.es_personalizable, c.nombre AS categoria
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.id_vendedor = %s
            ORDER BY p.id_producto DESC
        """, (current_user.id_usuario,))
        productos_raw = cursor.fetchall()
        productos = [{
            'id_producto': p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'precio': float(p[3]),
            'imagen': p[4],
            'disponible': p[5],
            'es_personalizable': p[6],
            'categoria': p[7]
        } for p in productos_raw]

        # 🔹 Sugerencias del usuario (si el modelo existe)
        try:
            from src.models.ModelSugerencia import ModelSugerencia
            sugerencias_usuario = ModelSugerencia.obtener_por_usuario(db, current_user.id_usuario)
        except Exception as e:
            print(f"⚠️ No se pudieron cargar sugerencias: {e}")
            sugerencias_usuario = []

        cursor.close()

        return render_template(
            'usuarios/configuracion.html',
            categorias=categorias,
            productos_usuario=productos,
            sugerencias_usuario=sugerencias_usuario,
            user=current_user
        )

    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        flash(f"Error al cargar tu configuración: {e}", "danger")
        return render_template(
            'usuarios/configuracion.html',
            categorias=[],
            productos_usuario=[],
            sugerencias_usuario=[],
            user=current_user
        )


# ======================================================
# 🎬 PANEL DE VIDEOTUTORIALES DEL USUARIO
# ======================================================
@usuarios_bp.route('/mis_videos')
@login_required
def mis_videos():
    db = current_app.db
    cur = db.connection.cursor()

    cur.execute("""
        SELECT id_producto, nombre, descripcion, imagen, url_video, archivo_video, tipo_video, nivel_dificultad
        FROM productos
        WHERE id_vendedor = %s AND id_categoria = 4
        ORDER BY id_producto DESC
    """, (current_user.id_usuario,))
    videos = cur.fetchall()
    cur.close()

    return render_template('usuarios/mis_videos.html', videos=videos)


# ======================================================
# 📂 CONFIGURACIÓN DE ARCHIVOS
# ======================================================
UPLOAD_FOLDER_VIDEOS = 'src/static/videotutoriales_usuarios'
UPLOAD_FOLDER_IMAGENES = 'src/static/img'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# ======================================================
# 🎥 SUBIR VIDEOTUTORIAL
# ======================================================
@usuarios_bp.route('/subir_video', methods=['POST'])
@login_required
def subir_video():
    db = current_app.db
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    tipo_video = request.form.get('tipo')
    url_video = request.form.get('url')
    archivo = request.files.get('archivo')
    imagen = request.files.get('imagen')

    ruta_imagen = None
    if imagen and allowed_image(imagen.filename):
        os.makedirs(UPLOAD_FOLDER_IMAGENES, exist_ok=True)
        nombre_imagen = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{imagen.filename}")
        ruta_guardado_imagen = os.path.join(UPLOAD_FOLDER_IMAGENES, nombre_imagen)
        imagen.save(ruta_guardado_imagen)
        ruta_imagen = f"/static/img/{nombre_imagen}"

    nivel_dificultad = request.form.get('nivel_dificultad')
    duracion = request.form.get('duracion')
    herramientas = request.form.get('herramientas')
    instrucciones = request.form.get('instrucciones')

    if not titulo or not descripcion:
        flash("El título y la descripción son obligatorios.", "danger")
        return redirect(url_for('usuarios_bp.configuracion'))

    archivo_video = None
    if archivo and allowed_file(archivo.filename):
        os.makedirs(UPLOAD_FOLDER_VIDEOS, exist_ok=True)
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}")
        ruta_guardado = os.path.join(UPLOAD_FOLDER_VIDEOS, filename)
        archivo.save(ruta_guardado)
        archivo_video = filename
    elif not url_video:
        flash("Debes subir un archivo o proporcionar una URL válida.", "danger")
        return redirect(url_for('usuarios_bp.configuracion'))

    try:
        cur = db.connection.cursor()
        sql = """
            INSERT INTO productos (
                nombre, descripcion, instrucciones, tipo_video,
                nivel_dificultad, duracion, herramientas,
                precio, imagen, url_video, archivo_video,
                id_categoria, id_vendedor, disponible, es_personalizable
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s,
                    0, %s, %s, %s,
                    4, %s, 1, 0)
        """
        cur.execute(sql, (
            titulo, descripcion, instrucciones, tipo_video,
            nivel_dificultad, duracion, herramientas,
            ruta_imagen, url_video, archivo_video,
            current_user.id_usuario
        ))
        db.connection.commit()
        cur.close()
        flash("🎬 Tu videotutorial fue subido correctamente y está visible en el catálogo.", "success")
    except Exception as e:
        flash(f"Error al subir el videotutorial: {e}", "danger")

    return redirect(url_for('usuarios_bp.configuracion'))


# ======================================================
# 🛍️ SUBIR PRODUCTOS
# ======================================================
@usuarios_bp.route('/subir_producto', methods=['POST'])
@login_required
def subir_producto():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    id_categoria = request.form.get('id_categoria')
    disponible = True if request.form.get('disponible') else False
    es_personalizable = True if request.form.get('es_personalizable') else False
    imagen = request.files.get('imagen')

    if not id_categoria:
        flash("Debes seleccionar una categoría.", "danger")
        return redirect(url_for('usuarios_bp.configuracion'))

    id_categoria = int(id_categoria)
    if id_categoria == 4:
        flash("No puedes seleccionar la categoría de Videotutoriales.", "danger")
        return redirect(url_for('usuarios_bp.configuracion'))

    ruta_imagen = None
    if imagen and imagen.filename != '':
        os.makedirs(UPLOAD_FOLDER_IMAGENES, exist_ok=True)
        filename = secure_filename(imagen.filename)
        ruta_guardado = os.path.join(UPLOAD_FOLDER_IMAGENES, filename)
        imagen.save(ruta_guardado)
        ruta_imagen = f"/static/img/{filename}"

    try:
        db = current_app.db
        cur = db.connection.cursor()
        cur.execute("""
            INSERT INTO productos (nombre, descripcion, precio, id_categoria, id_vendedor, disponible, es_personalizable, imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, id_categoria, current_user.id_usuario, disponible, es_personalizable, ruta_imagen))
        db.connection.commit()
        cur.close()
        flash("✅ Producto subido exitosamente.", "success")
    except Exception as e:
        flash(f"❌ Error al subir el producto: {e}", "danger")

    return redirect(url_for('usuarios_bp.configuracion'))


# ======================================================
# ✏️ EDITAR PRODUCTO
# ======================================================
@usuarios_bp.route('/editar_producto/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def editar_producto(id_producto):
    db = current_app.db
    cur = db.connection.cursor()

    if request.method == 'GET':
        cur.execute("SELECT * FROM productos WHERE id_producto = %s AND id_vendedor = %s", 
                    (id_producto, current_user.id_usuario))
        producto = cur.fetchone()
        cur.close()
        if not producto:
            flash("No tienes permiso para editar este producto.", "danger")
            return redirect(url_for('usuarios_bp.configuracion'))
        return render_template('usuarios/editar_producto.html', producto=producto)

    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    id_categoria = request.form.get('id_categoria')
    disponible = 1 if request.form.get('disponible') else 0
    es_personalizable = 1 if request.form.get('es_personalizable') else 0
    imagen = request.files.get('imagen')

    if not nombre or not descripcion or not precio or not id_categoria:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('usuarios_bp.configuracion'))

    ruta_imagen = None
    if imagen and imagen.filename:
        nombre_imagen = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{imagen.filename}")
        ruta_guardado = os.path.join('src/static/img', nombre_imagen)
        imagen.save(ruta_guardado)
        ruta_imagen = f"/static/img/{nombre_imagen}"

    try:
        if ruta_imagen:
            cur.execute("""
                UPDATE productos 
                SET nombre=%s, descripcion=%s, precio=%s, id_categoria=%s, disponible=%s, es_personalizable=%s, imagen=%s
                WHERE id_producto=%s AND id_vendedor=%s
            """, (nombre, descripcion, precio, id_categoria, disponible, es_personalizable, ruta_imagen, id_producto, current_user.id_usuario))
        else:
            cur.execute("""
                UPDATE productos 
                SET nombre=%s, descripcion=%s, precio=%s, id_categoria=%s, disponible=%s, es_personalizable=%s
                WHERE id_producto=%s AND id_vendedor=%s
            """, (nombre, descripcion, precio, id_categoria, disponible, es_personalizable, id_producto, current_user.id_usuario))
        db.connection.commit()
        cur.close()
        flash("✅ Producto actualizado correctamente.", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"❌ Error al actualizar producto: {e}", "danger")

    return redirect(url_for('usuarios_bp.configuracion'))


# ======================================================
# 🗑️ ELIMINAR VIDEOTUTORIAL
# ======================================================
@usuarios_bp.route('/eliminar_video/<int:id_video>', methods=['POST', 'GET'])
@login_required
def eliminar_video(id_video):
    db = current_app.db
    cur = db.connection.cursor()
    try:
        cur.execute("DELETE FROM calificaciones WHERE id_producto = %s", (id_video,))
        cur.execute("""
            DELETE FROM productos
            WHERE id_producto = %s AND id_vendedor = %s AND id_categoria = 4
        """, (id_video, current_user.id_usuario))
        db.connection.commit()
        flash("🗑️ Videotutorial eliminado correctamente.", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"❌ Error al eliminar el videotutorial: {e}", "danger")
    finally:
        cur.close()
    return redirect(url_for('usuarios_bp.mis_videos'))


# ======================================================
# ✏️ EDITAR VIDEOTUTORIAL
# ======================================================
@usuarios_bp.route('/editar_video/<int:id_video>', methods=['GET', 'POST'])
@login_required
def editar_video(id_video):
    db = current_app.db
    cur = db.connection.cursor()
    cur.execute("""
        SELECT id_producto, nombre, descripcion, tipo_video, nivel_dificultad, duracion, 
               herramientas, instrucciones, imagen, url_video, archivo_video
        FROM productos 
        WHERE id_producto = %s AND id_vendedor = %s
    """, (id_video, current_user.id_usuario))
    video = cur.fetchone()
    cur.close()

    if not video:
        flash("❌ No se encontró el videotutorial o no tienes permiso para editarlo.", "danger")
        return redirect(url_for('usuarios_bp.configuracion'))

    if request.method == 'GET':
        return render_template("usuarios/editar_video.html", video=video)

    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    tipo_video = request.form.get('tipo_video')
    nivel_dificultad = request.form.get('nivel_dificultad')
    duracion = request.form.get('duracion')
    herramientas = request.form.get('herramientas')
    instrucciones = request.form.get('instrucciones')
    url_video = request.form.get('url_video')
    imagen = request.files.get('imagen')
    archivo = request.files.get('archivo')

    try:
        ruta_imagen = video[8]
        if imagen and imagen.filename:
            nombre_imagen = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{imagen.filename}")
            ruta_guardado_imagen = os.path.join('src/static/img', nombre_imagen)
            imagen.save(ruta_guardado_imagen)
            ruta_imagen = f"/static/img/{nombre_imagen}"

        archivo_video = video[10]
        if archivo and archivo.filename:
            nombre_video = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}")
            ruta_guardado = os.path.join('src/static/videotutoriales_usuarios', nombre_video)
            archivo.save(ruta_guardado)
            archivo_video = nombre_video

        cur = db.connection.cursor()
        cur.execute("""
            UPDATE productos
            SET nombre=%s, descripcion=%s, tipo_video=%s, nivel_dificultad=%s, 
                duracion=%s, herramientas=%s, instrucciones=%s, imagen=%s, 
                url_video=%s, archivo_video=%s
            WHERE id_producto = %s AND id_vendedor = %s
        """, (titulo, descripcion, tipo_video, nivel_dificultad, duracion, 
              herramientas, instrucciones, ruta_imagen, url_video, archivo_video,
              id_video, current_user.id_usuario))
        db.connection.commit()
        cur.close()
        flash("✅ Videotutorial actualizado correctamente.", "success")
        return redirect(url_for('usuarios_bp.mis_videos'))

    except Exception as e:
        db.connection.rollback()
        flash(f"❌ Error al actualizar el videotutorial: {e}", "danger")
        return redirect(url_for('usuarios_bp.mis_videos'))
