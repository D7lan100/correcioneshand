from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from src.models.ModelSuscripcion import ModelSuscripcion

suscripciones_bp = Blueprint('suscripciones_bp', __name__)


# ===============================
# LISTAR PLANES
# ===============================
@suscripciones_bp.route('/')
@login_required
def suscripcion():
    db = current_app.db
    cursor = db.connection.cursor()

    # Obtener planes disponibles
    cursor.execute("SELECT * FROM tipo_suscripcion ORDER BY precio_mensual ASC")
    planes = cursor.fetchall()

    # Obtener suscripción activa del usuario
    suscripcion_actual = ModelSuscripcion.obtener_suscripcion_activa(db, current_user.id_usuario)

    # Obtener historial de suscripciones (con fechas formateadas)
    cursor.execute("""
        SELECT s.id_suscripcion, s.id_usuario, 
               DATE_FORMAT(s.fecha_inicio, '%%d/%%m/%%Y') as fecha_inicio,
               DATE_FORMAT(s.fecha_fin, '%%d/%%m/%%Y') as fecha_fin,
               s.estado, ts.nombre AS tipo_nombre
        FROM suscripciones s
        INNER JOIN tipo_suscripcion ts ON s.id_tipo_suscripcion = ts.id_tipo_suscripcion
        WHERE s.id_usuario = %s
        ORDER BY s.fecha_inicio DESC
    """, (current_user.id_usuario,))
    historial = cursor.fetchall()

    cursor.close()

    # Determinar qué tutoriales mostrar según suscripción
    tutoriales_premium = []
    if suscripcion_actual:
        tipo_sub = suscripcion_actual.get('tipo_nombre', '').lower()
        
        if 'básica' in tipo_sub or 'basica' in tipo_sub:
            tutoriales_premium = ModelSuscripcion.obtener_videotutoriales_premium(db, limite=2)
        elif 'premium' in tipo_sub:
            tutoriales_premium = ModelSuscripcion.obtener_videotutoriales_premium(db, limite=None)

    return render_template(
        'suscripciones/suscripcion.html',
        planes=planes,
        suscripcion_actual=suscripcion_actual,
        historial=historial,
        tutoriales_premium=tutoriales_premium
    )


