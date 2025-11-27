-- ===========================================
--  TABLAS DE CATÁLOGOS
-- ===========================================

CREATE TABLE Genero (
    ID_Genero SERIAL PRIMARY KEY,
    Genero VARCHAR(20) NOT NULL
);

CREATE TABLE Roles (
    ID_Rol SERIAL PRIMARY KEY,
    Rol VARCHAR(20) NOT NULL
);

-- ===========================================
--  TABLA USUARIO
-- ===========================================

CREATE TABLE Usuario (
    ID_Usuario SERIAL PRIMARY KEY,
    ID_Genero INT REFERENCES Genero(ID_Genero),
    Nombre VARCHAR(20) NOT NULL,
    Apellido1 VARCHAR(50) NOT NULL,
    Apellido2 VARCHAR(50),
    Fecha_Nacimiento DATE,
    Correo VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(200) NOT NULL,
    Estado VARCHAR(20),
    FechaCreacion DATE DEFAULT CURRENT_DATE,
    FechaActualizacion DATE,
    FechaEliminacion DATE
);

-- ===========================================
--  RELACIÓN USUARIO–ROL (TABLA PUENTE)
-- ===========================================

CREATE TABLE UserRol (
    ID_UserRol SERIAL PRIMARY KEY,
    ID_Usuario INT NOT NULL REFERENCES Usuario(ID_Usuario),
    ID_Rol INT NOT NULL REFERENCES Roles(ID_Rol)
);

-- ===========================================
--  TABLAS DE RANGOS (SIN CAMBIOS)
-- ===========================================

CREATE TABLE RangoColesterol (
    ID_RangoColesterol SERIAL PRIMARY KEY,
    CodigoRangoColesterol INT,
    Min FLOAT,
    Max FLOAT,
    VersionModelo VARCHAR(10)
    Descripcion VARCHAR(20),
);

CREATE TABLE RangoGlucosa (
    ID_RangoGlucosa SERIAL PRIMARY KEY,
    CodigoRangoGlucosa INT,
    Min FLOAT,
    Max FLOAT,
    VersionModelo VARCHAR(10)
    Descripcion VARCHAR(20),
);

CREATE TABLE RangoIMC (
    ID_RangoIMC SERIAL PRIMARY KEY,
    CodigoRangoIMC INT,
    Min FLOAT,
    Max FLOAT,
    VersionModelo VARCHAR(10)
    Descripcion VARCHAR(20),
);

CREATE TABLE RangoPresionSanguinea (
    ID_RangoPresionSanguinea SERIAL PRIMARY KEY,
    CodigoRangoColesterol INT,
    Min FLOAT,
    Max FLOAT,
    VersionModelo VARCHAR(10),
    Descripcion VARCHAR(20),
);

-- ===========================================
--  TABLA CITA MÉDICA (SEGÚN TU DIAGRAMA)
-- ===========================================

CREATE TABLE Cita_Medica (
    ID_Cita SERIAL PRIMARY KEY,

    ID_Paciente INT NOT NULL REFERENCES Usuario(ID_Usuario),
    ID_Doctor INT NOT NULL REFERENCES Usuario(ID_Usuario),

    ID_RangoColesterol INT REFERENCES RangoColesterol(ID_RangoColesterol),
    ID_RangoGlucosa INT REFERENCES RangoGlucosa(ID_RangoGlucosa),
    ID_RangoPresionSanguinea INT REFERENCES RangoPresionSanguinea(ID_RangoPresionSanguinea),
    ID_RangoIMC INT REFERENCES RangoIMC(ID_RangoIMC),

    Peso FLOAT,
    Estatura FLOAT,
    Fecha_Cita DATE,
    Notas VARCHAR(255),

    Alcohol BOOLEAN,
    Drogas BOOLEAN,
    Actividad_Fisica BOOLEAN,
    Fumador BOOLEAN,
    EnfermedadCardiovascular FLOAT,

    FechaCreacion DATE DEFAULT CURRENT_DATE,
    FechaActualizacion DATE,
    FechaEliminacion DATE,
    Estado VARCHAR(20)
);

