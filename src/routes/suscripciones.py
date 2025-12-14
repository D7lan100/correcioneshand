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
            # Mostrar solo 2 tutoriales para suscripción básica
            tutoriales_premium = ModelSuscripcion.obtener_videotutoriales_premium(db, limite=2)
        elif 'premium' in tipo_sub:
            # Mostrar todos los tutoriales para suscripción premium
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
        # Agregar timestamp para evitar nombres duplicados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        path = os.path.join("src/static/comprobantes", filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        archivo.save(path)

        if ModelSuscripcion.crear_suscripcion(db, current_user.id_usuario, id_tipo, filename):
            flash("✅ Comprobante subido correctamente. Tu solicitud está pendiente de aprobación.", "success")
            return redirect(url_for('suscripciones_bp.suscripcion'))
        else:
            flash("❌ Error al procesar la suscripción. Intenta de nuevo.", "danger")

    return render_template('suscripciones/subir_comprobante.html', plan=plan)


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

    # Obtener beneficios según el tipo de suscripción
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