# ===============================
# SUBIR COMPROBANTE
# ===============================
@suscripciones_bp.route('/subir/<int:id_tipo>', methods=['GET', 'POST'])
@login_required
def subir_comprobante(id_tipo):
    db = current_app.db
    cursor = db.connection.cursor()

    # Verificar si ya tiene suscripción activa
    suscripcion_actual = ModelSuscripcion.obtener_suscripcion_activa(db, current_user.id_usuario)
    if suscripcion_actual:
        flash("Ya tienes una suscripción activa. Si deseas cambiar de plan, usa la opción 'Actualizar Plan'.", "warning")
        return redirect(url_for('suscripciones_bp.suscripcion'))

    cursor.execute("SELECT * FROM tipo_suscripcion WHERE id_tipo_suscripcion = %s", (id_tipo,))
    plan = cursor.fetchone()
    cursor.close()

    if not plan:
        flash("Plan no encontrado", "danger")
        return redirect(url_for('suscripciones_bp.suscripcion'))

    if request.method == 'POST':
        archivo = request.files.get('comprobante')
        if not archivo or archivo.filename == '':
            flash("Debes subir un comprobante.", "danger")
            return redirect(request.url)

        filename = secure_filename(archivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        path = os.path.join("src/static/comprobantes", filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        archivo.save(path)

        if ModelSuscripcion.crear_suscripcion(db, current_user.id_usuario, id_tipo, filename):
            flash("✅ Comprobante subido correctamente. Tu solicitud está pendiente de aprobación.", "success")
            return redirect(url_for('suscripciones_bp.suscripcion'))
        else:
            flash("❌ Error al procesar la suscripción. Intenta de nuevo.", "danger")

    return render_template('suscripciones/subir_comprobante.html', plan=plan)


# ===============================
# ACTUALIZAR PLAN (UPGRADE)
# ===============================
@suscripciones_bp.route('/actualizar-plan/<int:id_tipo>', methods=['GET', 'POST'])
@login_required
def actualizar_plan(id_tipo):
    """Permite al usuario actualizar su plan actual a uno superior"""
    db = current_app.db
    cursor = db.connection.cursor()

    # Verificar suscripción actual
    suscripcion_actual = ModelSuscripcion.obtener_suscripcion_activa(db, current_user.id_usuario)
    if not suscripcion_actual:
        flash("No tienes una suscripción activa para actualizar.", "warning")
        return redirect(url_for('suscripciones_bp.suscripcion'))

    # Obtener información del nuevo plan
    cursor.execute("SELECT * FROM tipo_suscripcion WHERE id_tipo_suscripcion = %s", (id_tipo,))
    nuevo_plan = cursor.fetchone()
    
    if not nuevo_plan:
        flash("Plan no encontrado", "danger")
        cursor.close()
        return redirect(url_for('suscripciones_bp.suscripcion'))

    # Verificar que sea un upgrade (no downgrade)
    if nuevo_plan[3] <= suscripcion_actual['precio_mensual']:
        flash("Solo puedes actualizar a un plan superior.", "warning")
        cursor.close()
        return redirect(url_for('suscripciones_bp.suscripcion'))

    cursor.close()

    if request.method == 'POST':
        archivo = request.files.get('comprobante')
        if not archivo or archivo.filename == '':
            flash("Debes subir el comprobante de pago de la diferencia.", "danger")
            return redirect(request.url)

        filename = secure_filename(archivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"upgrade_{timestamp}_{filename}"
        
        path = os.path.join("src/static/comprobantes", filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        archivo.save(path)

        # Crear solicitud de actualización
        cursor = db.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO suscripciones 
                (id_usuario, id_tipo_suscripcion, fecha_inicio, fecha_fin, 
                 comprobante, estado)
                VALUES (%s, %s, %s, %s, %s, 'pendiente')
            """, (
                current_user.id_usuario, 
                id_tipo, 
                suscripcion_actual['fecha_inicio'],
                suscripcion_actual['fecha_fin'],
                filename
            ))
            db.connection.commit()
            cursor.close()
            
            flash("✅ Solicitud de actualización enviada. Espera la aprobación del administrador.", "success")
            return redirect(url_for('suscripciones_bp.suscripcion'))
        except Exception as e:
            db.connection.rollback()
            cursor.close()
            flash(f"❌ Error al procesar la actualización: {e}", "danger")

    return render_template(
        'suscripciones/actualizar_plan.html', 
        plan_actual=suscripcion_actual,
        nuevo_plan=nuevo_plan
    )


# ===============================
# MI SUSCRIPCIÓN
# ===============================
@suscripciones_bp.route('/mi')
@login_required
def mi_suscripcion():
    db = current_app.db

    suscripcion = ModelSuscripcion.obtener_suscripcion_activa(db, current_user.id_usuario)

    if not suscripcion:
        flash("No tienes suscripción activa.", "info")
        return redirect(url_for('suscripciones_bp.suscripcion'))

    descuento = ModelSuscripcion.obtener_descuento(db, current_user.id_usuario)
    limite_tutoriales = ModelSuscripcion.obtener_limite_tutoriales(db, current_user.id_usuario)
    
    beneficios = {
        'descuento_porcentaje': int(descuento * 100),
        'limite_tutoriales': 'Ilimitado' if limite_tutoriales == 0 else limite_tutoriales,
        'acceso_premium': suscripcion['es_premium']
    }

    return render_template(
        'suscripciones/mi_suscripcion.html',
        suscripcion=suscripcion,
        beneficios=beneficios
    )