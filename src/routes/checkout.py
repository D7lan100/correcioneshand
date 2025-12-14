# src/routes/checkout.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from flask import session, flash
from src.models.ModelSuscripcion import ModelSuscripcion
import json

checkout_bp = Blueprint('checkout_bp', __name__)

def get_db_cursor():
    db = current_app.db
    return db.connection.cursor()

# ---------------------------------------------------------
# 1. VISTA PREVIA DEL RESUMEN DE PAGO
# ---------------------------------------------------------
@checkout_bp.route('/resumen', methods=['GET'])
@login_required
def resumen_pago():
    db = current_app.db
    cursor = db.connection.cursor()
    id_usuario = current_user.id_usuario

    try:
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_usuario = %s AND estado = 'pendiente' LIMIT 1", (id_usuario,))
        pedido = cursor.fetchone()

        if not pedido:
            flash("No tienes un pedido activo para pagar.", "warning")
            return redirect(url_for('carrito_bp.ver'))

        id_pedido_carrito = pedido[0]

        query_items = """
            SELECT 
                dp.id_detalle, p.nombre, p.precio, dp.cantidad, 
                dp.precio_total, dp.precio_propuesto, dp.aceptado_usuario,
                p.imagen, dp.estado_vendedor
            FROM detalle_pedido dp
            JOIN productos p ON dp.id_producto = p.id_producto
            WHERE dp.id_pedido = %s
            AND (
                (dp.estado_vendedor = 'aprobado' OR dp.estado_vendedor IS NULL)
                OR (dp.estado_vendedor = 'cotizado' AND dp.aceptado_usuario = 1)
            )
        """
        cursor.execute(query_items, (id_pedido_carrito,))
        items_raw = cursor.fetchall()

        if not items_raw:
            flash("No tienes productos listos para pagar.", "info")
            return redirect(url_for('carrito_bp.ver'))

        items_pago = []
        total_a_pagar = 0.0

        for row in items_raw:
            precio_final = float(row[4])
            total_a_pagar += precio_final
            
            items_pago.append({
                'id_detalle': row[0],
                'nombre': row[1],
                'cantidad': row[3],
                'precio_total': precio_final,
                'imagen_producto': row[7],
                'estado_vendedor': row[8]
            })

        return render_template('checkout/pago.html', items=items_pago, total=total_a_pagar)

    except Exception as e:
        print("Error en resumen de pago:", e)
        flash("Error al cargar el resumen de pago.", "danger")
        return redirect(url_for('carrito_bp.ver'))
    finally:
        cursor.close()


