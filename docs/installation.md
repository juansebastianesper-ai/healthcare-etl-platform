# Manual de Instalación

## Requisitos del Sistema

- Python 3.12+
- PostgreSQL 16+ (o cuenta Neon)
- Node.js (opcional, para desarrollo frontend)
- Docker y Docker Compose (opcional, para despliegue containerizado)

## Instalación con Docker (Recomendado)

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd healthcare-etl-platform
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con configuración deseada
```

### 3. Iniciar contenedores
```bash
docker-compose up -d
```

### 4. Verificar instalación
```bash
# Ver logs
docker-compose logs -f backend

# Revisar estado
docker-compose ps
```

### 5. Acceder a la plataforma
- Frontend: http://localhost:8000
- Admin Django: http://localhost:8000/admin/
- API Swagger: http://localhost:8000/swagger/
- API Redoc: http://localhost:8000/redoc/

## Instalación Local (Sin Docker)

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd healthcare-etl-platform
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4. Configurar base de datos PostgreSQL

#### Opción A: PostgreSQL Local
```bash
# Crear base de datos
createdb healthcare_etl

# Editar backend/config/settings.py con credenciales locales
```

#### Opción B: Neon (Cloud)
```bash
# Obtener connection string de Neon Dashboard
# Configurar en .env:
DB_HOST=ep-XXXX.us-east-2.aws.neon.tech
DB_NAME=healthcare_etl
DB_USER=your_user
DB_PASSWORD=your_password
DB_PORT=5432
```

### 5. Ejecutar migraciones
```bash
cd backend
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
# Usuario: admin
# Email: admin@healthcare.com
# Contraseña: admin123
```

### 7. Recolectar archivos estáticos
```bash
python manage.py collectstatic --noinput
```

### 8. Iniciar servidor
```bash
python manage.py runserver 0.0.0.0:8000
```

### 9. Poblar datos de ejemplo (opcional)
```bash
python manage.py shell -c "
import pandas as pd
from etl.engine import ETLEngine

engine = ETLEngine()
df = pd.read_csv('../datasets/sample_clinical_data.csv')
engine.run_from_content(df, 'sample_data.csv', 'Demo')
print('Datos de ejemplo cargados!')
"
```

## Configuración de Neon (Base de Datos Cloud)

1. Crear cuenta en [neon.tech](https://neon.tech)
2. Crear proyecto y obtener connection string
3. Configurar en `.env`:
```env
DB_HOST=your-project.us-east-2.aws.neon.tech
DB_NAME=healthcare_etl
DB_USER=your_user
DB_PASSWORD=your_password
DB_PORT=5432
```

## Configuración de JWT

Configurar en `.env`:
```env
JWT_ACCESS_HOURS=1      # Tiempo de vida del token de acceso
JWT_REFRESH_DAYS=7      # Tiempo de vida del refresh token
```

## Solución de Problemas

### Error de conexión a base de datos
```bash
# Verificar que PostgreSQL esté corriendo
# Linux/Mac:
sudo systemctl status postgresql

# Windows:
net start postgresql-16

# Verificar credenciales en .env
```

### Error de migraciones
```bash
python manage.py migrate --run-syncdb
```

### Error de dependencias
```bash
pip install --upgrade -r backend/requirements.txt
```
