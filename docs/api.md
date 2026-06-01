# Documentación de la API REST

## Autenticación

Todas las solicitudes a la API requieren autenticación JWT (excepto `/api/auth/login/`, `/api/auth/register/`, `/api/auth/refresh/`).

### Obtener Token
```
POST /api/auth/login/

Body:
{
    "username": "admin",
    "password": "admin123"
}

Response 200:
{
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@healthcare.com",
        "role": "ADMIN",
        ...
    },
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Uso del Token
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Refrescar Token
```
POST /api/auth/refresh/

Body:
{
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

## Endpoints

### Pacientes

#### Listar Pacientes
```
GET /api/etl/pacientes/
Authorization: Bearer <token>

Query Params:
  - page: número de página (default: 1)
  - search: búsqueda por nombre
  - riesgo: BAJO | MEDIO | ALTO | CRITICO
  - sexo: M | F
  - ordering: -edad | edad | -imc | imc
```

#### Detalle de Paciente
```
GET /api/etl/pacientes/{id}/
```

#### Pacientes Críticos
```
GET /api/etl/pacientes/criticos/
```

### ETL

#### Ejecutar ETL (Subir Archivo)
```
POST /api/etl/runs/upload/
Content-Type: multipart/form-data

Body:
  - archivo: (CSV or Excel file)
  - fuente: "Nombre de la fuente"
```

#### Historial ETL
```
GET /api/etl/runs/history/
```

#### Log de Ejecución
```
GET /api/etl/runs/{id}/log/
```

### Analytics

#### KPIs
```
GET /api/analytics/kpis/

Response:
{
    "total_pacientes": 150,
    "pacientes_criticos": 5,
    "hipertensos": 35,
    "diabeticos": 28,
    "fumadores": 42,
    "riesgo_promedio": 2.3,
    "distribucion_riesgo": {
        "BAJO": 50, "MEDIO": 40, "ALTO": 35, "CRITICO": 5
    },
    "distribucion_sexo": {"M": 80, "F": 70},
    ...
}
```

#### Estadísticas Descriptivas
```
GET /api/analytics/estadisticas/
GET /api/analytics/estadisticas/?campo=edad
```

#### Segmentación
```
GET /api/analytics/segmentacion/{criterio}/
  criterio: edad | sexo | riesgo | imc | diagnostico
```

### Machine Learning

#### Obtener Modelo Activo
```
GET /api/ml/models/active/
```

#### Entrenar Modelo
```
POST /api/ml/models/train/
```

#### Predecir Riesgo
```
POST /api/ml/predictions/predict/

Body:
{
    "edad": 45,
    "imc": 28.5,
    "glucosa": 180,
    "colesterol": 250,
    "presion_sistolica": 160,
    "frecuencia_cardiaca": 80,
    "fumador": true
}

Response:
{
    "prediccion": "ALTO",
    "probabilidad": 0.85,
    "probabilidades": {
        "BAJO": 0.05,
        "MEDIO": 0.10,
        "ALTO": 0.85,
        "CRITICO": 0.00
    }
}
```

### Dashboard

#### Obtener Datos del Dashboard
```
GET /api/dashboard/
```

### Reportes

#### Reporte PDF
```
GET /api/reports/pdf/{tipo}/
  tipo: general | pacientes | etl | ml
```

#### Exportar CSV
```
GET /api/reports/csv/{tipo}/
  tipo: pacientes | predicciones
```

#### Exportar Excel
```
GET /api/reports/excel/{tipo}/
  tipo: pacientes | etl
```

## Diagrama de Estados - ETL

```
PENDIENTE ──► PROCESANDO ──► COMPLETADO
                  │
                  ▼
               ERROR
```

## Códigos de Error

| Código | HTTP Status | Descripción |
|--------|-------------|-------------|
| `invalid_credentials` | 401 | Credenciales inválidas |
| `etl_error` | 400 | Error en proceso ETL |
| `model_not_trained` | 400 | Modelo no entrenado |
| `insufficient_data` | 400 | Datos insuficientes para ML |
| `report_error` | 400 | Error generando reporte |
| `unexpected_error` | 500 | Error interno del servidor |

## Throttling

- **Anónimo:** 100 requests/día
- **Autenticado:** 1000 requests/día