# ---------------------------------------------------------
# 2. PROCESAR PAGO + GUARDAR JSON DEL PAGO
# ---------------------------------------------------------
@checkout_bp.route('/procesar', methods=['POST'])
@login_required
def procesar_pago():
    db = current_app.db
    cursor = db.connection.cursor()
    id_usuario = current_user.id_usuario

    direccion = request.form.get('direccion')
    ciudad = request.form.get('ciudad')
    telefono = request.form.get('telefono')
    metodo_pago = request.form.get('metodo_pago')

    # Aquí recibimos el JSON serializado desde el front (campo oculto "detalles_pago")
    detalles_pago_raw = request.form.get('detalles_pago')

    if not direccion or not ciudad or not telefono or not metodo_pago:
        flash("Completa los datos de envío.", "danger")
        return redirect(url_for('checkout_bp.resumen_pago'))

    if not detalles_pago_raw:
        flash("No se recibieron los detalles del pago.", "danger")
        return redirect(url_for('checkout_bp.resumen_pago'))

    # Intentar parsear el JSON
    try:
        detalles_pago = json.loads(detalles_pago_raw)
    except Exception as e:
        print("Error parseando JSON de detalles_pago:", e)
        flash("Error en los datos de pago (JSON inválido).", "danger")
        return redirect(url_for('checkout_bp.resumen_pago'))

    # Validaciones básicas dependientes del método (puedes ampliar)
    if metodo_pago == "Tarjeta Crédito/Débito":
        # Aceptamos que front ya envió titular, numero, exp, cvc
        tar = detalles_pago.get('datos') or detalles_pago  # soporta dos formas
        if not tar.get('numero') or not tar.get('exp') or not tar.get('cvc'):
            flash("Completa los datos de la tarjeta.", "danger")
            return redirect(url_for('checkout_bp.resumen_pago'))

    if metodo_pago == "PSE":
        pse = detalles_pago.get('datos') or detalles_pago
        if not pse.get('banco') or not pse.get('identificacion'):
            flash("Completa los datos de PSE.", "danger")
            return redirect(url_for('checkout_bp.resumen_pago'))

    if metodo_pago == "PayPal":
        pp = detalles_pago.get('datos') or detalles_pago
        if not pp.get('email'):
            flash("Completa el correo de PayPal.", "danger")
            return redirect(url_for('checkout_bp.resumen_pago'))

    try:
        # 1) Obtener el pedido original (carrito/pending)
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_usuario = %s AND estado = 'pendiente' LIMIT 1", (id_usuario,))
        pedido_carrito = cursor.fetchone()

        if not pedido_carrito:
            flash("No existe un pedido pendiente.", "warning")
            return redirect(url_for('home_bp.home'))

        id_pedido_original = pedido_carrito[0]

        # 2) Identificar detalles que se van a pagar (los aprobados o cotizados y aceptados)
        cursor.execute("""
            SELECT id_detalle, precio_total FROM detalle_pedido 
            WHERE id_pedido = %s 
            AND (
                (estado_vendedor = 'aprobado' OR estado_vendedor IS NULL)
                OR (estado_vendedor = 'cotizado' AND aceptado_usuario = 1)
            )
        """, (id_pedido_original,))
        
        detalles_a_pagar = cursor.fetchall()

        if not detalles_a_pagar:
            flash("No hay productos aprobados para pagar.", "danger")
            return redirect(url_for('carrito_bp.ver'))

        ids_detalles = [d[0] for d in detalles_a_pagar]
        total_pagado = sum(float(d[1]) for d in detalles_a_pagar)

        # -------------------------------------------------------
        # INSERT PEDIDO NUEVO + JSON de detalles_pago
        # -------------------------------------------------------
        cursor.execute("""
            INSERT INTO pedidos (
                id_usuario, fecha_pedido, estado, metodo_pago, 
                direccion_envio, ciudad_envio, telefono_contacto, 
                total_pagado, detalles_pago
            )
            VALUES (%s, NOW(), 'pagado', %s, %s, %s, %s, %s, %s)
        """, (
            id_usuario, metodo_pago, direccion, ciudad, telefono,
            total_pagado, json.dumps(detalles_pago)
        ))

        cursor.execute("SELECT LAST_INSERT_ID()")
        id_nuevo_pedido = cursor.fetchone()[0]

        # 3) MOVER LOS ITEMS PAGADOS AL NUEVO PEDIDO
        placeholders = ",".join(["%s"] * len(ids_detalles))
        cursor.execute(f"""
            UPDATE detalle_pedido
            SET id_pedido = %s
            WHERE id_detalle IN ({placeholders})
        """, [id_nuevo_pedido] + ids_detalles)

        db.connection.commit()

        flash(f"¡Pago exitoso! Tu pedido #{id_nuevo_pedido} fue registrado.", "success")
        return redirect(url_for('home_bp.home'))

    except Exception as e:
        db.connection.rollback()
        print("Error procesando pago:", e)
        flash("Error procesando el pago.", "danger")
        return redirect(url_for('checkout_bp.resumen_pago'))

    finally:
        cursor.close()
        
def calcular_total_con_descuento(db, id_usuario, productos_carrito):
    """
    Calcula el total del carrito aplicando descuentos por suscripción
    
    Args:
        db: Conexión a la base de datos
        id_usuario: ID del usuario
        productos_carrito: Lista de productos en el carrito
        
    Returns:
        dict con subtotal, descuento, total y porcentaje
    """
    subtotal = sum(float(p.get('precio_total', 0)) for p in productos_carrito)
    
    # Obtener descuento según suscripción
    descuento_porcentaje = ModelSuscripcion.obtener_descuento(db, id_usuario)
    descuento_monto = subtotal * descuento_porcentaje
    total = subtotal - descuento_monto
    
    return {
        'subtotal': round(subtotal, 2),
        'descuento_porcentaje': round(descuento_porcentaje * 100, 2),
        'descuento_monto': round(descuento_monto, 2),
        'total': round(total, 2),
        'tiene_descuento': descuento_porcentaje > 0
    }


# ===========================================
# Actualiza tu ruta de checkout existente
# ===========================================

