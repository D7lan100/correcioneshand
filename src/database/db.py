# src/database/db.py
import pymysql
from pymysql.cursors import DictCursor
from flask import current_app

def get_connection():
    """
    Devuelve una conexión directa a la base de datos MySQL.
    Compatible con Flask y tu config.py.
    """
    try:
        connection = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            cursorclass=DictCursor
        )
        return connection
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return None
 