# src/routes/navbar.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from src.models.ModelCalendario import ModelCalendario
from src.models.ModelSugerencia import ModelSugerencia 
from src.models.entities.Calendario import Calendario
from src.models.entities.User import User

navbar_bp = Blueprint('navbar_bp', __name__)

@navbar_bp.route('/perfil/configuracion', endpoint='configuracion_perfil')
@login_required
def configuracion_perfil():
    """Renderiza la configuración del perfil, las sugerencias del usuario y las categorías para subir productos."""
    try:
        sugerencias = ModelSugerencia.obtener_por_usuario(current_app.db, current_user.id)
    except Exception as e:
        sugerencias = []
        flash(f"⚠ Error al obtener sugerencias: {str(e)}", "danger")

    # 🔹 Obtener categorías disponibles (excluyendo 'Tutorial')
    # 🔹 Obtener categorías disponibles (excluyendo 'Tutorial')
    try:
        cur = current_app.db.connection.cursor()
        cur.execute("""
            SELECT id_categoria, nombre
            FROM categorias
            WHERE nombre != 'Tutorial'
            ORDER BY nombre
        """)
        data = cur.fetchall()
        categorias = [{'id_categoria': row[0], 'nombre': row[1]} for row in data]  # 👈 convierte las tuplas a diccionarios
        cur.close()
    except Exception as e:
        categorias = []
        flash(f"⚠ Error al cargar categorías: {str(e)}", "danger")



    # 🔹 Renderizar plantilla con todo lo necesario
    return render_template(
        'usuarios/configuracion.html',
        user=current_user,
        sugerencias=sugerencias,
        categorias=categorias
    )

@navbar_bp.route('/perfil/actualizar', methods=['POST'], endpoint='actualizar_perfil')
@login_required
def actualizar_perfil():
    # Obtenemos los datos del formulario
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    nueva_contra = request.form.get('contraseña')

    try:
        cur = current_app.db.connection.cursor()
        if nueva_contra:
            hash_pw = generate_password_hash(nueva_contra)
            cur.execute("""
                UPDATE usuarios
                SET nombre_completo=%s, correo_electronico=%s, telefono=%s,
                    direccion=%s, contraseña=%s
                WHERE id_usuario=%s
            """, (nombre, correo, telefono, direccion, hash_pw, current_user.id))
        else:
            cur.execute("""
                UPDATE usuarios
                SET nombre_completo=%s, correo_electronico=%s, telefono=%s,
                    direccion=%s
                WHERE id_usuario=%s
            """, (nombre, correo, telefono, direccion, current_user.id))
        current_app.db.connection.commit()
        flash('✅ Perfil actualizado correctamente.', 'success')
    except Exception as e:
        current_app.db.connection.rollback()
        flash(f'❌ Error al actualizar el perfil: {str(e)}', 'danger')
    finally:
        cur.close()

    # Redirigimos al endpoint correcto
    return redirect(url_for('navbar_bp.configuracion_perfil'))

@navbar_bp.route('/donaciones', endpoint='donaciones')
def donaciones():
    return render_template("navbar/donaciones.html")

@navbar_bp.route('/contacto', endpoint='contacto')
def contacto():
    return render_template("navbar/contacto.html")

@navbar_bp.route('/calendario', methods=['GET', 'POST'], endpoint='calendario')
@login_required
def calendario():
    if request.method == "POST":
        nombre = request.form.get("nombre_evento")
        descripcion = request.form.get("descripcion")
        fecha = request.form.get("fecha_evento")

        if not nombre or not fecha:
            flash("El nombre y la fecha del evento son obligatorios.", "danger")
            return redirect(url_for("navbar_bp.calendario"))

        nuevo_evento = Calendario(
            nombre_evento=nombre,
            descripcion=descripcion,
            fecha_evento=fecha,
            id_usuario=current_user.id
        )

        try:
            ModelCalendario.add_event(current_app.db, nuevo_evento)
            flash("Evento agregado correctamente", "success")
        except Exception as e:
            flash(f"Error al agregar el evento: {str(e)}", "danger")

        return redirect(url_for("navbar_bp.calendario"))

    return render_template("navbar/calendario.html")