@checkout_bp.route('/')
@login_required
def checkout():
    """Página de checkout con descuentos automáticos"""
    db = current_app.db
    
    # Obtener productos del carrito (tu lógica existente)
    cursor = db.connection.cursor()
    cursor.execute("""
        SELECT dp.*, p.nombre, p.imagen, p.precio
        FROM detalle_pedido dp
        INNER JOIN productos p ON dp.id_producto = p.id_producto
        INNER JOIN pedidos ped ON dp.id_pedido = ped.id_pedido
        WHERE ped.id_usuario = %s AND ped.estado = 'pendiente'
    """, (current_user.id_usuario,))
    
    productos_carrito = cursor.fetchall()
    cursor.close()
    
    # Calcular totales con descuento
    totales = calcular_total_con_descuento(
        db, current_user.id_usuario, productos_carrito
    )
    
    # Obtener información de suscripción
    suscripcion = ModelSuscripcion.obtener_suscripcion_activa(
        db, current_user.id_usuario
    )
    
    return render_template(
        'checkout/checkout.html',
        productos=productos_carrito,
        totales=totales,
        suscripcion=suscripcion,
        user=current_user
    )


# ===========================================
# Vista previa de precio con descuento
# ===========================================

@checkout_bp.route('/precio-con-descuento/<int:id_producto>')
@login_required
def precio_con_descuento(id_producto):
    """API que retorna el precio de un producto con descuento aplicado"""
    from flask import jsonify
    db = current_app.db
    
    cursor = db.connection.cursor()
    cursor.execute("SELECT precio FROM productos WHERE id_producto = %s", (id_producto,))
    resultado = cursor.fetchone()
    cursor.close()
    
    if not resultado:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    precio_original = float(resultado[0])
    precio_final = ModelSuscripcion.aplicar_descuento(
        db, current_user.id_usuario, precio_original
    )
    descuento_porcentaje = ModelSuscripcion.obtener_descuento(
        db, current_user.id_usuario
    ) * 100
    
    return jsonify({
        'precio_original': precio_original,
        'precio_final': precio_final,
        'descuento_porcentaje': descuento_porcentaje,
        'ahorro': precio_original - precio_final
    })


# ===========================================
# Función auxiliar para agregar al carrito con descuento
# ===========================================

def agregar_al_carrito_con_descuento(db, id_usuario, id_producto, cantidad=1):
    """Agrega un producto al carrito aplicando el descuento automáticamente"""
    cursor = db.connection.cursor()
    
    # Obtener precio del producto
    cursor.execute("SELECT precio FROM productos WHERE id_producto = %s", (id_producto,))
    resultado = cursor.fetchone()
    
    if not resultado:
        cursor.close()
        return False, "Producto no encontrado"
    
    precio_original = float(resultado[0])
    
    # Aplicar descuento por suscripción
    precio_final = ModelSuscripcion.aplicar_descuento(db, id_usuario, precio_original)
    precio_total = precio_final * cantidad
    
    try:
        # Buscar o crear pedido pendiente
        cursor.execute("""
            SELECT id_pedido FROM pedidos 
            WHERE id_usuario = %s AND estado = 'pendiente'
            ORDER BY id_pedido DESC LIMIT 1
        """, (id_usuario,))
        
        pedido = cursor.fetchone()
        
        if not pedido:
            # Crear nuevo pedido
            cursor.execute("""
                INSERT INTO pedidos (id_usuario, estado, metodo_pago)
                VALUES (%s, 'pendiente', 'No definido')
            """, (id_usuario,))
            db.connection.commit()
            id_pedido = cursor.lastrowid
        else:
            id_pedido = pedido[0]
        
        # Agregar al detalle del pedido
        cursor.execute("""
            INSERT INTO detalle_pedido 
            (id_pedido, id_producto, cantidad, precio_total)
            VALUES (%s, %s, %s, %s)
        """, (id_pedido, id_producto, cantidad, precio_total))
        
        db.connection.commit()
        cursor.close()
        
        descuento_aplicado = (precio_original - precio_final) * cantidad
        
        return True, {
            'precio_original': precio_original,
            'precio_final': precio_final,
            'descuento_aplicado': descuento_aplicado,
            'precio_total': precio_total
        }
        
    except Exception as e:
        db.connection.rollback()
        cursor.close()
        return False, str(e)