-- ===========================================
--  ÍNDICES RECOMENDADOS PARA OPTIMIZAR CONSULTAS
-- ===========================================

CREATE INDEX idx_cita_paciente ON Cita_Medica(ID_Paciente);
CREATE INDEX idx_cita_doctor   ON Cita_Medica(ID_Doctor);




INSERT INTO rangocolesterol (id_rangocolesterol, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (1, 1, 0, 100, '1.0', 'Óptimo');
INSERT INTO rangocolesterol (id_rangocolesterol, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (2, 2, 100, 130, '1.0', 'Poco Elevado');
INSERT INTO rangocolesterol (id_rangocolesterol, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (3, 3, 130, 160, '1.0', 'Límite Alto');
INSERT INTO rangocolesterol (id_rangocolesterol, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (4, 4, 160, 190, '1.0', 'Alto');
INSERT INTO rangocolesterol (id_rangocolesterol, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (5, 5, 190, 999, '1.0', 'Muy Alto');


INSERT INTO rangoglucosa (id_rangoglucosa, codigorangoglucosa, min, max, versionmodelo, descripcion) VALUES (1, 1, 0, 100, '1.0', 'Normal');
INSERT INTO rangoglucosa (id_rangoglucosa, codigorangoglucosa, min, max, versionmodelo, descripcion) VALUES (2, 2, 100, 126, '1.0', 'Prediabetes');
INSERT INTO rangoglucosa (id_rangoglucosa, codigorangoglucosa, min, max, versionmodelo, descripcion) VALUES (3, 3, 126, 200, '1.0', 'Diabetes Probable');
INSERT INTO rangoglucosa (id_rangoglucosa, codigorangoglucosa, min, max, versionmodelo, descripcion) VALUES (4, 4, 200, 999, '1.0', 'Hiperglucemia');

INSERT INTO rangoimc (id_rangoimc, codigorangoimc, min, max, versionmodelo, descripcion) VALUES (1, 1, 0, 18.5, '1.0', 'Peso bajo');
INSERT INTO rangoimc (id_rangoimc, codigorangoimc, min, max, versionmodelo, descripcion) VALUES (2, 2, 18.5, 25, '1.0', 'Peso Normal');
INSERT INTO rangoimc (id_rangoimc, codigorangoimc, min, max, versionmodelo, descripcion) VALUES (3, 3, 25, 30, '1.0', 'Sobrepeso');
INSERT INTO rangoimc (id_rangoimc, codigorangoimc, min, max, versionmodelo, descripcion) VALUES (4, 4, 30, 35, '1.0', 'Obesidad Clase 1');
INSERT INTO rangoimc (id_rangoimc, codigorangoimc, min, max, versionmodelo, descripcion) VALUES (5, 5, 35, 40, '1.0', 'Obesidad Clase 2');
INSERT INTO rangoimc (id_rangoimc, codigorangoimc, min, max, versionmodelo, descripcion) VALUES (6, 6, 40, 999, '1.0', 'Obesidad Clase 3');

INSERT INTO rangopresionsanguinea (id_rangopresionsanguinea, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (1, 1, 0, 120, '1.0', 'Normal');
INSERT INTO rangopresionsanguinea (id_rangopresionsanguinea, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (2, 2, 120, 130, '1.0', 'Elevada');
INSERT INTO rangopresionsanguinea (id_rangopresionsanguinea, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (3, 3, 130, 140, '1.0', 'HTA Estadio 1');
INSERT INTO rangopresionsanguinea (id_rangopresionsanguinea, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (4, 4, 140, 180, '1.0', 'HTA Estadio 2');
INSERT INTO rangopresionsanguinea (id_rangopresionsanguinea, codigorangocolesterol, min, max, versionmodelo, descripcion) VALUES (5, 5, 180, 320, '1.0', 'Crisis Hipertensiva');