BEGIN;

-- =========================================================
-- Limpieza opcional (por si re-ejecutas el script)
-- =========================================================
DROP TABLE IF EXISTS "Cita_Medica" CASCADE;
DROP TABLE IF EXISTS "Prediccion" CASCADE;
DROP TABLE IF EXISTS "UserRol" CASCADE;
DROP TABLE IF EXISTS "Usuario" CASCADE;
DROP TABLE IF EXISTS "Roles" CASCADE;
DROP TABLE IF EXISTS "Genero" CASCADE;
DROP TABLE IF EXISTS "RangoColesterol" CASCADE;
DROP TABLE IF EXISTS "RangoGlucosa" CASCADE;

-- =========================================================
-- Catálogos
-- =========================================================
CREATE TABLE "Genero" (
  "ID_Genero"      SERIAL PRIMARY KEY,
  "Genero"         VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE "Roles" (
  "ID_Rol"         SERIAL PRIMARY KEY,
  "Rol"            VARCHAR(20) NOT NULL UNIQUE
);

-- Rangos (para mapear colesterol/glucosa a 1/2/3)
CREATE TABLE "RangoColesterol" (
  "ID_RangoColesterol"       SERIAL PRIMARY KEY,
  "CodigoRangoColesterol"    INT NOT NULL CHECK ("CodigoRangoColesterol" IN (1,2,3)),
  "Min"                      DOUBLE PRECISION NOT NULL,
  "Max"                      DOUBLE PRECISION NOT NULL,
  "VersionModelo"            VARCHAR(10) NOT NULL,
  "Descripcion"              VARCHAR(20) NOT NULL,
  CONSTRAINT "CK_RangoColesterol_MinMax" CHECK ("Min" < "Max")
);

CREATE TABLE "RangoGlucosa" (
  "ID_RangoGlucosa"          SERIAL PRIMARY KEY,
  "CodigoRangoGlucosa"       INT NOT NULL CHECK ("CodigoRangoGlucosa" IN (1,2,3)),
  "Min"                      DOUBLE PRECISION NOT NULL,
  "Max"                      DOUBLE PRECISION NOT NULL,
  "VersionModelo"            VARCHAR(10) NOT NULL,
  "Descripcion"              VARCHAR(20) NOT NULL,
  CONSTRAINT "CK_RangoGlucosa_MinMax" CHECK ("Min" < "Max")
);

-- =========================================================
-- Usuario y relación con roles
-- =========================================================
CREATE TABLE "Usuario" (
  "ID_Usuario"         SERIAL PRIMARY KEY,
  "ID_Genero"          INT NOT NULL,
  "Nombre"             VARCHAR(20) NOT NULL,
  "Apellido1"          VARCHAR(50) NOT NULL,
  "Apellido2"          VARCHAR(50),
  "Fecha_Nacimiento"   DATE NOT NULL,
  "Correo"             VARCHAR(50) NOT NULL,
  "Password"           VARCHAR(200) NOT NULL,
  "Estado"             VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
  "FechaCreacion"      TIMESTAMP NOT NULL DEFAULT NOW(),
  "FechaActualizacion" TIMESTAMP NOT NULL DEFAULT NOW(),
  "FechaEliminacion"   TIMESTAMP NULL,

  CONSTRAINT "FK_Usuario_Genero"
    FOREIGN KEY ("ID_Genero") REFERENCES "Genero"("ID_Genero")
      ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Correo único (clave para login)
CREATE UNIQUE INDEX "UQ_Usuario_Correo" ON "Usuario" ("Correo");

-- Tabla puente UserRol
CREATE TABLE "UserRol" (
  "ID_UserRol"   SERIAL PRIMARY KEY,
  "ID_Usuario"   INT NOT NULL,
  "ID_Rol"       INT NOT NULL,

  CONSTRAINT "FK_UserRol_Usuario"
    FOREIGN KEY ("ID_Usuario") REFERENCES "Usuario"("ID_Usuario")
      ON UPDATE CASCADE ON DELETE CASCADE,

  CONSTRAINT "FK_UserRol_Roles"
    FOREIGN KEY ("ID_Rol") REFERENCES "Roles"("ID_Rol")
      ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT "UQ_UserRol_UsuarioRol" UNIQUE ("ID_Usuario", "ID_Rol")
);

-- =========================================================
-- Predicción
-- =========================================================
CREATE TABLE "Prediccion" (
  "ID_Prediccion"      SERIAL PRIMARY KEY,
  "ProbabilidadRiesgo" DOUBLE PRECISION NOT NULL CHECK ("ProbabilidadRiesgo" >= 0 AND "ProbabilidadRiesgo" <= 100),
  "VersionModelo"      VARCHAR(10) NOT NULL
  -- Recomendación opcional:
  -- ,"FechaPrediccion" TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =========================================================
-- Cita Médica (núcleo)
-- =========================================================
CREATE TABLE "Cita_Medica" (
  "ID_Cita"               SERIAL PRIMARY KEY,

  "ID_Patient"            INT NOT NULL,
  "ID_Doctor"             INT NOT NULL,

  -- Rangos derivados (nullable, porque puedes guardar crudos primero y calcular después)
  "ID_RangoColesterol"    INT NULL,
  "ID_RangoGlucosa"       INT NULL,

  -- Valores crudos capturados
  "Peso"                  DOUBLE PRECISION NULL,
  "Estatura"              DOUBLE PRECISION NULL, -- define convención: cm (recomendado por tu dataset)
  "Fecha_Cita"            DATE NOT NULL DEFAULT CURRENT_DATE,
  "Notas"                 VARCHAR(255) NULL,

  "Alcohol"               BOOLEAN NOT NULL DEFAULT FALSE,
  "Drogas"                BOOLEAN NOT NULL DEFAULT FALSE,
  "Actividad_Fisica"      BOOLEAN NOT NULL DEFAULT FALSE,
  "Fumador"               BOOLEAN NOT NULL DEFAULT FALSE,

  "FechaCreacion"         TIMESTAMP NOT NULL DEFAULT NOW(),
  "FechaActualizacion"    TIMESTAMP NOT NULL DEFAULT NOW(),
  "FechaEliminacion"      TIMESTAMP NULL,
  "Estado"                VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',

  -- Crudos compatibles con el dataset / ML
  "ColesterolTotal"       DOUBLE PRECISION NULL, -- mg/dL
  "PresionSistolica"      DOUBLE PRECISION NULL, -- mmHg
  "PresionDiastolica"     DOUBLE PRECISION NULL, -- mmHg
  "Glucosa"               DOUBLE PRECISION NULL, -- mg/dL
  "IMCValor"              DOUBLE PRECISION NULL,

  -- Predicción asociada (1 a 1 opcional)
  "ID_Prediccion"         INT NULL,

  CONSTRAINT "FK_Cita_Patient"
    FOREIGN KEY ("ID_Patient") REFERENCES "Usuario"("ID_Usuario")
      ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT "FK_Cita_Doctor"
    FOREIGN KEY ("ID_Doctor") REFERENCES "Usuario"("ID_Usuario")
      ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT "FK_Cita_RangoColesterol"
    FOREIGN KEY ("ID_RangoColesterol") REFERENCES "RangoColesterol"("ID_RangoColesterol")
      ON UPDATE CASCADE ON DELETE SET NULL,

  CONSTRAINT "FK_Cita_RangoGlucosa"
    FOREIGN KEY ("ID_RangoGlucosa") REFERENCES "RangoGlucosa"("ID_RangoGlucosa")
      ON UPDATE CASCADE ON DELETE SET NULL,

  CONSTRAINT "FK_Cita_Prediccion"
    FOREIGN KEY ("ID_Prediccion") REFERENCES "Prediccion"("ID_Prediccion")
      ON UPDATE CASCADE ON DELETE SET NULL,

  -- Checks de sanidad (no clínicos, solo para evitar basura)
  CONSTRAINT "CK_Cita_Peso" CHECK ("Peso" IS NULL OR ("Peso" >= 20 AND "Peso" <= 400)),
  CONSTRAINT "CK_Cita_Estatura" CHECK ("Estatura" IS NULL OR ("Estatura" >= 50 AND "Estatura" <= 250)),
  CONSTRAINT "CK_Cita_PresionSis" CHECK ("PresionSistolica" IS NULL OR ("PresionSistolica" >= 50 AND "PresionSistolica" <= 300)),
  CONSTRAINT "CK_Cita_PresionDia" CHECK ("PresionDiastolica" IS NULL OR ("PresionDiastolica" >= 30 AND "PresionDiastolica" <= 200)),
  CONSTRAINT "CK_Cita_Colesterol" CHECK ("ColesterolTotal" IS NULL OR ("ColesterolTotal" >= 50 AND "ColesterolTotal" <= 1000)),
  CONSTRAINT "CK_Cita_Glucosa" CHECK ("Glucosa" IS NULL OR ("Glucosa" >= 40 AND "Glucosa" <= 600)),
  CONSTRAINT "CK_Cita_IMC" CHECK ("IMCValor" IS NULL OR ("IMCValor" >= 10 AND "IMCValor" <= 80))
);

-- Índices para consultas comunes (por paciente, doctor, fecha)
CREATE INDEX "IX_Cita_Patient" ON "Cita_Medica" ("ID_Patient");
CREATE INDEX "IX_Cita_Doctor"  ON "Cita_Medica" ("ID_Doctor");
CREATE INDEX "IX_Cita_Fecha"   ON "Cita_Medica" ("Fecha_Cita");

COMMIT;
