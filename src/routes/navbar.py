# src/routes/navbar.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from src.models.ModelCalendario import ModelCalendario
from src.models.ModelSugerencia import ModelSugerencia 
from src.models.entities.Calendario import Calendario
from src.models.entities.User import User
from src.database.db import get_connection

navbar_bp = Blueprint('navbar_bp', __name__)

@navbar_bp.route('/perfil/actualizar', methods=['POST'], endpoint='actualizar_perfil')
@login_required
def actualizar_perfil():
    """Actualiza los datos del perfil del usuario logueado."""
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    nueva_contra = request.form.get('nueva_contraseña')
    confirmar_contra = request.form.get('confirmar_contraseña')

    # ✅ Validar coincidencia de contraseñas
    if nueva_contra and nueva_contra != confirmar_contra:
        flash('❌ Las contraseñas no coinciden. Intenta nuevamente.', 'danger')
        return redirect(url_for('navbar_bp.configuracion_perfil'))

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

    return redirect(url_for('usuarios_bp.configuracion'))


@navbar_bp.route('/donaciones', endpoint='donaciones')
def donaciones():
    return render_template("navbar/donaciones.html")

# ============================================================
# 🔄 CONTACTO - CON FAQs CARGADAS DIRECTAMENTE
# ============================================================
@navbar_bp.route('/contacto', endpoint='contacto')
def contacto():
    """Carga la página de contacto con las FAQs"""
    print("\n" + "="*60)
    print("🔍 NAVBAR: Cargando página de contacto")
    print("="*60)
    
    try:
        db = get_connection()
        cursor = db.cursor()
        
        print("\n📝 Ejecutando consulta de FAQs...")
        
        sql_query = """
            SELECT 
            asunto, 
            mensaje, 
            respuesta
            FROM pqr
            WHERE es_pregunta = 1
            AND visible_faq = 1
            AND respuesta IS NOT NULL
            AND CHAR_LENGTH(TRIM(respuesta)) > 0
            AND asunto <> '0'
            AND mensaje <> '0'
            AND respuesta <> '0'
            ORDER BY fecha DESC
        """

        
        cursor.execute(sql_query)
        faq = cursor.fetchall()
        
        print(f"✅ FAQs encontradas: {len(faq)}")
        
        if len(faq) > 0:
            print("\n📋 Lista de FAQs:")
        for idx, item in enumerate(faq, 1):
            try:
                print(f"{idx}. {item[0]}")
            except Exception:
                print(f"{idx}. [ERROR EN REGISTRO] →", item)
        
        print("="*60 + "\n")

        cursor.close()
        db.close()

        return render_template("contacto.html", faq=faq)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return render_template("contacto.html", faq=[])

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
