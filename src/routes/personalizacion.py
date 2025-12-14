# src/routes/personalizacion.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os

personalizacion_bp = Blueprint('personalizacion_bp', __name__)

@personalizacion_bp.route('/personalizar', methods=['GET', 'POST'])
@login_required 
def personalizar():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        id_producto_str = request.form.get('id_producto') 
        cantidad_str = request.form.get('cantidad', '1') # Por defecto 1

        # 1. Validación y Debug de Entradas
        try:
            id_producto = int(id_producto_str)
            cantidad = int(cantidad_str)
            if cantidad < 1:
                cantidad = 1
        except (ValueError, TypeError):
            flash("❌ El ID de producto o la cantidad son inválidos.", "danger")
            return redirect(url_for('home_bp.home'))

        print(f"\n--- DEBUG PERSONALIZACIÓN ---")
        print(f"Tipo recibido: {tipo}")
        print(f"ID Producto: {id_producto}")
        print(f"Cantidad: {cantidad}")
        print(f"ID Usuario: {current_user.id}") 
        print("-----------------------------\n")

        detalles_personalizacion = "" # Descripción detallada para la tabla 'solicitudes'
        tipo_pers = None              # El tipo de campo a actualizar en 'detalle_pedido'
        valor_pers = None             # El valor (texto o nombre de archivo) a actualizar

        flash_msg = 'Solicitud de personalización procesada.'
        
        # 2. Lógica para manejar el formulario y preparar los datos
        if tipo == 'texto':
            detalles_personalizacion = request.form.get('descripcion')
            tipo_pers = 'texto'
            valor_pers = detalles_personalizacion
            flash_msg = 'Descripción de texto enviada correctamente.'
            
        elif tipo == 'boceto':
            imagen = request.files.get('boceto')
            tipo_pers = 'boceto'
            flash_msg = 'Boceto subido correctamente.'
            
            if imagen and imagen.filename:
                # ... (código previo) ...

                # 🛑 CORRECCIÓN FINAL: Forzar la extracción solo del nombre del archivo
                # Esto maneja casos donde el navegador envía la ruta completa (ej. en Windows)
                # y evita que los 'separadores de ruta' (como \) se guarden en la BD.
                
                # 1. Separar la ruta usando el separador nativo del OS (os.sep)
                partes_ruta = imagen.filename.split(os.sep) 
                
                # 2. Tomar solo la última parte (el nombre del archivo)
                filename_clean = partes_ruta[-1] 
                
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Usar el nombre de archivo limpio para guardar y para la BD
                file_path = os.path.join(upload_folder, filename_clean)
                
                imagen.save(file_path)
                
                # 2.2. Preparación de Variables para BD y Solicitudes
                valor_pers = filename_clean # <--- Guardamos el nombre limpio
                detalles_personalizacion = f"Boceto subido: {filename_clean}"
            else:
                flash("❌ No se recibió un archivo válido para el boceto.", "danger")
                return redirect(request.referrer or url_for('home_bp.home')) # Redirige a donde vino

        # Si hay más tipos de personalización, añádelos aquí
        
        # 3. Llamada Crítica a la Lógica de Base de Datos
        if tipo_pers is None:
            flash("❌ Tipo de personalización no reconocido.", "danger")
            return redirect(request.referrer or url_for('home_bp.home'))

        if agregar_personalizado(id_producto, cantidad, detalles_personalizacion, tipo_pers, valor_pers):
            print("✅ El código 'agregar_personalizado' terminó y devolvió TRUE.")
            flash(flash_msg + " Solicitud de personalización enviada al vendedor.", 'success')
        else:
            print("❌ El código 'agregar_personalizado' terminó y devolvió FALSE.")
            flash("❌ Error al procesar la solicitud de personalización. Consulte el log del servidor.", 'danger')
            
        return redirect(url_for('carrito_bp.ver')) 

    # 4. Manejo de GET (Mostrar el Panel)
    return render_template('personalizacion/panel.html')