-- File: BBDD/Banco/Banco.sql

-- Crear Bases de Datos (si no existen)
CREATE DATABASE IF NOT EXISTS Banco CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS InventarioDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear Usuarios Específicos (si no existen)
-- ATENCIÓN: Reemplaza 'banco_secret_password' y 'inventario_secret_password' con las contraseñas
-- que pusiste en tu archivo .env. ¡No las hardcodees aquí si puedes evitarlo!
-- Sin embargo, el script de inicialización no tiene acceso directo al .env.
-- Una opción es pasar las passwords como variables de entorno al contenedor mariadb
-- y usarlas en un script .sh que genere este .sql, pero es más complejo.
-- Por simplicidad AHORA, las ponemos aquí, pero considera la alternativa .sh para producción.
CREATE USER IF NOT EXISTS 'banquero'@'%' IDENTIFIED BY 'banco'; -- Usa la password del .env
CREATE USER IF NOT EXISTS 'manager'@'%' IDENTIFIED BY 'inventario'; -- Usa la password del .env

-- Otorgar Permisos Específicos
GRANT SELECT, INSERT, UPDATE, DELETE ON Banco.* TO 'banquero'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON InventarioDB.* TO 'manager'@'%';
-- Si necesitas más permisos (e.g., CREATE TABLE, ALTER TABLE desde la app), añádelos aquí.
-- Evita GRANT ALL PRIVILEGES si no es estrictamente necesario.

-- Aplicar los cambios de privilegios
FLUSH PRIVILEGES;

-- Cambiar a la base de datos del Banco para crear sus tablas
USE Banco;

CREATE TABLE IF NOT EXISTS CuentasAlmacenadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_cuenta VARCHAR(255) NOT NULL,
    datos_objeto TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Usuarios (
    dni_usuario VARCHAR(255) PRIMARY KEY NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    fk_id_cuenta INT NOT NULL,
    CONSTRAINT fk_usuario_cuenta FOREIGN KEY (fk_id_cuenta) REFERENCES CuentasAlmacenadas(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_fk_id_cuenta ON Usuarios (fk_id_cuenta);

-- Cambiar a la base de datos del Inventario para crear sus tablas
USE InventarioDB;

CREATE TABLE IF NOT EXISTS ProductosInventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    precio DECIMAL(10, 2) NOT NULL,
    cantidad INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_precio CHECK (precio >= 0),
    CONSTRAINT chk_cantidad CHECK (cantidad >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE INDEX idx_nombre_producto ON ProductosInventario (nombre);