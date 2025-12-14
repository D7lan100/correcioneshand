from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .carrito import get_db_cursor 
import json # 🛑 Importar JSON para la plantilla

vendedor_bp = Blueprint('vendedor_bp', __name__, template_folder="../templates/vendedor")

@vendedor_bp.route('/solicitudes')
@login_required
def ver_solicitudes():
    cur = None
    try:
        cur = get_db_cursor() 

        # 🛑 CORRECCIÓN: La consulta ahora selecciona todas las columnas necesarias 
        # de detalle_pedido para que la plantilla las muestre.
        cur.execute("""
            SELECT 
                s.id_solicitud, 
                s.estado AS estado_solicitud,
                s.detalles_adicionales,
                s.feedback_vendedor,
                u.nombre_completo AS nombre_comprador, 
                p.nombre AS nombre_producto, 
                
                dp.id_detalle, 
                dp.cantidad, 
                dp.texto_personalizado, 
                dp.imagen_personalizada, 
                dp.plantilla_seleccionada,  -- Añadido
                dp.formulario_seleccionado, -- Añadido
                dp.precio_total, 
                
                pe.id_pedido 
                
            FROM solicitudes s
            JOIN detalle_pedido dp ON s.id_detalle = dp.id_detalle 
            JOIN pedidos pe ON dp.id_pedido = pe.id_pedido 
            JOIN usuarios u ON s.id_usuario = u.id_usuario 
            JOIN productos p ON s.id_producto = p.id_producto
            
            WHERE s.id_vendedor = %s 
            ORDER BY s.fecha_solicitud DESC
        """, (current_user.id,))
        
        solicitudes = cur.fetchall()

        # Convertir tuplas a diccionarios
        columnas = [col[0] for col in cur.description] 
        solicitudes_dict = [dict(zip(columnas, row)) for row in solicitudes]
        
        # 💡 Procesar JSON de plantilla/formulario para hacerlo legible
        for sol in solicitudes_dict:
            try:
                if sol.get('plantilla_seleccionada'):
                    # Convertir la cadena JSON en un dict de Python
                    sol['plantilla_seleccionada'] = json.loads(sol['plantilla_seleccionada'])
            except json.JSONDecodeError:
                # Si no es JSON válido, dejarlo como texto
                pass
            
            try:
                if sol.get('formulario_seleccionado'):
                    sol['formulario_seleccionado'] = json.loads(sol['formulario_seleccionado'])
            except json.JSONDecodeError:
                pass


        print(f"\n✅ Solicitudes recuperadas exitosamente. Filas: {len(solicitudes_dict)}")
        
        return render_template('vendedor/solicitudes.html', solicitudes=solicitudes_dict)

    except Exception as e:
        print("\n--- ERROR FATAL CAPTURADO EN EL PANEL DE SOLICITUDES ---")
        print(f"Tipo de Error: {type(e)._name_}")
        print(f"Mensaje: {e}")
        print("------------------------------------------------------\n")
        flash(f"Ocurrió un error grave al cargar las solicitudes: {e}", "danger")
        return redirect(url_for('home_bp.home'))
        
    finally:
        if cur:
            cur.close()


@vendedor_bp.route('/responder_solicitud', methods=['POST'])
@login_required
def responder_solicitud():
    db = current_app.db
    cursor = None
    try:
        id_detalle = request.form.get('id_detalle')
        mensaje_vendedor = request.form.get('mensaje_vendedor') 
        precio_propuesto_str = request.form.get('precio_propuesto')
        estado_vendedor = request.form.get('estado_vendedor') 
        
        # 🛑 FIX 1: Reinsertar validación de datos esenciales
        if not id_detalle or not estado_vendedor:
            flash('Error: Faltan datos esenciales para responder.', 'danger')
            return redirect(url_for('vendedor_bp.ver_solicitudes'))

        precio_propuesto = None
        if precio_propuesto_str and precio_propuesto_str.strip(): # Asegurarse que no sea cadena vacía
            try:
                precio_propuesto = float(precio_propuesto_str)
            except ValueError:
                flash('El precio propuesto no es un número válido.', 'danger')
                return redirect(url_for('vendedor_bp.ver_solicitudes'))
        
        cursor = db.connection.cursor()
        
        # 1. ACTUALIZAR EL DETALLE_PEDIDO
        update_fields_detalle = [f"estado_vendedor = '{estado_vendedor}'"]
        params_detalle = []
        
        if precio_propuesto is not None:
             if estado_vendedor == 'cotizado':
                 # 🛑 CORRECCIÓN: Usar 'precio_propuesto' de la BD
                 update_fields_detalle.append("precio_propuesto = %s") 
                 params_detalle.append(precio_propuesto)
             elif estado_vendedor == 'aprobado':
                 update_fields_detalle.append("precio_total = %s") 
                 params_detalle.append(precio_propuesto)
                 
        params_detalle.append(id_detalle)
        
        sql_update_detalle = f"""
            UPDATE detalle_pedido
            SET {', '.join(update_fields_detalle)}
            WHERE id_detalle = %s
        """
        cursor.execute(sql_update_detalle, tuple(params_detalle))
            
        # 2. ACTUALIZAR LA SOLICITUD ASOCIADA
        cursor.execute("""
            UPDATE solicitudes
            SET estado = %s, feedback_vendedor = %s
            WHERE id_detalle = %s
        """, (estado_vendedor, mensaje_vendedor, id_detalle))

        db.connection.commit()
        
        flash(f'Respuesta enviada. El detalle de pedido {id_detalle} ha sido marcado como {estado_vendedor}.', 'success')
        return redirect(url_for('vendedor_bp.ver_solicitudes'))

    except Exception as e:
        if db.connection:
            db.connection.rollback()
        
        print(f"\n❌ 🛑 ERROR FATAL en responder_solicitud: {e} 🛑 ❌\n")
        flash(f'Ocurrió un error al procesar tu respuesta: {e}', 'danger')
        return redirect(url_for('vendedor_bp.ver_solicitudes'))
    finally:
        if cursor:
          cursor.close()