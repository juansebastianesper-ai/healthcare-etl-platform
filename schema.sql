-- ============================================================
-- SCRIPT SQL COMPLETO - Healthcare ETL Platform
-- Generado a partir de migraciones Django
-- Compatible con PostgreSQL y SQLite
-- ============================================================

-- ============================================================
-- 1. TABLA: auth_user (heredada de Django)
-- ============================================================
-- (Tabla estándar de Django, no incluida en migraciones del proyecto)

-- ============================================================
-- 2. TABLA: authentication_user
-- ============================================================
CREATE TABLE IF NOT EXISTS authentication_user (
    id              BIGSERIAL PRIMARY KEY,
    password        VARCHAR(128) NOT NULL,
    last_login      TIMESTAMP NULL,
    is_superuser    BOOLEAN NOT NULL DEFAULT FALSE,
    username        VARCHAR(150) NOT NULL UNIQUE,
    first_name      VARCHAR(150) NOT NULL DEFAULT '',
    last_name       VARCHAR(150) NOT NULL DEFAULT '',
    email           VARCHAR(254) NOT NULL DEFAULT '',
    is_staff        BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined     TIMESTAMP NOT NULL DEFAULT NOW(),
    role            VARCHAR(10) NOT NULL DEFAULT 'ANALISTA'
                    CHECK (role IN ('ADMIN', 'MEDICO', 'ANALISTA')),
    telefono        VARCHAR(15) NULL
);

