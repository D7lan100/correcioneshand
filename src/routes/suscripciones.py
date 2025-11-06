from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from src.models.ModelSuscripcion import ModelSuscripcion
from src.models.entities.Suscripcion import Suscripcion
from datetime import date, timedelta
import os

suscripciones_bp = Blueprint('suscripciones_bp', __name__, url_prefix='/suscripciones')


# 🟢 Listar los planes disponibles
@suscripciones_bp.route('/')
@login_required
def listar_planes():
    cursor = current_app.db.connection.cursor()
    cursor.execute("""
        SELECT id_tipo_suscripcion, nombre, descripcion, precio_mensual
        FROM tipo_suscripcion
    """)
    planes = cursor.fetchall()
    cursor.close()
    return render_template('suscripciones/suscripciones.html', planes=planes)


# 🟡 Subir comprobante y crear la suscripción
@suscripciones_bp.route('/pago/<int:id_tipo>', methods=['GET', 'POST'])
@login_required
def subir_comprobante(id_tipo):
    if request.method == 'POST':
        file = request.files.get('comprobante')
        if not file or file.filename.strip() == '':
            flash('⚠️ Debes subir un comprobante de pago.', 'danger')
            return redirect(request.url)

        # Crear carpeta si no existe
        upload_folder = os.path.join('src', 'static', 'comprobantes')
        os.makedirs(upload_folder, exist_ok=True)

        # Guardar el archivo
        filename = f"user_{current_user.id_usuario}_{file.filename}"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Crear la entidad de suscripción
        suscripcion = Suscripcion(
            id_usuario=current_user.id_usuario,
            id_tipo_suscripcion=id_tipo,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            comprobante=filename,
            estado='pendiente'
        )

        # Guardar en la base de datos
        resultado = ModelSuscripcion.insert(current_app.db, suscripcion)

        if resultado:
            flash('📤 Comprobante enviado correctamente. Espera la validación del administrador.', 'success')
        else:
            flash('❌ Error al guardar la suscripción. Inténtalo de nuevo.', 'danger')

        return redirect(url_for('suscripciones_bp.ver_suscripcion'))

    # Si es método GET, mostrar el formulario
    cursor = current_app.db.connection.cursor()
    cursor.execute("SELECT * FROM tipo_suscripcion WHERE id_tipo_suscripcion = %s", (id_tipo,))
    plan = cursor.fetchone()
    cursor.close()

    if not plan:
        flash('El plan seleccionado no existe.', 'danger')
        return redirect(url_for('suscripciones_bp.listar_planes'))

    return render_template('suscripciones/subir_comprobante.html', plan=plan)


# 🔵 Ver la suscripción del usuario
@suscripciones_bp.route('/mi-suscripcion')
@login_required
def ver_suscripcion():
    # Validar y actualizar suscripciones vencidas
    ModelSuscripcion.validar_vencidas(current_app.db)

    # Obtener la última suscripción del usuario
    suscripcion = ModelSuscripcion.get_last_by_user(current_app.db, current_user.id_usuario)
    if not suscripcion:
        flash('Aún no tienes una suscripción activa.', 'info')
        return redirect(url_for('suscripciones_bp.listar_planes'))

    # Determinar estado visual
    estado_mostrar = "Desconocido"
    if suscripcion.estado == "aprobada" and suscripcion.fecha_inicio <= date.today() <= suscripcion.fecha_fin:
        estado_mostrar = "Activa"
    elif suscripcion.estado == "aprobada" and date.today() > suscripcion.fecha_fin:
        estado_mostrar = "Expirada"
    elif suscripcion.estado:
        estado_mostrar = suscripcion.estado.capitalize()

    # Obtener detalles del plan
    cursor = current_app.db.connection.cursor()
    cursor.execute("SELECT nombre, precio_mensual FROM tipo_suscripcion WHERE id_tipo_suscripcion = %s",
                   (suscripcion.id_tipo_suscripcion,))
    plan = cursor.fetchone()
    cursor.close()

    return render_template('suscripciones/mi_suscripcion.html',
                           suscripcion=suscripcion,
                           plan=plan,
                           estado=estado_mostrar)
