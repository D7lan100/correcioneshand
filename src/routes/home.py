# src/routes/home.py
from flask import Blueprint, render_template, flash, current_app
from flask_login import login_required, current_user
from src.models.ModelProducto import ModelProducto
from src.models.ModelUser import ModelUser

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/', endpoint='index')
def index():
    try:
        db = current_app.db

        # Productos destacados
        productos_destacados = ModelProducto.obtener_mas_populares(db, limit=9)

        # Totales para estadísticas
        total_productos = ModelProducto.count_all(db) if hasattr(ModelProducto, 'count_all') else len(productos_destacados)
        total_usuarios = ModelUser.count_all(db) if hasattr(ModelUser, 'count_all') else 0

        return render_template(
            'home/index.html',
            productos=productos_destacados,
            total_productos=total_productos,
            total_usuarios=total_usuarios
        )
    except Exception as e:
        flash("Error al cargar los productos: " + str(e), "danger")
        return render_template('home/index.html', productos=[])

@home_bp.route('/home', endpoint='home')
@login_required
def home():
    try:
        db = current_app.db

        productos_lista = ModelProducto.get_all(db)
        total_productos = ModelProducto.count_all(db) if hasattr(ModelProducto, 'count_all') else len(productos_lista)
        total_usuarios = ModelUser.count_all(db) if hasattr(ModelUser, 'count_all') else 0

        return render_template(
            'home/home.html',
            user=current_user,
            productos=productos_lista,
            total_productos=total_productos,
            total_usuarios=total_usuarios
        )
    except Exception as e:
        flash("Error al cargar los productos: " + str(e), "danger")
        return render_template('home/home.html', user=current_user, productos=[])