-- ============================================================
-- 3. TABLA: etl_patient
-- ============================================================
CREATE TABLE IF NOT EXISTS etl_patient (
    id                      BIGSERIAL PRIMARY KEY,
    nombre                  VARCHAR(200) NOT NULL,
    edad                    INTEGER NOT NULL CHECK (edad >= 0 AND edad <= 120),
    sexo                    VARCHAR(1) NOT NULL CHECK (sexo IN ('M', 'F', 'O')),
    peso                    DOUBLE PRECISION NOT NULL CHECK (peso >= 0.1 AND peso <= 500),
    altura                  DOUBLE PRECISION NOT NULL CHECK (altura >= 0.3 AND altura <= 2.5),
    imc                     DOUBLE PRECISION NULL,
    imc_clasificacion       VARCHAR(20) NULL
                            CHECK (imc_clasificacion IN (
                                'BAJO_PESO', 'NORMAL', 'SOBREPESO',
                                'OBESIDAD_I', 'OBESIDAD_II', 'OBESIDAD_III'
                            )),
    presion_sistolica       INTEGER NOT NULL CHECK (presion_sistolica >= 30 AND presion_sistolica <= 300),
    presion_diastolica      INTEGER NOT NULL CHECK (presion_diastolica >= 20 AND presion_diastolica <= 200),
    glucosa                 DOUBLE PRECISION NOT NULL CHECK (glucosa >= 0 AND glucosa <= 1000),
    colesterol              DOUBLE PRECISION NOT NULL CHECK (colesterol >= 0 AND colesterol <= 800),
    frecuencia_cardiaca     INTEGER NOT NULL CHECK (frecuencia_cardiaca >= 20 AND frecuencia_cardiaca <= 300),
    saturacion_oxigeno      DOUBLE PRECISION NOT NULL CHECK (saturacion_oxigeno >= 0 AND saturacion_oxigeno <= 100),
    fumador                 BOOLEAN NOT NULL DEFAULT FALSE,
    diagnostico             TEXT NULL,
    riesgo                  VARCHAR(10) NULL
                            CHECK (riesgo IN ('BAJO', 'MEDIO', 'ALTO', 'CRITICO')),
    fecha_registro          TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at              TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_patient_riesgo ON etl_patient (riesgo);
CREATE INDEX IF NOT EXISTS idx_patient_edad ON etl_patient (edad);
CREATE INDEX IF NOT EXISTS idx_patient_sexo ON etl_patient (sexo);
CREATE INDEX IF NOT EXISTS idx_patient_imc ON etl_patient (imc);

-- ============================================================
-- 4. TABLA: etl_etlsource
-- ============================================================
CREATE TABLE IF NOT EXISTS etl_etlsource (
    id              BIGSERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    descripcion     TEXT NULL,
    tipo_archivo    VARCHAR(10) NOT NULL,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 5. TABLA: etl_etlrun
-- ============================================================
CREATE TABLE IF NOT EXISTS etl_etlrun (
    id                      BIGSERIAL PRIMARY KEY,
    archivo                 VARCHAR(500) NOT NULL,
    fuente_id               BIGINT NULL REFERENCES etl_etlsource(id)
                            ON DELETE SET NULL,
    registros_procesados    INTEGER NOT NULL DEFAULT 0,
    registros_limpios       INTEGER NOT NULL DEFAULT 0,
    registros_errores       INTEGER NOT NULL DEFAULT 0,
    estado                  VARCHAR(15) NOT NULL DEFAULT 'PENDIENTE'
                            CHECK (estado IN ('PENDIENTE', 'PROCESANDO', 'COMPLETADO', 'ERROR')),
    fecha_inicio            TIMESTAMP NULL,
    fecha_fin               TIMESTAMP NULL,
    log_detalle             TEXT NULL,
    usuario_id              BIGINT NULL REFERENCES authentication_user(id)
                            ON DELETE SET NULL,
    created_at              TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 6. TABLA: ml_mlmodel
-- ============================================================
CREATE TABLE IF NOT EXISTS ml_mlmodel (
    id                  BIGSERIAL PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL DEFAULT 'Random Forest Classifier',
    version             VARCHAR(20) NOT NULL,
    accuracy            DOUBLE PRECISION NULL CHECK (accuracy >= 0 AND accuracy <= 1),
    precision           DOUBLE PRECISION NULL CHECK (precision >= 0 AND precision <= 1),
    recall              DOUBLE PRECISION NULL CHECK (recall >= 0 AND recall <= 1),
    f1_score            DOUBLE PRECISION NULL CHECK (f1_score >= 0 AND f1_score <= 1),
    matriz_confusion    JSONB NULL,
    parametros          JSONB NULL,
    entrenado_en        TIMESTAMP NOT NULL DEFAULT NOW(),
    activo              BOOLEAN NOT NULL DEFAULT FALSE,
    ruta_archivo        VARCHAR(500) NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 7. TABLA: ml_prediction
-- ============================================================
CREATE TABLE IF NOT EXISTS ml_prediction (
    id                  BIGSERIAL PRIMARY KEY,
    paciente_id         BIGINT NULL REFERENCES etl_patient(id)
                        ON DELETE CASCADE,
    modelo_id           BIGINT NULL REFERENCES ml_mlmodel(id)
                        ON DELETE SET NULL,
    prediccion          VARCHAR(10) NOT NULL,
    probabilidad        DOUBLE PRECISION NOT NULL,
    features            JSONB NOT NULL,
    fecha_prediccion    TIMESTAMP NOT NULL DEFAULT NOW(),
    usuario_id          BIGINT NULL REFERENCES authentication_user(id)
                        ON DELETE SET NULL
);

-- ============================================================
-- 8. TABLA: django migrations (control de Django)
-- ============================================================
CREATE TABLE IF NOT EXISTS django_migrations (
    id      BIGSERIAL PRIMARY KEY,
    app     VARCHAR(255) NOT NULL,
    name    VARCHAR(255) NOT NULL,
    applied TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================
-- DATOS INICIALES: Usuarios por defecto
-- ============================================================
-- NOTA: Estos usuarios se crean via management command seed_users
-- pero se incluye el SQL por referencia.

-- Admin: admin / admin123 (Rol: ADMIN)
-- Medico: medico / medico123 (Rol: MEDICO)
-- Analista: analista / analista123 (Rol: ANALISTA)

-- ============================================================
-- SECUENCIAS (PostgreSQL) - Reset de IDs
-- ============================================================
-- ALTER SEQUENCE etl_patient_id_seq RESTART WITH 1;
-- ALTER SEQUENCE etl_etlrun_id_seq RESTART WITH 1;
-- ALTER SEQUENCE etl_etlsource_id_seq RESTART WITH 1;
-- ALTER SEQUENCE ml_prediction_id_seq RESTART WITH 1;
