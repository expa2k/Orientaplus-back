CREATE DATABASE IF NOT EXISTS orientaplus
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE orientaplus;

CREATE TABLE IF NOT EXISTS usuarios (
    id              INT          NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(80)  NOT NULL,
    apellido        VARCHAR(80)  NOT NULL,
    correo          VARCHAR(120) NOT NULL,
    contrasena      VARCHAR(255) NOT NULL,
    rol             ENUM('admin', 'estudiante') NOT NULL DEFAULT 'estudiante',
    activo          TINYINT(1)   NOT NULL DEFAULT 1,
    fecha_registro  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_correo (correo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
