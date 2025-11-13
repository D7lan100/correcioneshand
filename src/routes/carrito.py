# src/routes/carrito.py
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user
from src.database.db import get_connection

csrf = CSRFProtect()
carrito_bp = Blueprint('carrito_bp', __name__, template_folder="../templates/navbar")

# ----------------------------------------
# 🛒 Agregar producto al carrito (SESSION)
# ----------------------------------------
@csrf.exempt
@carrito_bp.route('/agregar/<int:id_producto>', methods=['POST'])
def agregar(id_producto):
    cantidad = int(request.form.get('cantidad', 1))

    if 'carrito' not in session:
        session['carrito'] = {}

    carrito = session['carrito']

    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_producto, nombre, precio, imagen 
                FROM productos 
                WHERE id_producto = %s
            """, (id_producto,))
            producto = cursor.fetchone()

        if not producto:
            flash("❌ Producto no encontrado.", "danger")
            return redirect(url_for('productos_bp.productos'))

        id_str = str(id_producto)
        if id_str in carrito:
            carrito[id_str]['cantidad'] += cantidad
        else:
            carrito[id_str] = {
                'id_producto': producto[0],
                'nombre': producto[1],
                'precio': float(producto[2]),
                'imagen': producto[3],
                'cantidad': cantidad
            }

        session['carrito'] = carrito
        session.modified = True  # ✅ MUY IMPORTANTE
        print("🛍️ Carrito actual:", session['carrito'])
        flash("✅ Producto agregado correctamente al carrito.", "success")

    except Exception as e:
        print(f"❌ Error al agregar producto: {e}")
        flash("No se pudo agregar el producto al carrito.", "danger")

    return redirect(url_for('carrito_bp.ver'))

# ----------------------------------------
# 👀 Ver carrito (desde SESSION)
# ----------------------------------------
@csrf.exempt
@carrito_bp.route('/')
def ver():
    carrito = session.get('carrito', {})
    productos_detalle = []
    total = 0.0

    if not carrito:
        flash("Tu carrito está vacío. Agrega productos antes de continuar.", "info")
        return render_template('navbar/carrito.html', productos=[], total=0)

    # ✅ Leer directamente los datos del carrito guardado en la sesión
    for item in carrito.values():
        subtotal = float(item['precio']) * int(item['cantidad'])
        total += subtotal
        productos_detalle.append({
            'id_producto': item['id_producto'],
            'nombre': item['nombre'],
            'precio': item['precio'],
            'imagen': item['imagen'],
            'cantidad': item['cantidad'],
            'subtotal': subtotal
        })

    print("🧾 Carrito mostrado:", productos_detalle)
    return render_template('navbar/carrito.html', productos=productos_detalle, total=total)

# ----------------------------------------
# 🗑️ Eliminar producto del carrito
# ----------------------------------------
@csrf.exempt
@carrito_bp.route('/eliminar/<int:id_producto>', methods=['POST'])
def eliminar(id_producto):
    carrito = session.get('carrito', {})

    id_str = str(id_producto)
    if id_str in carrito:
        del carrito[id_str]
        session['carrito'] = carrito
        session.modified = True
        flash("🗑️ Producto eliminado del carrito.", "info")
    else:
        flash("⚠️ El producto no se encontró en el carrito.", "warning")

    return redirect(url_for('carrito_bp.ver'))


# ----------------------------------------
# 🧹 Vaciar carrito
# ----------------------------------------
@csrf.exempt
@carrito_bp.route('/vaciar', methods=['POST'])
def vaciar():
    session.pop('carrito', None)
    flash("🧹 Carrito vaciado correctamente.", "info")
    return redirect(url_for('carrito_bp.ver'))


# ----------------------------------------
# 💳 Checkout — Confirmación del pedido
# ----------------------------------------
@csrf.exempt
@carrito_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    carrito = session.get('carrito', {})
    if not carrito:
        flash("⚠️ Tu carrito está vacío.", "warning")
        return redirect(url_for('carrito_bp.ver'))

    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nombre_completo, correo, telefono, direccion
            FROM usuarios WHERE id_usuario = %s
        """, (current_user.id_usuario,))
        usuario = cursor.fetchone()

    usuario_data = {
        'nombre': usuario[0] if usuario else '',
        'correo': usuario[1] if usuario else '',
        'telefono': usuario[2] if usuario else '',
        'direccion': usuario[3] if usuario else ''
    }

    productos = list(carrito.values())
    total = sum(item['precio'] * item['cantidad'] for item in productos)

    if request.method == 'POST':
        # Guardar pedido en base de datos (si lo deseas)
        flash("✅ Pedido confirmado correctamente.", "success")
        session.pop('carrito', None)
        return redirect(url_for('carrito_bp.ver'))

    return render_template('navbar/confirmar_pedido.html', items=productos, total=total, usuario=usuario_data)


# ----------------------------------------
# 🚀 Continuar compra — Resumen con usuario
# ----------------------------------------
@carrito_bp.route('/continuar')
@login_required
def continuar():
    carrito = session.get('carrito', {})

    if not carrito:
        flash('Tu carrito está vacío. Agrega productos antes de continuar.', 'warning')
        return redirect(url_for('carrito_bp.ver'))

    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())

    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (current_user.id_usuario,))
        usuario = cursor.fetchone()

    return render_template(
        'carrito/continuar.html',
        usuario=usuario,
        carrito=carrito,
        total=total
    )
