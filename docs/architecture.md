# Arquitectura del Sistema

## Visión General

Healthcare ETL Platform sigue una arquitectura de microservicios monolíticos con separación clara de responsabilidades mediante apps de Django.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cliente Web                             │
│                  HTML5 + Bootstrap 5 + Chart.js                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/JSON + JWT
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx / Gunicorn (Proxy)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django REST Framework                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Auth App   │ │ ETL App  │ │Analytics │ │    ML App        │  │
│  │ JWT + Roles│ │Extract-  │ │App       │ │ Random Forest    │  │
│  │            │ │Transform │ │KPIs+Stats│ │ Predict + Train  │  │
│  └────────────┘ │-Load     │ └──────────┘ └──────────────────┘  │
│                 └──────────┘ ┌──────────┐ ┌──────────────────┐  │
│                              │Dashboard │ │   Reports App    │  │
│                              │App       │ │PDF/Excel/CSV     │  │
│                              └──────────┘ └──────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Core App                               │   │
│  │        Exceptions · Logging · Middleware · Utils          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL (Neon)                            │
│  Tables: User, Patient, ETLRun, ETLSource, MLModel, Prediction  │
└─────────────────────────────────────────────────────────────────┘
```

## Principios de Diseño

### Clean Architecture
- Separación en capas: API → Service → Repository
- Inversión de dependencias
- Modelos de dominio independientes

### SOLID
- **S:** Cada app tiene una responsabilidad única
- **O:** Abierto a extensión, cerrado a modificación
- **L:** Sustitución de servicios
- **I:** Interfaces específicas por funcionalidad
- **D:** Dependency injection via services

### Repository Pattern
- Servicios encapsulan lógica de negocio
- Vistas solo manejan HTTP (request/response)
- Modelos son representación de datos

## Flujo de Datos

### ETL Pipeline
```
Extract ──► Transform ──► Load ──► Analytics ──► ML
  │              │             │          │           │
  ▼              ▼             ▼          ▼           ▼
 CSV/Excel   Clean Data   PostgreSQL    KPIs      Predictions
```

### Autenticación
```
Client ──► POST /auth/login ──► Validate ──► JWT Token
  │                                                    │
  └─────────── Bearer Token ─────► API Views ──────────┘
                                        │
                                   Permission
                                   Check (Role)
```

## Seguridad

- JWT con refresh tokens
- Roles (Admin, Médico, Analista)
- Throttling por usuario/anónimo
- CORS configurado
- Variables de entorno para secretos
- Logging de todas las operaciones críticas

## Base de Datos - ERD

```
┌─────────────────┐       ┌──────────────────┐
│      User       │       │     Patient      │
├─────────────────┤       ├──────────────────┤
│ id (PK)         │       │ id (PK)          │
│ username        │       │ nombre           │
│ email           │       │ edad             │
│ password        │       │ sexo             │
│ role            │       │ peso             │
│ is_active       │       │ altura           │
└─────────────────┘       │ imc              │
        │                 │ riesgo           │
        │                 │ glucosa          │
        │                 │ colesterol       │
        ▼                 │ fumador          │
┌─────────────────┐       │ fecha_registro   │
│    ETLRun       │       └──────────────────┘
├─────────────────┤                │
│ id (PK)         │                │
│ archivo         │                ▼
│ usuario (FK)    │       ┌──────────────────┐
│ estado          │       │   Prediction     │
│ fecha_inicio    │       ├──────────────────┤
│ fecha_fin       │       │ id (PK)          │
│ registros_*     │       │ paciente (FK)    │
│ fuente (FK)     │       │ modelo (FK)      │
└─────────────────┘       │ prediccion       │
                          │ probabilidad     │
┌─────────────────┐       │ fecha_prediccion │
│   MLModel       │       └──────────────────┘
├─────────────────┤
│ id (PK)         │
│ version         │
│ accuracy        │
│ precision       │
│ recall          │
│ f1_score        │
│ activo          │
│ ruta_archivo    │
└─────────────────┘
```
