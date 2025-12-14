from flask import Blueprint, render_template, flash, current_app, request
from flask_login import login_required, current_user
from src.models.ModelProducto import ModelProducto
from src.models.ModelUser import ModelUser
from datetime import datetime

# ---------------------------
# Helpers (Copiados de admin_bp.py para garantizar que funcione)
# ---------------------------
def fetchall_dict(cursor):
    """Convierte los resultados del cursor en una lista de diccionarios."""
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

# ---------------------------
# Definición del Blueprint
# ---------------------------
home_bp = Blueprint('home_bp', __name__)

# ---------------------------
# Funciones de Soporte para la Base de Datos
# ---------------------------
def obtener_categorias(db):
    """Obtiene todas las categorías de la BD."""
    categorias = []
    try:
        cur = db.connection.cursor()
        cur.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre ASC")
        categorias = fetchall_dict(cur)
        cur.close()
    except Exception as e:
        # En un entorno real, usarías logging.error(e)
        print(f"❌ Error al cargar categorías: {e}")
    return categorias


# ---------------------------
# Ruta Principal / (Productos Destacados)
# ---------------------------
@home_bp.route('/', endpoint='index')
def index():
    try:
        db = current_app.db
        
        # 1. Obtener datos clave
        # Asumimos que get_mas_vendidos devuelve una lista de diccionarios (iterable)
        productos_destacados = ModelProducto.get_mas_vendidos(db, limit=9)
        categorias_lista = obtener_categorias(db)
        
        # 2. Obtener estadísticas
        total_productos = ModelProducto.count_all(db) if hasattr(ModelProducto, 'count_all') else len(productos_destacados)
        total_usuarios = ModelUser.count_all(db) if hasattr(ModelUser, 'count_all') else 0

        return render_template(
            'home/index.html',
            productos=productos_destacados,
            categorias=categorias_lista,
            total_productos=total_productos,
            total_usuarios=total_usuarios
        )
    except Exception as e:
        flash("Error al cargar la página principal: " + str(e), "danger")
        return render_template('home/index.html', productos=[], categorias=[], total_productos=0, total_usuarios=0)

# ---------------------------
# Ruta Home /home (Requiere login - Vista principal de productos)
# ---------------------------
@home_bp.route('/home', endpoint='home')
@login_required
def home():
    try:
        db = current_app.db
        
        # 1. Obtener el número de página de la URL. Por defecto, es 1.
        page = request.args.get('page', 1, type=int)
        PER_PAGE = 20

        # 2. Obtener los productos paginados (Devuelve el objeto de paginación)
        productos_paginados = ModelProducto.get_all(db, page=page, per_page=PER_PAGE)
        
        # 🚨 CORRECCIÓN CRÍTICA: Extraer la lista de productos del objeto de paginación
        productos_a_mostrar = productos_paginados.items
        
        categorias_lista = obtener_categorias(db) 
        
        # 3. Obtener estadísticas (opcional)
        total_productos = productos_paginados.total
        total_usuarios = ModelUser.count_all(db) if hasattr(ModelUser, 'count_all') else 0

        # 4. Renderizar y pasar las variables
        return render_template(
            'home/home.html',
            user=current_user,
            productos=productos_a_mostrar, # ⬅️ AHORA PASAMOS LA LISTA REAL DE PRODUCTOS (.items)
            categorias=categorias_lista, 
            total_productos=total_productos,
            total_usuarios=total_usuarios,
            
            # NOTA: También puedes pasar el objeto de paginación si lo usas en la plantilla para los botones
            # pagination=productos_paginados 
        )
    except Exception as e:
        # Aquí es donde capturas si falla la conexión o el modelo
        flash("Error al cargar los productos o categorías: " + str(e), "danger")
        # Asegúrate de pasar listas vacías en caso de error
        return render_template('home/home.html', user=current_user, productos=[], categorias=[], total_productos=0, total_usuarios=0)