-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 15-12-2025 a las 00:22:11
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `handigeniussandra`
--

DELIMITER $$
--
-- Procedimientos
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_cantidad_producto_material` (IN `p_id_producto` INT, IN `p_id_material` INT, IN `p_nueva_cantidad` DECIMAL(10,2))   BEGIN
  UPDATE producto_material
  SET cantidad_utilizada = p_nueva_cantidad
  WHERE id_producto = p_id_producto AND id_material = p_id_material;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_correo_usuario` (IN `p_id_usuario` INT, IN `p_nuevo_correo` VARCHAR(100))   BEGIN
  UPDATE usuarios
  SET correo_electronico = p_nuevo_correo
  WHERE id_usuario = p_id_usuario;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_estado_pedido` (IN `p_id_pedido` INT, IN `p_nuevo_estado` ENUM('pendiente','pagado','enviado','entregado','cancelado'))   BEGIN
  UPDATE pedidos
  SET estado = p_nuevo_estado
  WHERE id_pedido = p_id_pedido;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_estado_sugerencia` (IN `p_id_sugerencia` INT, IN `p_nuevo_estado` ENUM('pendiente','respondida','rechazada'))   BEGIN
  UPDATE sugerencias
  SET estado = p_nuevo_estado
  WHERE id_sugerencia = p_id_sugerencia;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_fecha_inventario` (IN `p_id_inventario` INT, IN `p_nueva_fecha` DATE)   BEGIN
  UPDATE inventario_materiales
  SET fecha_entrada = p_nueva_fecha
  WHERE id_inventario = p_id_inventario;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_nombre_rol` (IN `p_id_rol` INT, IN `p_nuevo_nombre` VARCHAR(50))   BEGIN
  UPDATE roles
  SET nombre = p_nuevo_nombre
  WHERE id_rol = p_id_rol;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_precio_producto` (IN `p_id_producto` INT, IN `p_nuevo_precio` DECIMAL(10,2))   BEGIN
  UPDATE productos
  SET precio = p_nuevo_precio
  WHERE id_producto = p_id_producto;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_precio_tipo_suscripcion` (IN `p_id_tipo` INT, IN `p_nuevo_precio` DECIMAL(10,2))   BEGIN
  UPDATE tipo_suscripcion
  SET precio_mensual = p_nuevo_precio
  WHERE id_tipo_suscripcion = p_id_tipo;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_precio_tutorial` (IN `p_id_tutorial` INT, IN `p_nuevo_precio` DECIMAL(10,2))   BEGIN
  UPDATE tutoriales
  SET precio = p_nuevo_precio
  WHERE id_tutorial = p_id_tutorial;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_puntuacion_calificacion_producto` (IN `p_id_calificacion` INT, IN `p_nueva_puntuacion` DECIMAL(2,1))   BEGIN
  UPDATE calificaciones
  SET puntuacion = p_nueva_puntuacion
  WHERE id_calificacion = p_id_calificacion;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_stock_material` (IN `p_id_material` INT, IN `p_nuevo_stock` DECIMAL(10,2))   BEGIN
  UPDATE materiales
  SET stock_actual = p_nuevo_stock
  WHERE id_material = p_id_material;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `buscar_tutoriales_por_usuario` (IN `p_id_usuario` INT)   BEGIN
  SELECT t.*
  FROM tutoriales t
  WHERE t.id_usuario = p_id_usuario;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `consultar_pedidos_usuario` (IN `p_id_usuario` INT)   BEGIN
  SELECT p.id_pedido, p.estado, p.fecha_pedido, p.metodo_pago
  FROM pedidos p
  WHERE p.id_usuario = p_id_usuario;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `insertar_producto` (IN `p_nombre` VARCHAR(150), IN `p_descripcion` TEXT, IN `p_precio` DECIMAL(10,2), IN `p_imagen` TEXT, IN `p_id_categoria` INT, IN `p_id_vendedor` INT, IN `p_es_personalizable` BOOLEAN)   BEGIN
  INSERT INTO productos (nombre, descripcion, precio, imagen, id_categoria, id_vendedor, es_personalizable)
  VALUES (p_nombre, p_descripcion, p_precio, p_imagen, p_id_categoria, p_id_vendedor, p_es_personalizable);
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `insertar_sugerencia_usuario` (IN `p_id_usuario` INT, IN `p_titulo` VARCHAR(150), IN `p_descripcion` TEXT)   BEGIN
  INSERT INTO sugerencias (id_usuario, titulo, descripcion, fecha_envio)
  VALUES (p_id_usuario, p_titulo, p_descripcion, CURDATE());
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `productos_por_categoria` (IN `p_id_categoria` INT)   BEGIN
  SELECT p.*
  FROM productos p
  WHERE p.id_categoria = p_id_categoria;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `registrar_calificacion` (IN `p_id_usuario` INT, IN `p_id_producto` INT, IN `p_puntuacion` DECIMAL(2,1), IN `p_comentario` TEXT)   BEGIN
  INSERT INTO calificaciones (id_usuario, id_producto, puntuacion, comentario)
  VALUES (p_id_usuario, p_id_producto, p_puntuacion, p_comentario);
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `registrar_ingreso_inventario` (IN `p_id_material` INT, IN `p_cantidad` DECIMAL(10,2), IN `p_observaciones` TEXT)   BEGIN
  INSERT INTO inventario_materiales (id_material, fecha_entrada, cantidad, observaciones)
  VALUES (p_id_material, CURDATE(), p_cantidad, p_observaciones);
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `ver_productos_personalizables` ()   BEGIN
  SELECT * FROM productos WHERE es_personalizable = TRUE;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `vistas_interaccion_materiales` ()   BEGIN
  SELECT * FROM materiales;
  SELECT * FROM producto_material;
  SELECT * FROM inventario_materiales;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `vistas_interaccion_productos` ()   BEGIN
  SELECT * FROM productos;
  SELECT * FROM producto_material;
  SELECT * FROM categorias;
  SELECT * FROM detalle_pedido;
  SELECT * FROM tutoriales;
  SELECT * FROM usuarios;
  SELECT * FROM calificaciones;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `vistas_interaccion_suscripcion` ()   BEGIN
  SELECT * FROM suscripciones;
  SELECT * FROM usuarios;
  SELECT * FROM tipo_suscripcion;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `vistas_interaccion_tutoriales` ()   BEGIN
  SELECT * FROM tutoriales;
  SELECT * FROM usuarios;
  SELECT * FROM productos;        -- combos ahora son producto_relacion
  SELECT * FROM calificaciones;   -- ya no hay tabla calificacion_tutoriales
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `vistas_interaccion_usuario` ()   BEGIN
  SELECT * FROM usuarios;
  SELECT * FROM suscripciones;
  SELECT * FROM sugerencias;
  SELECT * FROM roles;
  SELECT * FROM calificaciones;  -- unificada para productos y tutoriales
  SELECT * FROM pedidos;
  SELECT * FROM detalle_pedido;  -- reemplaza carrito
  SELECT * FROM tutoriales;
  SELECT * FROM productos;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `vistas_todas_las_tablas` ()   BEGIN
  SELECT * FROM calificaciones;
  SELECT * FROM detalle_pedido;
  SELECT * FROM inventario_materiales;
  SELECT * FROM materiales;
  SELECT * FROM pedidos;
  SELECT * FROM producto_material;
  SELECT * FROM productos;
  SELECT * FROM roles;
  SELECT * FROM sugerencias;
  SELECT * FROM suscripciones;
  SELECT * FROM tipo_suscripcion;
  SELECT * FROM tutoriales;
  SELECT * FROM usuarios;
  SELECT * FROM categorias;
  SELECT * FROM material_audiovisual;
  SELECT * FROM calendario;
  SELECT * FROM domicilio;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calendario`
