-- File: database/init/init.sql

-- Switch to the target database
USE Banco;

-- Create the CuentasAlmacenadas table
CREATE TABLE IF NOT EXISTS CuentasAlmacenadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_cuenta VARCHAR(255) NOT NULL COMMENT 'Type of account object (e.g., Cuenta, CuentaJoven)',
    datos_objeto TEXT NOT NULL COMMENT 'JSON string representing the account object state'
    -- Consider using JSON type if your MariaDB version supports it well and you need JSON-specific functions:
    -- datos_objeto JSON NOT NULL COMMENT 'JSON representation of the account object state'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create the Usuarios table
CREATE TABLE IF NOT EXISTS Usuarios (
    dni_usuario VARCHAR(255) PRIMARY KEY NOT NULL COMMENT 'SHA256 hash of the user DNI',
    contraseña VARCHAR(255) NOT NULL COMMENT 'SHA256 hash of the user password',
    fk_id_cuenta INT NOT NULL COMMENT 'Foreign key linking to the account',
    CONSTRAINT fk_usuario_cuenta FOREIGN KEY (fk_id_cuenta) REFERENCES CuentasAlmacenadas(id)
        ON DELETE CASCADE -- If an account is deleted, delete the user link too
        ON UPDATE CASCADE -- If an account ID changes (unlikely with AUTO_INCREMENT), update the link
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional: Add an index for better performance on foreign key lookups
CREATE INDEX idx_fk_id_cuenta ON Usuarios (fk_id_cuenta);