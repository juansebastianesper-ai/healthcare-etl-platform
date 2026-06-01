# Healthcare ETL Platform

Plataforma Inteligente de Analítica Clínica - ETL + Machine Learning para datos clínicos.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Bootstrap 5 + Chart.js)         │
├─────────────────────────────────────────────────────────────┤
│                    Django REST Framework                     │
├───────────┬──────────┬──────────┬───────────┬───────────────┤
│   Auth    │   ETL    │Analytics │    ML     │   Reports     │
│   JWT     │  Engine  │   KPIs   │RandomForest│ PDF/Excel/CSV │
├───────────┴──────────┴──────────┴───────────┴───────────────┤
│                    PostgreSQL (Neon)                         │
└─────────────────────────────────────────────────────────────┘
```

## Tecnologías

- **Backend:** Python 3.12, Django 5.1, DRF, Pandas, NumPy, Scikit-Learn
- **Frontend:** HTML5, Bootstrap 5, JavaScript, Chart.js
- **Base de Datos:** PostgreSQL (Neon)
- **Autenticación:** JWT (djangorestframework-simplejwt)
- **Documentación API:** Swagger/OpenAPI (drf-yasg)

## Estructura del Proyecto

```
healthcare-etl-platform/
├── backend/
│   ├── config/           # Configuración Django
│   ├── authentication/   # Autenticación JWT y Roles
│   ├── etl/              # Motor ETL (Extract, Transform, Load)
│   ├── analytics/        # KPIs, Estadísticas, Segmentación
│   ├── ml/               # Machine Learning (Random Forest)
│   ├── dashboard/        # Dashboard API
│   ├── reports/          # Reportes PDF/Excel/CSV
│   ├── core/             # Base, Excepciones, Logging
│   ├── templates/        # Templates HTML
│   └── static/           # Archivos estáticos (CSS, JS)
├── datasets/             # Datasets de ejemplo
├── docs/                 # Documentación
├── docker-compose.yml    # Orquestación Docker
├── Dockerfile            # Imagen Docker
└── deploy.sh             # Script de despliegue
```

## Instalación Rápida

### Con Docker (Recomendado)

```bash
git clone <repo-url>
cd healthcare-etl-platform
cp .env.example .env
docker-compose up -d
```

Acceder a:
- Plataforma: http://localhost:8000
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/swagger/

### Instalación Local

```bash
pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

### Credenciales por Defecto

- **Usuario:** admin
- **Contraseña:** admin123

## API Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Iniciar sesión |
| POST | `/api/auth/register/` | Registrar usuario |
| POST | `/api/auth/refresh/` | Refrescar token |
| GET | `/api/auth/profile/` | Perfil del usuario |
| GET | `/api/auth/users/` | Listar usuarios |

### ETL
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/etl/pacientes/` | Listar pacientes |
| GET | `/api/etl/pacientes/{id}/` | Detalle paciente |
| GET | `/api/etl/pacientes/criticos/` | Pacientes críticos |
| POST | `/api/etl/runs/upload/` | Ejecutar ETL |
| GET | `/api/etl/runs/history/` | Historial ETL |

### Analytics
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/analytics/kpis/` | KPIs del sistema |
| GET | `/api/analytics/estadisticas/` | Estadísticas descriptivas |
| GET | `/api/analytics/segmentacion/{criterio}/` | Segmentación |

### Machine Learning
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/ml/models/train/` | Entrenar modelo |
| GET | `/api/ml/models/active/` | Modelo activo |
| POST | `/api/ml/predictions/predict/` | Predecir riesgo |

### Dashboard
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/dashboard/` | Datos del dashboard |

### Reportes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/reports/pdf/{tipo}/` | Reporte PDF |
| GET | `/api/reports/csv/{tipo}/` | Exportar CSV |
| GET | `/api/reports/excel/{tipo}/` | Exportar Excel |

## Roles de Usuario

- **Administrador:** Acceso completo al sistema
- **Médico:** Visualización de datos y predicciones
- **Analista:** Gestión de datos y ejecución ETL

## Licencia

MIT License
