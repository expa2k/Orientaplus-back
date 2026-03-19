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

CREATE TABLE IF NOT EXISTS areas_profesionales (
    id              INT          NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(100) NOT NULL,
    codigo_riasec   VARCHAR(6)   NOT NULL,
    descripcion     TEXT,
    icono           VARCHAR(50)  DEFAULT NULL,
    activo          TINYINT(1)   NOT NULL DEFAULT 1,

    PRIMARY KEY (id),
    UNIQUE KEY uq_areas_codigo (codigo_riasec)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS carreras (
    id              INT          NOT NULL AUTO_INCREMENT,
    area_id         INT          NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    perfil_riasec   VARCHAR(6)   NOT NULL,
    campo_laboral   TEXT,
    activo          TINYINT(1)   NOT NULL DEFAULT 1,

    PRIMARY KEY (id),
    CONSTRAINT fk_carreras_area FOREIGN KEY (area_id)
        REFERENCES areas_profesionales(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS preguntas_test (
    id              INT          NOT NULL AUTO_INCREMENT,
    bloque          INT          NOT NULL DEFAULT 1,
    tipo            ENUM('likert', 'opcion_multiple') NOT NULL DEFAULT 'likert',
    texto           TEXT         NOT NULL,
    opciones        JSON         DEFAULT NULL,
    dimension_riasec CHAR(1)     NOT NULL,
    orden           INT          NOT NULL DEFAULT 0,
    activo          TINYINT(1)   NOT NULL DEFAULT 1,

    PRIMARY KEY (id),
    INDEX idx_preguntas_bloque (bloque),
    INDEX idx_preguntas_dimension (dimension_riasec)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sesiones_test (
    id              INT          NOT NULL AUTO_INCREMENT,
    usuario_id      INT          NOT NULL,
    estado          ENUM('en_progreso', 'completada', 'abandonada') NOT NULL DEFAULT 'en_progreso',
    bloque_actual   INT          NOT NULL DEFAULT 1,
    vector_riasec   JSON         DEFAULT NULL,
    fecha_inicio    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin       DATETIME     DEFAULT NULL,

    PRIMARY KEY (id),
    CONSTRAINT fk_sesiones_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_sesiones_usuario (usuario_id),
    INDEX idx_sesiones_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS respuestas_test (
    id              INT          NOT NULL AUTO_INCREMENT,
    sesion_id       INT          NOT NULL,
    pregunta_id     INT          NOT NULL,
    valor           VARCHAR(10)  NOT NULL,
    fecha_respuesta DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_respuestas_sesion FOREIGN KEY (sesion_id)
        REFERENCES sesiones_test(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_respuestas_pregunta FOREIGN KEY (pregunta_id)
        REFERENCES preguntas_test(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uq_respuesta_unica (sesion_id, pregunta_id),
    INDEX idx_respuestas_sesion (sesion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
