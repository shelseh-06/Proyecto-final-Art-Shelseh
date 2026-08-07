-- ========================================
-- Base de datos: ART SHELSEH
-- ========================================

CREATE DATABASE IF NOT EXISTS art_shelseh CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE art_shelseh;

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    categoria_id INT,
    imagen VARCHAR(300),
    badge VARCHAR(50),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL,
    tipo VARCHAR(100),
    descripcion TEXT,
    telefono VARCHAR(20),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Datos iniciales
-- ========================================

-- Categorías
INSERT INTO categorias (nombre) VALUES ('Maquetas'), ('Manualidades');

-- Productos
INSERT INTO productos (nombre, descripcion, precio, categoria_id, imagen, badge) VALUES
('Maqueta del Sistema Solar', 'Maqueta educativa del sistema solar con planetas pintados a mano y detalles orbitales.', 85000.00, 1, 'img/Maqueta del sistema solar.jpeg', 'Popular'),
('Cartelera: El Romanticismo', 'Cartelera decorativa sobre el movimiento romántico con ilustraciones y textos detallados.', 42000.00, 2, 'img/Cartelera sobre el romanticismo.jpeg', 'Nuevo'),
('Cartelera: Buenos Modales', 'Cartelera educativa sobre etiqueta y buenos modales con diseño colorido y llamativo.', 38000.00, 2, 'img/Cartelera sobre los buenos modales.jpeg', NULL),
('Cartelera: Paulo Freire', 'Cartelera dedicada al pedagogo Paulo Freire con sus principales ideas y aportes.', 40000.00, 2, 'img/Cartelera sobre Paulo Freire.jpeg', NULL),
('Lapbook: Querido Hijo', 'Lapbook interactivo sobre la obra "Querido hijo estamos en huelga" con solapas y textos.', 55000.00, 1, 'img/Lapbook sobre la obra-Querido hijo estamos en huelga.jpeg', NULL),
('Lapbook: Querido Hijo II', 'Segunda parte del lapbook con más detalles, ilustraciones y contenido literario.', 60000.00, 1, 'img/Lapbook sobre la obra-Querido hijo estamos en huelga 2.jpeg', 'Encargo'),
('Portadas de Cuadernos', 'Portadas decorativas y personalizadas para cuadernos, hechas con técnicas manuales.', 25000.00, 2, 'img/Portadas de cuadernos.jpeg', NULL),
('Maqueta Sistema Solar II', 'Vista detallada de la maqueta del sistema solar con acabados en relieve y colores vibrantes.', 90000.00, 1, 'img/Maqueta del sistema solar  2.jpeg', 'Popular');
