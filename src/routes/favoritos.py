from flask import Blueprint, redirect, url_for, session, flash, render_template, current_app, request
from flask_login import login_required, current_user

favoritos_bp = Blueprint('favoritos_bp', __name__, url_prefix="/favoritos")

# -----------------------------
# 🔹 Agregar producto a favoritos
# -----------------------------
@favoritos_bp.route('/agregar/<int:id_producto>', methods=['POST'])
@login_required
def agregar_favorito(id_producto):
    db = current_app.db
    cursor = db.connection.cursor()
    id_usuario = current_user.id_usuario

    try:
        # Verificar si ya está en favoritos
        cursor.execute("""
            SELECT id_favorito FROM favoritos 
            WHERE id_usuario = %s AND id_producto = %s
        """, (id_usuario, id_producto))
        existente = cursor.fetchone()

        if existente:
            flash('Ya está en tus favoritos 💙', 'info')
        else:
            cursor.execute("""
                INSERT INTO favoritos (id_usuario, id_producto)
                VALUES (%s, %s)
            """, (id_usuario, id_producto))
            db.connection.commit()
            flash('Agregado a tus favoritos 💾', 'success')
    except Exception as e:
        db.connection.rollback()
        flash(f'Error al agregar a favoritos: {e}', 'danger')
    finally:
        cursor.close()

    return redirect(request.referrer or url_for('home_bp.home'))


# -----------------------------
# 🔹 Eliminar producto de favoritos
# -----------------------------
@favoritos_bp.route('/eliminar/<int:id_producto>', methods=['POST'])
@login_required
def eliminar_favorito(id_producto):
    db = current_app.db
    cursor = db.connection.cursor()
    id_usuario = current_user.id_usuario

    try:
        cursor.execute("""
            DELETE FROM favoritos 
            WHERE id_usuario = %s AND id_producto = %s
        """, (id_usuario, id_producto))
        db.connection.commit()
        flash('Eliminado de tus favoritos 💔', 'warning')
    except Exception as e:
        db.connection.rollback()
        flash(f'Error al eliminar de favoritos: {e}', 'danger')
    finally:
        cursor.close()
        
    print("📍 Referrer:", request.referrer)
    print("📍 URL Favoritos endpoint:", url_for('favoritos_bp.ver_favoritos'))


    return redirect(request.referrer or url_for('favoritos_bp.ver_favoritos'))


# -----------------------------
# 🔹 Ver lista de favoritos
# -----------------------------
@favoritos_bp.route('/', endpoint='ver_favoritos')
@login_required
def ver_favoritos():
    db = current_app.db
    cursor = db.connection.cursor()

    favoritos = []
    try:
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.imagen, p.id_categoria
            FROM favoritos f
            JOIN productos p ON f.id_producto = p.id_producto
            WHERE f.id_usuario = %s
        """, (current_user.id_usuario,))
        resultados = cursor.fetchall()

        # Convertir las tuplas a diccionarios
        for fila in resultados:
            favoritos.append({
                'id_producto': fila[0],
                'nombre': fila[1],
                'precio': fila[2],
                'imagen': fila[3],
                'id_categoria': fila[4]
            })
    except Exception as e:
        flash(f'Error al cargar favoritos: {e}', 'danger')
    finally:
        cursor.close()

    return render_template('videotutoriales/favoritos.html', favoritos=favoritos)