--

CREATE TABLE `calendario` (
  `id_evento` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `nombre_evento` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_evento` date NOT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `calendario`
--

INSERT INTO `calendario` (`id_evento`, `id_usuario`, `nombre_evento`, `descripcion`, `fecha_evento`, `fecha_registro`) VALUES
(1, 6, 'Cumpleaños de Ana', 'Comprar un ramo de rosas y una carta personalizada', '2025-09-15', '2025-09-14 15:23:34'),
(3, 14, 'cumpleaños', 'padre ', '2025-11-07', '2025-11-02 20:26:18'),
(4, 18, 'Madre cumpleaños', 'wdsadas', '2025-11-29', '2025-11-13 08:08:19');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calificaciones`
--

CREATE TABLE `calificaciones` (
  `id_calificacion` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `puntuacion` decimal(2,1) DEFAULT NULL,
  `comentario` text DEFAULT NULL,
  `fecha_calificacion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `calificaciones`
--

INSERT INTO `calificaciones` (`id_calificacion`, `id_usuario`, `id_producto`, `puntuacion`, `comentario`, `fecha_calificacion`) VALUES
(14, 14, 61, 3.0, 'uiduuds', '2025-11-13 07:43:57'),
(15, 19, 65, 5.0, 'chimbita', '2025-11-13 19:51:13'),
(16, 14, 46, 5.0, '', '2025-11-25 22:16:49'),
(17, 14, 40, 5.0, 'adjffjaiodewio', '2025-11-25 22:17:13'),
(18, 14, 39, 5.0, '3414313234', '2025-11-25 22:17:26'),
(19, 14, 65, 1.0, 'horrible', '2025-11-26 11:41:24'),
(20, 19, 61, 5.0, 'si esta muy chimba', '2025-11-26 11:59:23');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`) VALUES
(1, 'Ramo', 'Ramos de flores personalizables'),
(2, 'Carta', 'Cartas personalizadas con mensajes'),
(3, 'Combo', 'Paquetes de productos combinados'),
(4, 'Tutorial', 'Videotutoriales de elaboración'),
(5, 'Material', 'Materiales para fabricar los detalles');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_pedido`
--

CREATE TABLE `detalle_pedido` (
  `id_detalle` int(11) NOT NULL,
  `id_pedido` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad` int(11) DEFAULT 1,
  `precio_total` decimal(10,2) DEFAULT NULL,
  `instrucciones_envio` text DEFAULT NULL,
  `formulario_seleccionado` text DEFAULT NULL,
  `texto_personalizado` text DEFAULT NULL,
  `imagen_personalizada` text DEFAULT NULL,
  `plantilla_seleccionada` text DEFAULT NULL,
  `estado_vendedor` enum('pendiente','aprobado','rechazado','cotizado') DEFAULT 'pendiente',
  `mensaje_vendedor` text DEFAULT NULL,
  `precio_propuesto` decimal(10,2) DEFAULT NULL,
  `aceptado_usuario` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_pedido`
--

INSERT INTO `detalle_pedido` (`id_detalle`, `id_pedido`, `id_producto`, `cantidad`, `precio_total`, `instrucciones_envio`, `formulario_seleccionado`, `texto_personalizado`, `imagen_personalizada`, `plantilla_seleccionada`, `estado_vendedor`, `mensaje_vendedor`, `precio_propuesto`, `aceptado_usuario`) VALUES
(12, 7, 48, 1, 12000.00, NULL, NULL, NULL, NULL, NULL, 'pendiente', NULL, NULL, 0),
(13, 7, 39, 1, 82000.00, NULL, NULL, 'ydfufyuewfgr', 'src\\static\\personalizacion\\bocetos_usuarios\\descarga_1.jpg', NULL, 'pendiente', NULL, NULL, 0),
(14, 7, 38, 1, 63000.00, NULL, NULL, 'grfdhdgbrdg', 'src\\static\\personalizacion\\bocetos_usuarios\\images_3.jpg', NULL, 'pendiente', NULL, NULL, 0),
(27, 15, 71, 1, 800000.00, NULL, NULL, 'diosss', 'personalizacion/bocetos_usuarios/IMG_2024.PNG', '{\"flores\": \"Rojas\", \"flores_url\": \"/static/personalizacion/flores_rojas.png\", \"secundarias\": \"Escabiosa\", \"papel\": \"Negro\", \"cinta\": \"Negra\"}', 'aprobado', NULL, 800000.00, 1),
(28, 20, 49, 1, 18000.00, NULL, NULL, NULL, NULL, NULL, 'aprobado', NULL, NULL, 0),
(29, 14, 72, 1, 211000.00, NULL, NULL, 'VAMOOO', 'personalizacion/bocetos_usuarios/IMG_1309.PNG', '{\"flores\": \"Blancas\", \"flores_url\": \"/static/personalizacion/flores_blancas.png\", \"secundarias\": \"Asparagus\", \"papel\": \"Negro\", \"cinta\": \"Negra\"}', 'cotizado', NULL, 300000.00, 0),
(30, 17, 71, 1, 80000.00, NULL, NULL, NULL, 'personalizacion/bocetos_usuarios/descarga_1.jpg', NULL, 'aprobado', NULL, 80000.00, 1),
(31, 17, 72, 1, 211000.00, NULL, NULL, NULL, 'personalizacion/bocetos_usuarios/sensores-de-agua-removebg-preview.png', NULL, 'cotizado', NULL, 40000.00, 0),
(35, 19, 72, 1, 211000.00, NULL, NULL, NULL, NULL, NULL, 'aprobado', NULL, NULL, 0),
(36, 14, 36, 1, 67000.00, NULL, NULL, 'sialsakdjakjdskjbdbakbjfjbfad', 'personalizacion/bocetos_usuarios/image_12.png', '{\"flores\": \"Rosadas\", \"flores_url\": \"/static/personalizacion/flores_rosadas.png\", \"secundarias\": \"Solidago\", \"papel\": \"Kraft\", \"cinta\": \"Azul\"}', 'pendiente', NULL, NULL, 0),
(37, 20, 76, 1, 250000.00, NULL, '{\"contacto\": {\"nombre\": \"Johann Leon\", \"email\": \"johannleon2007@gmail.com\", \"telefono\": \"3214567890\"}, \"producto_info\": \"Ramo buchon 100 rosas\", \"destinatario\": {\"nombre\": \"Maribel\", \"relacion\": \"Familiar\", \"relacion_otro\": \"\"}, \"ocasion\": \"Día de la Madre\", \"estilo\": \"Divertido\", \"estilo_otro\": \"\", \"incluir_mensaje\": \"Sí\", \"mensaje_personalizado\": \"Te amo mami\", \"ramos\": {\"tipos\": [\"Rosas\", \"Tulipanes\"], \"cantidad\": \"12\", \"cantidad_otro\": \"\", \"envoltura\": [\"Tela decorativa\"], \"detalles\": \"moño rosa\"}, \"carta\": {\"estilo\": null, \"mensaje\": \"\", \"extension\": null, \"extension_otro\": \"\"}, \"colores\": [\"Rosa\", \"Azul\"], \"detalles_adicionales\": \"no gracias el moño rosado no mas\", \"fecha_limite\": \"2025-11-30\", \"acepto_condiciones\": true}', 'aljsdhadjkakdhadjsdsahk', 'personalizacion/bocetos_usuarios/images_3.jpg', '{\"flores\": \"Amarillas\", \"flores_url\": \"/static/personalizacion/flores_amarillas.png\", \"secundarias\": \"Asparagus\", \"papel\": \"Blanco\", \"cinta\": \"Rosa\"}', 'aprobado', NULL, 250000.00, 1),
(38, 19, 76, 1, 200000.00, NULL, NULL, NULL, NULL, NULL, 'aprobado', NULL, NULL, 0);

--
-- Disparadores `detalle_pedido`
--
DELIMITER $$
CREATE TRIGGER `calcular_precio_total_detalle` BEFORE INSERT ON `detalle_pedido` FOR EACH ROW BEGIN
  SET NEW.precio_total = NEW.cantidad * (
    SELECT precio FROM productos WHERE id_producto = NEW.id_producto
  );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `validar_pedido_vacio` AFTER DELETE ON `detalle_pedido` FOR EACH ROW BEGIN
  IF NOT EXISTS (SELECT 1 FROM detalle_pedido WHERE id_pedido = OLD.id_pedido) THEN
    UPDATE pedidos
    SET estado = 'cancelado'
    WHERE id_pedido = OLD.id_pedido;
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `domicilio`
--

CREATE TABLE `domicilio` (
  `id_domicilio` int(11) NOT NULL,
  `id_pedido` int(11) DEFAULT NULL,
  `direccion_envio` text DEFAULT NULL,
  `fecha_envio` date DEFAULT NULL,
  `estado` enum('pendiente','en camino','entregado','cancelado') DEFAULT 'pendiente',
  `empresa_transportadora` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `domicilio`
--

INSERT INTO `domicilio` (`id_domicilio`, `id_pedido`, `direccion_envio`, `fecha_envio`, `estado`, `empresa_transportadora`) VALUES
(2, 3, 'Carrera 10 #20-30, Medellín', '2025-08-21', 'pendiente', 'Coordinadora');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `donaciones`
--

CREATE TABLE `donaciones` (
  `id_donacion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `monto` decimal(12,2) NOT NULL,
  `metodo_pago` varchar(50) NOT NULL,
  `detalles_pago` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`detalles_pago`)),
  `fecha` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `donaciones`
