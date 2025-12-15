# HandiGenius 🛠️

Sistema web de comercio electrónico especializado en productos artesanales y personalizados, desarrollado con Flask y MySQL.

## 🚀 Características

- **Catálogo de productos** con sistema de categorías
- **Autenticación de usuarios** con roles (cliente, vendedor, administrador)
- **Carrito de compras** con gestión de pedidos
- **Personalización de productos** con carga de bocetos
- **Sistema de calificaciones** y reseñas
- **Panel administrativo** completo
- **Chat en tiempo real** con Socket.IO
- **Sistema de suscripciones** para vendedores
- **Gestión de favoritos**
- **Notificaciones por correo electrónico**
- **Video tutoriales** integrados

## 🛠️ Tecnologías

- **Backend:** Flask 3.0.3
- **Base de datos:** MySQL con PyMySQL
- **Autenticación:** Flask-Login
- **Formularios:** Flask-WTF
- **Sesiones:** Flask-Session (filesystem)
- **WebSockets:** Flask-SocketIO con eventlet
- **Email:** Flask-Mail
- **Servidor:** Gunicorn

## 📋 Requisitos Previos

- Python 3.11+
- MySQL 8.0+
- pip

## 🔧 Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/D7lan100/correcioneshand.git
cd correcioneshand
```

### 2. Crear entorno virtual
```bash
python -m venv env

# Windows
.\env\Scripts\activate

# Linux/Mac
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:
```env
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña
MYSQL_DB=handigeniussandra
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_app_password
```

### 5. Importar base de datos
```bash
# Importa el archivo SQL a tu MySQL local
mysql -u root -p handigeniussandra < handigeniussandra(10).sql
```

### 6. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🌐 Despliegue en Producción

Este proyecto está configurado para desplegarse en Railway:

### Variables de entorno requeridas:
```
FLASK_ENV=production
SECRET_KEY=clave_secreta_segura
MYSQL_HOST=host_de_railway
MYSQL_USER=root
MYSQL_PASSWORD=contraseña_de_railway
MYSQL_DB=railway
MAIL_USERNAME=email@gmail.com
MAIL_PASSWORD=app_password
```

### Archivos de configuración:

- `Procfile`: Configuración para Gunicorn con eventlet workers
- `requirements.txt`: Dependencias de Python
- `.gitignore`: Archivos excluidos del repositorio

## 📁 Estructura del Proyecto
```
correcioneshand/
├── app.py                 # Aplicación principal
├── config.py              # Configuración (dev/prod)
├── Procfile              # Configuración de despliegue
├── requirements.txt      # Dependencias
├── src/
│   ├── models/          # Modelos de datos
│   ├── routes/          # Rutas/controladores
│   ├── templates/       # Plantillas HTML
│   └── static/          # CSS, JS, imágenes
└── flask_session/       # Sesiones del servidor
```

## 👥 Roles de Usuario

### Cliente
- Explorar catálogo de productos
- Agregar productos al carrito
- Realizar pedidos
- Personalizar productos
- Calificar y comentar
- Gestionar favoritos

### Vendedor
- Publicar productos propios
- Gestionar inventario
- Ver estadísticas de ventas
- Responder a solicitudes de personalización

### Administrador
- Gestión completa de usuarios
- Moderación de contenido
- Aprobación de suscripciones
- Acceso a panel de estadísticas
- Gestión de PQRs

## 🔒 Seguridad

- Contraseñas hasheadas con Werkzeug
- Protección CSRF con Flask-WTF
- Sesiones seguras con cookies HttpOnly
- Validación de datos en servidor
- Sanitización de inputs

## 📧 Configuración de Email

Para el envío de correos, necesitas:

1. Cuenta de Gmail
2. Generar una contraseña de aplicación
3. Configurar `MAIL_USERNAME` y `MAIL_PASSWORD`

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autores

**D7lan100**
- GitHub: [@D7lan100](https://github.com/D7lan100)
- GitHub: [@JohannL27](https://github.com/JohannL27)
- GitHub: [@Copetin999](https://github.com/Copetin999)
- GitHub: [@juanesteban999](https://github.com/juanesteban999)
