from flask import Blueprint, redirect, url_for, session, flash, render_template, current_app, request
from flask_login import login_required, current_user

favoritos_bp = Blueprint('favoritos_bp', __name__, url_prefix="/favoritos")

@favoritos_bp.route('/agregar/<int:id_producto>', methods=['POST'])
@login_required
def agregar_favorito(id_producto):
    db = current_app.db
    cursor = db.connection.cursor()
    id_usuario = current_user.id_usuario

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

    return redirect(request.referrer or url_for('home_bp.home'))



@favoritos_bp.route('/eliminar/<int:id_producto>', methods=['POST'])
@login_required
def eliminar_favorito(id_producto):
    db = current_app.db
    cursor = db.connection.cursor()
    id_usuario = current_user.id_usuario

    cursor.execute("""
        DELETE FROM favoritos WHERE id_usuario = %s AND id_producto = %s
    """, (id_usuario, id_producto))
    db.connection.commit()
    flash('Eliminado de tus favoritos 💔', 'warning')

    return redirect(request.referrer or url_for('favoritos_bp.ver_favoritos'))


@favoritos_bp.route('/')
@login_required
def ver_favoritos():
    db = current_app.db
    cursor = db.connection.cursor()

    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.precio, p.imagen, p.id_categoria
        FROM favoritos f
        JOIN productos p ON f.id_producto = p.id_producto
        WHERE f.id_usuario = %s
    """, (current_user.id_usuario,))
    
    resultados = cursor.fetchall()

    # Convertir las tuplas a diccionarios manualmente
    favoritos = []
    for fila in resultados:
        favoritos.append({
            'id_producto': fila[0],
            'nombre': fila[1],
            'precio': fila[2],
            'imagen': fila[3],
            'id_categoria': fila[4]
        })

    return render_template('videotutoriales/favoritos.html', favoritos=favoritos)