--

INSERT INTO `donaciones` (`id_donacion`, `id_usuario`, `monto`, `metodo_pago`, `detalles_pago`, `fecha`) VALUES
(1, 14, 50000.00, 'PSE', '{\"monto\": \"50000\", \"metodo_pago\": \"PSE\", \"detalles_pago\": \"{\\\"banco\\\":\\\"ojefuewlf\\\",\\\"documento\\\":\\\"efwfew\\\",\\\"nombre\\\":\\\"fewfew\\\"}\"}', '0000-00-00 00:00:00'),
(2, 19, 70000.00, 'PSE', '{\"monto\": \"70000\", \"metodo_pago\": \"PSE\", \"detalles_pago\": \"{\\\"banco\\\":\\\"Davivienda\\\",\\\"documento\\\":\\\"1029144866\\\",\\\"nombre\\\":\\\"Johann Leon\\\"}\"}', '0000-00-00 00:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `favoritos`
--

CREATE TABLE `favoritos` (
  `id_favorito` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `fecha_guardado` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `favoritos`
--

INSERT INTO `favoritos` (`id_favorito`, `id_usuario`, `id_producto`, `fecha_guardado`) VALUES
(3, 20, 64, '2025-11-17 23:49:13'),
(7, 19, 64, '2025-11-26 17:49:17');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `material_audiovisual`
--

CREATE TABLE `material_audiovisual` (
  `id_material_audiovisual` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `titulo` varchar(255) DEFAULT NULL,
  `tipo` enum('imagen','video','documento') NOT NULL,
  `url` text NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_subida` datetime DEFAULT current_timestamp(),
  `miniatura` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id_notificacion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `mensaje` text NOT NULL,
  `fecha_envio` datetime DEFAULT current_timestamp(),
  `leida` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `notificaciones`
--

INSERT INTO `notificaciones` (`id_notificacion`, `id_usuario`, `titulo`, `mensaje`, `fecha_envio`, `leida`) VALUES
(1, 14, 'Sugerencia pendiente', 'Tu sugerencia \'un menu mas bonito\' fue marcada como \'pendiente\'.', '2025-11-20 13:51:45', 0),
(2, 18, 'Sugerencia aceptada', 'Tu sugerencia \'Solicitud pra epoca navideña\' fue marcada como \'aceptada\'.', '2025-11-20 22:54:46', 0),
(3, 20, 'Sugerencia aceptada', 'Tu sugerencia \'Solicitud pra epoca navideña\' fue marcada como \'aceptada\'.', '2025-11-26 11:48:53', 0),
(4, 14, 'Sugerencia aceptada', 'Tu sugerencia \'un menu mas bonito\' fue marcada como \'aceptada\'.', '2025-11-26 12:06:57', 0),
(5, 18, 'Sugerencia pendiente', 'Tu sugerencia \'Solicitud pra epoca navideña\' fue marcada como \'pendiente\'.', '2025-11-26 12:43:31', 0),
(6, 14, 'Sugerencia pendiente', 'Tu sugerencia \'un menu mas bonito\' fue marcada como \'pendiente\'.', '2025-11-26 12:43:42', 0),
(7, 14, 'Sugerencia aceptada', 'Tu sugerencia \'un menu mas bonito\' fue marcada como \'aceptada\'. Comentario del administrador: ioemiow', '2025-11-26 12:43:55', 0),
(8, 18, 'Sugerencia aceptada', 'Tu sugerencia \'Solicitud pra epoca navideña\' fue marcada como \'aceptada\'. Comentario del administrador: dijeojdwodjw', '2025-11-26 12:44:02', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id_pedido` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_pedido` datetime DEFAULT current_timestamp(),
  `estado` enum('pendiente','pagado','enviado','entregado','cancelado') DEFAULT 'pendiente',
  `metodo_pago` varchar(50) DEFAULT NULL,
  `direccion_envio` text DEFAULT NULL,
  `ciudad_envio` varchar(100) DEFAULT NULL,
  `telefono_contacto` varchar(20) DEFAULT NULL,
  `total_pagado` decimal(10,2) DEFAULT 0.00,
  `detalles_pago` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`detalles_pago`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos`
--

INSERT INTO `pedidos` (`id_pedido`, `id_usuario`, `fecha_pedido`, `estado`, `metodo_pago`, `direccion_envio`, `ciudad_envio`, `telefono_contacto`, `total_pagado`, `detalles_pago`) VALUES
(2, 8, '2025-09-14 15:23:34', 'pagado', 'Nequi', NULL, NULL, NULL, 0.00, NULL),
(3, 7, '2025-09-14 15:23:34', 'cancelado', 'Daviplata', NULL, NULL, NULL, 0.00, NULL),
(4, 14, '2025-11-13 02:36:24', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(5, 14, '2025-11-13 04:25:57', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(6, 14, '2025-11-13 06:08:40', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(7, 18, '2025-11-13 07:05:38', 'pendiente', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(8, 19, '2025-11-13 23:34:34', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(9, 19, '2025-11-14 03:59:05', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(10, 20, '2025-11-14 04:11:40', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(11, 19, '2025-11-17 17:32:18', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(12, 20, '2025-11-17 17:41:38', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(13, 19, '2025-11-17 17:42:39', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(14, 19, '2025-11-17 17:58:59', 'pendiente', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(15, 20, '2025-11-17 18:18:33', 'pendiente', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(16, 14, '2025-11-20 15:52:09', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(17, 14, '2025-11-25 21:13:41', 'pagado', 'Tarjeta Crédito/Débito', 'carrera 69 p bis # 73 a 42', 'Bogotá', '3214567890', 291000.00, '{\"envio\": {\"ciudad\": \"Bogot\\u00e1\", \"telefono\": \"3214567890\", \"direccion\": \"carrera 69 p bis # 73 a 42\"}, \"metodo\": \"Tarjeta Cr\\u00e9dito/D\\u00e9bito\", \"datos\": {\"titular\": \"dfeuewohfw\", \"numero\": \"3213321232456789\", \"exp\": \"10/30\", \"cvc\": \"321\", \"postal\": \"11011\"}}'),
(18, 14, '2025-11-26 11:44:07', 'cancelado', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(19, 14, '2025-11-26 11:47:23', 'pendiente', 'No definido', NULL, NULL, NULL, 0.00, NULL),
(20, 19, '2025-11-26 12:39:23', 'pagado', 'Tarjeta Crédito/Débito', 'carrera 69 p bis # 73 a 42', 'Bogotá', '3214567890', 268000.00, '{\"envio\": {\"ciudad\": \"Bogot\\u00e1\", \"telefono\": \"3214567890\", \"direccion\": \"carrera 69 p bis # 73 a 42\"}, \"metodo\": \"Tarjeta Cr\\u00e9dito/D\\u00e9bito\", \"datos\": {\"titular\": \"Johann Leon\", \"numero\": \"3213321232456789\", \"exp\": \"10/30\", \"cvc\": \"873\", \"postal\": \"11011\"}}');

--
-- Disparadores `pedidos`
--
DELIMITER $$
CREATE TRIGGER `backup_pedidos_cancelados` AFTER DELETE ON `pedidos` FOR EACH ROW BEGIN
  INSERT INTO pedidos_cancelados (
    id_pedido, id_usuario, fecha_pedido, estado_original, metodo_pago, motivo
  )
  VALUES (
    OLD.id_pedido, OLD.id_usuario, OLD.fecha_pedido, OLD.estado, OLD.metodo_pago,
    'Cancelado por eliminación directa'
  );
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos_cancelados`
--

CREATE TABLE `pedidos_cancelados` (
  `id_pedido` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `fecha_pedido` datetime DEFAULT NULL,
  `estado_original` varchar(20) DEFAULT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `motivo` text DEFAULT NULL,
  `fecha_cancelacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos_cancelados`
--

INSERT INTO `pedidos_cancelados` (`id_pedido`, `id_usuario`, `fecha_pedido`, `estado_original`, `metodo_pago`, `motivo`, `fecha_cancelacion`) VALUES
(1, 5, '2025-09-14 15:23:34', 'cancelado', 'Tarjeta de crédito', 'Cancelado por eliminación directa', '2025-11-10 04:56:07');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pqr`
--

CREATE TABLE `pqr` (
  `id_pqr` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `tipo` enum('Queja','Petición','Reclamo','Sugerencia','Pregunta') NOT NULL,
  `es_pregunta` tinyint(1) DEFAULT 0,
  `asunto` varchar(150) DEFAULT NULL,
  `mensaje` text NOT NULL,
  `respuesta` text DEFAULT NULL,
  `visible_faq` tinyint(1) DEFAULT 0,
  `estado` enum('Pendiente','Respondido') DEFAULT 'Pendiente',
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pqr`
--

INSERT INTO `pqr` (`id_pqr`, `id_usuario`, `tipo`, `es_pregunta`, `asunto`, `mensaje`, `respuesta`, `visible_faq`, `estado`, `fecha`) VALUES
(7, 14, 'Sugerencia', 1, 'efbouwouefbew', 'habla habla h afvioviowenf', 'dasdas', 0, 'Respondido', '2025-11-21 18:33:13'),
(8, 14, 'Pregunta', 1, 'WAAWFASFAS', 'FAFFASFA', 'UY8GUYYG76', 0, 'Respondido', '2025-11-21 20:01:55'),
(9, 14, 'Petición', 1, 'ijladjiowejfciowe', 'euiwcnionwiociownrcio', 'que chimba', 1, 'Respondido', '2025-11-26 16:47:44'),
(10, 20, 'Petición', 1, 'wefwefw', 'fwefewf', 'fwfewfew', 1, 'Respondido', '2025-11-26 16:50:03'),
(11, 20, 'Queja', 1, 'dasdasd', 'dasdasf', NULL, 0, 'Pendiente', '2025-11-26 16:51:05'),
(12, 19, 'Pregunta', 1, 'efbouwouefbew', 'ceiownciowencionwec', 'tititit', 1, 'Respondido', '2025-11-26 17:44:54');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  `imagen` text DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_vendedor` int(11) DEFAULT NULL,
  `disponible` tinyint(1) DEFAULT 1,
  `es_personalizable` tinyint(1) DEFAULT 1,
  `calificacion_promedio` decimal(3,2) DEFAULT NULL,
  `instrucciones` text DEFAULT NULL,
  `tipo_video` enum('publico','privado','premium') DEFAULT NULL,
  `url_video` text DEFAULT NULL,
  `archivo_video` text DEFAULT NULL,
  `nivel_dificultad` varchar(50) DEFAULT NULL,
  `duracion` varchar(50) DEFAULT NULL,
  `herramientas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre`, `descripcion`, `precio`, `imagen`, `id_categoria`, `id_vendedor`, `disponible`, `es_personalizable`, `calificacion_promedio`, `instrucciones`, `tipo_video`, `url_video`, `archivo_video`, `nivel_dificultad`, `duracion`, `herramientas`) VALUES
(36, 'Ramo de 20 Girasoles', 'Ramo grande con 20 girasoles amarillos vibrantes', 67000.00, 'https://lovelyfloweers.com/cdn/shop/files/58c68140-8030-4ccb-910a-489a6e8fdd38.jpg?v=1717342786&width=250', 1, NULL, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(37, 'Ramo de Tulipanes', 'Ramo de 12 tulipanes en varios colores primaverales', 52000.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMcQMK6pym79LKe6Yy7c_6KX6wDFNV2ibZUQ&s', 1, NULL, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(38, 'Ramo de Lirios y Rosas Blancas', 'Combinación de lirios blancos y rosas blancas elegantes', 63000.00, 'https://floresyflores.co/wp-content/uploads/2022/07/IMG_9136-1.jpg', 1, NULL, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(39, 'Frasco de Orquídeas Moradas', 'Ramo de 7 orquídeas moradas de alta gama', 82000.00, 'https://m.media-amazon.com/images/I/71Uf4mQIaEL.jpg', 1, NULL, 1, 1, 5.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(40, 'Ramo de Gerberas Naranjas con rosas', 'Ramo de 10 gerberas naranjas brillantes', 46000.00, 'https://i.pinimg.com/736x/e9/c5/44/e9c544d82767a049ba2f6c546a9d31f4.jpg', 1, NULL, 1, 1, 5.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(41, 'Ramo de Lirios', 'Pequeño ramo con 6 orquides y rosas rosadas', 39000.00, 'https://florerialucilas.com/cdn/shop/files/RamoRosasyLirios.png?v=1750370754', 1, NULL, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(42, 'Ramo de Jazmín Blanco', 'Ramo aromático de jazmín blanco para regalo íntimo', 42000.00, 'https://i.pinimg.com/474x/41/21/08/4121084526444c99f2d7838706f86948.jpg', 1, NULL, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(43, 'Ramo de Flores Silvestres Mix', 'Ramo mixto de flores silvestres de campo', 54000.00, 'https://www.fioroagna.cl/cdn/shop/files/Disenosintitulo_7_580x.png?v=1742223869', 1, NULL, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(44, 'Ramo gigante de Rosas', 'Ramo grande de rosas', 100000.00, 'https://floresyflores.co/wp-content/uploads/2024/06/flores-y-flores-7.jpg', 1, NULL, 0, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(45, 'Ramo de 15 Rosas Rosadas', 'Ramo de 15 rosas de tono rosado suave', 58000.00, 'https://solorosasyalgomas.cl/wp-content/uploads/2023/11/RAMO-DE-12-ROSAS-ROSADAS.png', 1, NULL, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(46, 'Carta con Caligrafía', 'Carta manuscrita con caligrafía artística', 15000.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwUf9NPzzuiMxOyupTAXNR5gJisVUV8J0tGw&s', 2, NULL, 1, 0, 5.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(47, 'Carta Musical', 'Carta con notas musicales para amantes de la musica', 25000.00, 'https://i.ytimg.com/vi/NUf5UyLClYg/sddefault.jpg', 2, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(48, 'Carta Amorosa', 'Carta romántica con sobre decorativo', 12000.00, 'https://cdn0.uncomo.com/es/posts/4/4/0/cartas_de_amor_romanticas_para_mi_novio_49044_0_600.jpg', 2, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(49, 'Carta de Cumpleaños', 'Carta personalizada para cumpleaños', 18000.00, 'https://i.ytimg.com/vi/moUmz-WzQ1A/maxresdefault.jpg', 2, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(50, 'Carta de Agradecimiento', 'Carta de agradecimiento elegante', 15000.00, 'https://images.unsplash.com/photo-1607582270286-0ee0422f290e?auto=format&fit=crop&w=800&q=80', 2, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(51, 'Carta Futbolera', 'Carta inspirada en el futbol, con un balon en foami ', 14000.00, 'https://i.etsystatic.com/36715963/r/il/b29822/5070246825/il_300x300.5070246825_k4o8.jpg', 2, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(52, 'Carta Divertida de zorro', 'Carta con diseño divertido y colorido anaranjado', 13000.00, 'https://st.depositphotos.com/27821720/54716/v/450/depositphotos_547162518-stock-illustration-cute-lovely-fox-letter-writing.jpg', 2, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(53, 'Combo Primavera', 'Combo de utiles primavera de cartilla y colores', 65000.00, 'https://tiendauniversal.com/cdn/shop/files/7707463690047_1.jpg?v=1761561567', 3, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(54, 'Combo Rosas y Materiales', 'materiales necesarios para rosas de papel', 72000.00, 'https://www.pequeocio.com/wp-content/uploads/2013/04/como-hacer-una-rosa-de-papel.jpg', 3, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(55, 'Combo Tulipanes y Carta', 'Materiales para carta + tulipanes de papel', 60000.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQVua27UFqPStjFFbXmsXWnOIVo49ZWa1gqKw&s', 3, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(56, 'Papel de Regalo Estampado', 'Hojas de papel decorativo para envolver regalos', 2000.00, 'https://www.google.com/search?q=Papel+de+Regalo+Estampado&ie=UTF-8#vhid=ocIIiZSRSlp2gM&vssid=_S7YVacWKLc2NwbkP78eVyQ0_51', 5, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(57, 'Cinta Decorativa Azul', 'Cinta de 3 metros color azul', 3000.00, 'https://w7.pngwing.com/pngs/1010/557/png-transparent-white-and-green-pattern-graphics-blue-ribbon-baby-blue-decorative-ribbon-blue-ribbon-text.png', 5, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(58, 'Cinta Decorativa Roja', 'Cinta de 3 metros color rojo', 3000.00, 'https://bombay.net.co/sitio/wp-content/smush-webp/2023/10/77010301EK05.jpg.webp', 5, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(59, 'Cartulina Multicolor', 'Set de cartulinas de colores variados', 5000.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRvrBzfQoEWzoB4EhF3rkKMH6TzOIRGAJLLTw&s', 5, NULL, 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(60, 'Videotutorial Ramos Artificiales Básico', 'Cómo hacer un ramo de flores artificiales paso a paso', 0.00, 'https://imgs.search.brave.com/OLFVF9hfZtaNANENXcs3vJ6CxVwssP4-S8ZKCYYR-9E/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pLnl0/aW1nLmNvbS92aS9W/YjZHd216eTVFTS9t/YXhyZXNkZWZhdWx0/LmpwZw', 4, NULL, 1, 1, NULL, 'Sigue el video; recorta flores, agrupa, ata con cinta.', 'premium', 'https://www.youtube.com/watch?v=Vb6Gwmzy5EM', NULL, 'intermedio', '≈ 10 min', 'flores artificiales, cinta, tijeras, alambre'),
(61, 'Videotutorial Flor de Loto', 'Tutorial para crear flores de loto', 0.00, 'https://i.ytimg.com/vi/NzZNP5i1NLI/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLBnZgYvm55Y5bRviAjjxAkQpltEmA', 4, NULL, 1, 1, 4.00, 'Usa pegamento y origame del color de tu eleccion.', 'publico', 'https://www.youtube.com/watch?v=NzZNP5i1NLI', NULL, 'avanzado', '≈ 15 min', 'cartulina, pegamento, alambre, cinta'),
(62, 'Videotutorial Caligrafía de Cartas Principiantes', 'Aprende caligrafía para escribir cartas manuscritas con estilo', 0.00, 'https://imgs.search.brave.com/lWJe9nOrmb1j5Tekcq1dEbBHR0Dk-i_bz0X4qCBned0/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pLnl0/aW1nLmNvbS92aS9J/c2pnY0RId1RfNC9o/cWRlZmF1bHQuanBn/P3NxcD0tb2F5bXdF/bUNPQURFT2dDOHF1/S3FRTWE4QUVCLUFI/T0JZQUNoQWVLQWd3/SUFCQUJHR1VnVHlo/Qk1BOD0mcnM9QU9u/NENMRFY2Q0VCa3VC/WHNKY05wTlNITzNa/RVc4ZzdRUQ', 4, NULL, 1, 1, NULL, 'Practica trazos básicos y luego escribe tu carta.', 'publico', 'https://www.youtube.com/watch?v=IsjgcDHwT_4', NULL, 'basico', '2 min', 'pluma de punta, papel, tinta, hoja de práctica'),
(63, 'Carta con Forma de Gato', 'Moldea tu carta con la apariencia de un gatito!', 0.00, 'https://imgs.search.brave.com/_1LK5ejQNmspU1ySDpv3kOijeUVUcydFaaqpwAaayvE/rs:fit:200:200:1:0/g:ce/aHR0cHM6Ly9pLnl0/aW1nLmNvbS92aS96/TXQ3WkgxZy1tTS9t/YXhyZXNkZWZhdWx0/LmpwZw', 4, NULL, 1, 1, NULL, 'Explora estilos modernos, sombras y mezcla de pinceles.', 'publico', 'youtube.com/watch?v=zMt7ZH1g-mM', NULL, 'avanzado', '≈ 20 min', 'pinceles de lettering, cartulina, marcadores, regla'),
(64, ' Solicitud pra epoca navideña', 'nuevo video', 0.00, '/static/img/20251113082400_descarga_1.jpg', 4, 18, 1, 0, NULL, 'uygefwgfiyweguf', 'publico', '', '20251113082400_Video_de_WhatsApp_2025-11-13_a_las_02.11.56_f53be4c0.mp4', 'Intermedio', '5 MINUTOS', 'TIJERITAS CINTA PALOS'),
(65, 'ayuda mk', 'aaaaaaaaaaaaa', 0.00, '/static/img/20251113195751_IMG_4879.PNG', 4, 19, 1, 0, 3.00, 'pipipipi', 'publico', '', '20251113195030_v09044g40000cecgbfbc77u1v1j2qsv0.mp4', 'Intermedio', '10 ', 'Tijeras, Cartulina, Cinta'),
(73, 'ramo de flores variado', 'fsabjhdfhbjad', 50000.00, '/static/img/20251126113032_sensores-de-agua-removebg-preview.png', 1, 14, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(74, 'sisas chechin', 'chechito', 0.00, '/static/img/20251126113127_descarga_1.jpg', 4, 14, 1, 0, NULL, 'i¿uifdsuifnsdionvewo', 'publico', '', '20251126113127_Video_de_WhatsApp_2025-11-13_a_las_02.11.56_f53be4c0.mp4', 'Intermedio', '10', 'cinta tijeras y limpiapipas'),
(75, 'flores ', 'iudashiojidfjiefad', 0.00, '/static/img/20251126114236_Exotic-Blue-Roses-Bouquet-400x400.jpg', 4, 14, 1, 0, NULL, 'ijjciweomciowenciow', 'premium', '', '20251126114236_Rocket_League-2025_06_21-02_01_57.mp4', 'Intermedio', '10 min', 'tijeres, cintas y flores'),
(76, 'Ramo buchon de 100 rosas ', 'Hermoso ramo de 100 rosas para cualquier ocasion', 200000.00, '/static/img/20251126115705_bouquet_grande_de_rosas_rojas__3.jpg', 1, 20, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

--
-- Disparadores `productos`
--
DELIMITER $$
CREATE TRIGGER `backup_productos` AFTER DELETE ON `productos` FOR EACH ROW BEGIN
    INSERT INTO productos_eliminados (
        id_producto,
        nombre,
        descripcion,
        precio,
        id_categoria,
        id_vendedor,
        fecha_eliminado
    ) VALUES (
        OLD.id_producto,
        OLD.nombre,
        OLD.descripcion,
        OLD.precio,
        OLD.id_categoria,
        OLD.id_vendedor,
        NOW()
    );
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos_eliminados`
--

CREATE TABLE `productos_eliminados` (
  `id_producto` int(11) DEFAULT NULL,
  `nombre` varchar(150) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_vendedor` int(11) DEFAULT NULL,
  `fecha_eliminado` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos_eliminados`
--

INSERT INTO `productos_eliminados` (`id_producto`, `nombre`, `descripcion`, `precio`, `id_categoria`, `id_vendedor`, `fecha_eliminado`) VALUES
(23, 'carta', 'carta', 200.00, 2, 14, '2025-11-13 01:38:24'),
(22, 'carta', 'carta', 200.00, 2, 6, '2025-11-13 01:38:26'),
(21, 'carta', 'carta', 200.00, 2, 6, '2025-11-13 01:38:29'),
(34, 'sisasmillitos', 'sadadsdadfdaf', 0.00, 4, 16, '2025-11-13 05:23:26'),
(24, 'Ramo de Rosas Rojas', 'Ramo de 12 rosas rojas frescas', 55000.00, 1, 6, '2025-11-13 10:52:48'),
(25, 'Ramo de Girasoles', 'Ramo de 8 girasoles amarillos brillantes', 45000.00, 1, 9, '2025-11-13 10:52:55'),
(27, 'Carta Musical', 'Carta con QR que reproduce una canción', 25000.00, 2, 6, '2025-11-13 10:53:05'),
(29, 'Tutorial Flores Amarillas', 'Videotutorial de cómo armar ramos de girasoles', 20000.00, 4, 6, '2025-11-13 10:53:16'),
(30, 'Tutorial Ramos Profesionales', 'Curso avanzado de ramos para eventos', 60000.00, 4, 6, '2025-11-13 10:53:20'),
(32, 'Cinta Decorativa Azul', 'Cinta de 3 metros color azul', 3000.00, 5, 6, '2025-11-13 10:53:25'),
(33, 'Palo de Balso', 'Palo de madera para soporte de arreglos', 1500.00, 5, 6, '2025-11-13 10:53:28'),
(26, 'Carta con Caligrafía', 'Carta manuscrita con caligrafía artística', 15000.00, 2, 9, '2025-11-13 11:02:58'),
(28, 'Combo Primavera', 'Incluye ramo de girasoles + carta personalizada', 65000.00, 3, 6, '2025-11-13 11:03:00'),
(31, 'Papel de Regalo Estampado', 'Hoja de papel decorativo para envolver', 2000.00, 5, 6, '2025-11-13 11:03:02'),
(35, ':,v', 'adadda', 0.00, 4, 16, '2025-11-13 11:03:40'),
(67, 'intento2', 'aaaaaaasdafdf', 1000.00, 1, 19, '2025-11-14 04:22:57'),
(69, 'ayudaaaaaaaaaaaa', 'sadad', 120000.00, 1, 19, '2025-11-17 21:51:22'),
(70, 'otra vez esta mrd', 'afdadffaf', 120000.00, 1, 19, '2025-11-17 21:54:18'),
(66, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'asfdaf', 122000.00, 1, 19, '2025-11-17 21:54:22'),
(72, '17/11Johann', 'asdadasd', 211000.00, 1, 20, '2025-11-26 16:53:17'),
(68, ':,vsss', 'dadasd', 0.00, 4, 19, '2025-11-26 17:12:43'),
(71, '17/11sisas', 'aaaaadwq2', 10000.00, 1, 19, '2025-11-26 17:12:48');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto_relacion`
--

CREATE TABLE `producto_relacion` (
  `id_producto_padre` int(11) NOT NULL,
  `id_producto_hijo` int(11) NOT NULL,
  `cantidad` decimal(10,2) DEFAULT NULL,
  `unidad` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id_rol`, `nombre`, `descripcion`) VALUES
(1, 'Usuario', 'Cliente que compra, crea y vende productos, tutoriales, combos, etc.'),
(2, 'Administrador', 'Gestión de usuarios, productos y reportes');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitudes`
--

CREATE TABLE `solicitudes` (
  `id_solicitud` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_vendedor` int(11) DEFAULT NULL,
  `id_producto` int(11) NOT NULL,
  `id_detalle` int(11) DEFAULT NULL,
  `estado` enum('pendiente','en_revision','cotizado','finalizado','cancelado') NOT NULL DEFAULT 'pendiente',
  `detalles_adicionales` text DEFAULT NULL,
  `feedback_vendedor` text DEFAULT NULL,
  `fecha_solicitud` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `solicitudes`
--

INSERT INTO `solicitudes` (`id_solicitud`, `id_usuario`, `id_vendedor`, `id_producto`, `id_detalle`, `estado`, `detalles_adicionales`, `feedback_vendedor`, `fecha_solicitud`) VALUES
(15, 20, 19, 71, 27, '', 'Boceto subido: IMG_2024.PNG', 'bueno', '2025-11-17 18:18:46'),
(16, 19, 20, 72, 29, 'cotizado', 'Personalización de plantilla guardada (Detalle ID: 29)', 'de una', '2025-11-17 19:02:17'),
(17, 14, 19, 71, 30, '', 'Boceto subido: descarga_1.jpg', 'iuwfehfduudsfsdf', '2025-11-21 17:50:14'),
(18, 14, 20, 72, 31, 'cotizado', 'Boceto subido: sensores-de-agua-removebg-preview.png', 'aaaarerwrw', '2025-11-21 17:59:35'),
(19, 19, 20, 76, 37, '', 'Formulario Completado: Día de la Madre - 2025-11-30', 'claro puede ser posible, sin embargo el precio aumentara 50k', '2025-11-26 12:34:11');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sugerencias`
--

CREATE TABLE `sugerencias` (
  `id_sugerencia` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `titulo` varchar(150) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_envio` date DEFAULT NULL,
  `estado` enum('pendiente','aceptada','rechazada') NOT NULL DEFAULT 'pendiente',
  `retroalimentacion` text DEFAULT NULL,
  `likes` int(11) NOT NULL DEFAULT 0,
  `dislikes` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sugerencias`
--

INSERT INTO `sugerencias` (`id_sugerencia`, `id_usuario`, `titulo`, `descripcion`, `fecha_envio`, `estado`, `retroalimentacion`, `likes`, `dislikes`) VALUES
(3, 14, 'un menu mas bonito', 'mejorar el menu del inico que sea mas bonito', '2025-11-10', 'aceptada', 'ioemiow', 2, 0),
(4, 18, 'mejorar la calidad de los ramos', 'el material esta de mala calidad', '2025-11-13', 'rechazada', NULL, 0, 0),
(5, 18, 'Solicitud pra epoca navideña', 'unos regalos personalizados para la epoca navideña que aperezcan en la pagina principal', '2025-11-13', 'aceptada', 'dijeojdwodjw', 1, 0),
(6, 18, 'aa', 'aa', '2025-11-13', '', NULL, 0, 0),
(7, 20, 'Solicitud pra epoca navideña', 'chimba de deatlles', '2025-11-26', 'aceptada', '', 1, 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sugerencias_votos`
--

CREATE TABLE `sugerencias_votos` (
  `id_voto` int(11) NOT NULL,
  `id_sugerencia` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `tipo` enum('like','dislike') NOT NULL,
  `fecha_voto` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sugerencias_votos`
--

INSERT INTO `sugerencias_votos` (`id_voto`, `id_sugerencia`, `id_usuario`, `tipo`, `fecha_voto`) VALUES
(1, 3, 14, 'like', '2025-11-10 01:28:13'),
(2, 3, 18, 'like', '2025-11-13 07:47:41'),
(3, 5, 20, 'like', '2025-11-26 11:48:58'),
(4, 7, 14, 'like', '2025-11-26 12:07:49');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `suscripciones`
--

CREATE TABLE `suscripciones` (
  `id_suscripcion` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `id_tipo_suscripcion` int(11) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `comprobante` varchar(255) DEFAULT NULL,
  `estado` enum('pendiente','aprobada','rechazada','vencida') DEFAULT 'pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `suscripciones`
--

INSERT INTO `suscripciones` (`id_suscripcion`, `id_usuario`, `id_tipo_suscripcion`, `fecha_inicio`, `fecha_fin`, `comprobante`, `estado`) VALUES
(15, 15, 1, '2025-11-03', '2025-12-03', 'user_15_backiee-108233.jpg', 'vencida'),
(17, 18, 1, '2025-11-13', '2025-12-13', 'user_18_descarga (1).jpg', 'pendiente'),
(18, 14, 1, '2025-12-05', '2026-01-04', 'user_14_backiee-108233.jpg', 'pendiente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_suscripcion`
--

CREATE TABLE `tipo_suscripcion` (
  `id_tipo_suscripcion` int(11) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `precio_mensual` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_suscripcion`
--

INSERT INTO `tipo_suscripcion` (`id_tipo_suscripcion`, `nombre`, `descripcion`, `precio_mensual`) VALUES
(1, 'Básica', 'Acceso a 2 tutoriales al mes', 15000.00),
(2, 'Premium', 'Acceso ilimitado a tutoriales + descuentos en productos', 30000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre_completo` varchar(150) NOT NULL,
  `correo_electronico` varchar(100) NOT NULL,
  `contraseña` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` text DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `id_rol` int(11) DEFAULT 1,
  `codigo_reset` varchar(10) DEFAULT NULL,
  `expira_reset` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre_completo`, `correo_electronico`, `contraseña`, `telefono`, `direccion`, `fecha_registro`, `id_rol`, `codigo_reset`, `expira_reset`, `is_active`) VALUES
(6, 'Catalina Nova', 'CatalinaN@gmail.com', '123456789000', '3006666666', 'Calle 87 #12-34', '2025-09-14 15:23:34', 1, NULL, NULL, 1),
(7, 'Valentina Rodriguez', 'ValentinaR@gmail.com', '1234567890000', '3007777777', 'Av 30 #15-40', '2025-09-14 15:23:34', 1, NULL, NULL, 1),
(8, 'Jostin Suarez', 'JostinS@gmail.com', '11234567890', '3008888888', 'Carrera 14 #61-90', '2025-09-14 15:23:34', 1, NULL, NULL, 1),
(9, 'Danna Albino', 'DannaA@gmail.com', '111234567890', '3009999999', 'Carrera #11-39', '2025-09-14 15:23:34', 1, NULL, NULL, 1),
(10, 'Felipe Nova', 'felnov@gmail.com', 'scrypt:32768:8:1$XFnBNa46iHIsdoeq$b0f19ce2d7d6ed170d3377462591b76e1ffe05606327424816b3dfb11be5078a4f6176f9ccc28fd60dc8216a817572251b25238bb889907c545afd471e59016b', '3214567890', NULL, '2025-09-14 15:30:12', 1, NULL, NULL, 1),
(11, 'administrador', 'admin@gmail.com', 'scrypt:32768:8:1$6rbGJP63ALBIAaiP$c7802d3aac0d18f26533f9ff49423cb8b4b6fd36a258eb52f6e7b464a66d4a1dc58e699ff2f180938560482a3512691f3c65240aa66deb2ec34537fbe2df6279', '3456578905', NULL, '2025-09-15 19:31:21', 2, '896999', '2025-11-02 17:24:11', 1),
(12, 'copetin', 'copetin21@gmail.com', 'scrypt:32768:8:1$9qvGGsVBxmGGriou$05dee17be2ecfb086c7a6bec6e246329b9fa14c23d6c7c1d7e52e38bdecbd69dfa3465eaca0867d42e79bd1e0b6e604516767553c8cf919b4b85a0a03a2ca41e', '3214768909', NULL, '2025-09-16 08:52:53', 1, NULL, NULL, 1),
(14, 'Dylan', 'dgalindonova@gmail.com', 'scrypt:32768:8:1$90HEx7RSRbKHnb68$59b9fd48de87ea816414bbd20feb7aac2df9a793875ea60f57a294ba4b2a6f2e1b3ebc1e7caf4e56cc32b2d081cf2432a0b76c9975861cc069b16f2f560e0234', '3114893401', 'carrera 69 p bis # 73 a 42', '2025-10-02 09:59:33', 2, NULL, NULL, 1),
(15, 'Stiwar', 'stiwar@gmail.com', 'scrypt:32768:8:1$5r9u2vWQKciowxA1$a2666a2b683730dee1bdb9073c3248abc491a90468d5a48936952f0f0b410dc2ce6e307594e77dc430a22c08d016314bc151d00430d9d8745a7f9c15d6dcb3df', '3004444323', 'carrera 7 #73 a42', '2025-11-03 17:21:59', 1, NULL, NULL, 1),
(18, 'Paola Ballen', 'profepaolaballen@gmail.com', 'scrypt:32768:8:1$k7n0RZHuxoLlVBa2$8c8b292379be6fd14849012c0cb61eb87a24d77a86fa07e67766fb637960a77f913688d3bc37215994053af872d08f136b7e74fb3e752cc7ee0d8bd98691e051', '3334567890', 'carrera 68 # 73 a 43', '2025-11-13 07:01:31', 1, NULL, NULL, 1),
(19, 'sisaschechin', 'johannleon2007@gmail.com', 'scrypt:32768:8:1$qvHzyW1Z1bhf4Rad$2432bd5856702019185cc7e0c6f1f4d46800832a0605392cc89ba5d7ce2e26726b171e95a53f6073216a84f5fb31899b08dc7c93074260d8cf0f2a49f326117c', '3128622177', '', '2025-11-13 17:42:05', 1, NULL, NULL, 1),
(20, 'Johann', 'leonjohann2707@gmail.com', 'scrypt:32768:8:1$1RVa4cxqJbHQkqXF$88952899542e37a41501c49805981a8dd05b80607fd437b3b290b110860ca6ffc6c13b2b1cf864811844bb5f5993289c2134be25f73c560f242f349061f064ea', '3137682522', NULL, '2025-11-14 04:11:03', 1, NULL, NULL, 1);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_calendario_eventos`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_calendario_eventos` (
`id_evento` int(11)
,`usuario` varchar(150)
,`nombre_evento` varchar(150)
,`descripcion` text
,`fecha_evento` date
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_calificaciones_productos`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_calificaciones_productos` (
`producto` varchar(150)
,`puntuacion` decimal(2,1)
,`comentario` text
,`usuario` varchar(150)
,`fecha_calificacion` datetime
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vista_pedidos_clientes`
--

CREATE TABLE `vista_pedidos_clientes` (
  `id_pedido` int(11) DEFAULT NULL,
  `cliente` varchar(150) DEFAULT NULL,
  `estado` enum('pendiente','pagado','enviado','entregado','cancelado') DEFAULT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `fecha_pedido` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vista_pedidos_domicilio`
--

CREATE TABLE `vista_pedidos_domicilio` (
  `id_pedido` int(11) DEFAULT NULL,
  `cliente` varchar(150) DEFAULT NULL,
  `direccion_envio` text DEFAULT NULL,
  `fecha_envio` date DEFAULT NULL,
  `estado_envio` enum('pendiente','en camino','entregado','cancelado') DEFAULT NULL,
  `empresa_transportadora` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vista_productos_categorias`
--

CREATE TABLE `vista_productos_categorias` (
  `id_producto` int(11) DEFAULT NULL,
  `nombre` varchar(150) DEFAULT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `vendedor` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vista_sugerencias`
--

CREATE TABLE `vista_sugerencias` (
  `id_sugerencia` int(11) DEFAULT NULL,
  `usuario` varchar(150) DEFAULT NULL,
  `titulo` varchar(150) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_envio` date DEFAULT NULL,
  `estado` enum('pendiente','aceptada','rechazada') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vista_suscripciones`
--

CREATE TABLE `vista_suscripciones` (
  `id_suscripcion` int(11) DEFAULT NULL,
  `usuario` varchar(150) DEFAULT NULL,
  `tipo_suscripcion` varchar(100) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vista_usuarios_roles`
--

CREATE TABLE `vista_usuarios_roles` (
  `id_usuario` int(11) DEFAULT NULL,
  `nombre_completo` varchar(150) DEFAULT NULL,
  `correo_electronico` varchar(100) DEFAULT NULL,
  `rol` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_calendario_eventos`
--
DROP TABLE IF EXISTS `vista_calendario_eventos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_calendario_eventos`  AS SELECT `c`.`id_evento` AS `id_evento`, `u`.`nombre_completo` AS `usuario`, `c`.`nombre_evento` AS `nombre_evento`, `c`.`descripcion` AS `descripcion`, `c`.`fecha_evento` AS `fecha_evento` FROM (`calendario` `c` join `usuarios` `u` on(`c`.`id_usuario` = `u`.`id_usuario`)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_calificaciones_productos`
--
DROP TABLE IF EXISTS `vista_calificaciones_productos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_calificaciones_productos`  AS SELECT `p`.`nombre` AS `producto`, `c`.`puntuacion` AS `puntuacion`, `c`.`comentario` AS `comentario`, `u`.`nombre_completo` AS `usuario`, `c`.`fecha_calificacion` AS `fecha_calificacion` FROM ((`calificaciones` `c` join `productos` `p` on(`c`.`id_producto` = `p`.`id_producto`)) join `usuarios` `u` on(`c`.`id_usuario` = `u`.`id_usuario`)) ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `calificaciones`
--
ALTER TABLE `calificaciones`
  ADD PRIMARY KEY (`id_calificacion`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `detalle_pedido`
--
ALTER TABLE `detalle_pedido`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `id_pedido` (`id_pedido`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `domicilio`
--
ALTER TABLE `domicilio`
  ADD PRIMARY KEY (`id_domicilio`),
  ADD KEY `id_pedido` (`id_pedido`);

--
-- Indices de la tabla `donaciones`
--
ALTER TABLE `donaciones`
  ADD PRIMARY KEY (`id_donacion`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `favoritos`
--
ALTER TABLE `favoritos`
  ADD PRIMARY KEY (`id_favorito`),
  ADD UNIQUE KEY `id_usuario` (`id_usuario`,`id_producto`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `material_audiovisual`
--
ALTER TABLE `material_audiovisual`
  ADD PRIMARY KEY (`id_material_audiovisual`),
  ADD KEY `id_producto` (`id_producto`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id_notificacion`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id_pedido`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `pqr`
--
ALTER TABLE `pqr`
  ADD PRIMARY KEY (`id_pqr`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `id_categoria` (`id_categoria`),
  ADD KEY `id_vendedor` (`id_vendedor`);

--
-- Indices de la tabla `producto_relacion`
--
ALTER TABLE `producto_relacion`
  ADD PRIMARY KEY (`id_producto_padre`,`id_producto_hijo`),
  ADD KEY `id_producto_hijo` (`id_producto_hijo`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  ADD PRIMARY KEY (`id_solicitud`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_vendedor` (`id_vendedor`),
  ADD KEY `id_producto` (`id_producto`),
  ADD KEY `id_detalle` (`id_detalle`);

--
-- Indices de la tabla `sugerencias`
--
ALTER TABLE `sugerencias`
  ADD PRIMARY KEY (`id_sugerencia`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `sugerencias_votos`
--
ALTER TABLE `sugerencias_votos`
  ADD PRIMARY KEY (`id_voto`),
  ADD UNIQUE KEY `id_sugerencia` (`id_sugerencia`,`id_usuario`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `suscripciones`
--
ALTER TABLE `suscripciones`
  ADD PRIMARY KEY (`id_suscripcion`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_tipo_suscripcion` (`id_tipo_suscripcion`);

--
-- Indices de la tabla `tipo_suscripcion`
--
ALTER TABLE `tipo_suscripcion`
  ADD PRIMARY KEY (`id_tipo_suscripcion`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `correo_electronico` (`correo_electronico`),
  ADD KEY `fk_usuario_rol` (`id_rol`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `calificaciones`
--
ALTER TABLE `calificaciones`
  MODIFY `id_calificacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `detalle_pedido`
--
ALTER TABLE `detalle_pedido`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT de la tabla `domicilio`
--
ALTER TABLE `domicilio`
  MODIFY `id_domicilio` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `donaciones`
--
ALTER TABLE `donaciones`
  MODIFY `id_donacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `favoritos`
--
ALTER TABLE `favoritos`
  MODIFY `id_favorito` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `material_audiovisual`
--
ALTER TABLE `material_audiovisual`
  MODIFY `id_material_audiovisual` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id_notificacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id_pedido` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `pqr`
--
ALTER TABLE `pqr`
  MODIFY `id_pqr` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  MODIFY `id_solicitud` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `sugerencias`
--
ALTER TABLE `sugerencias`
  MODIFY `id_sugerencia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `sugerencias_votos`
--
ALTER TABLE `sugerencias_votos`
  MODIFY `id_voto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `suscripciones`
--
ALTER TABLE `suscripciones`
  MODIFY `id_suscripcion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `tipo_suscripcion`
--
ALTER TABLE `tipo_suscripcion`
  MODIFY `id_tipo_suscripcion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `donaciones`
--
ALTER TABLE `donaciones`
  ADD CONSTRAINT `donaciones_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `pqr`
--
ALTER TABLE `pqr`
  ADD CONSTRAINT `pqr_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
