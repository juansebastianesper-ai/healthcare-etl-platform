#!/bin/bash
# ==========================================
# Healthcare ETL Platform - Script de Despliegue
# ==========================================

set -e

echo "=========================================="
echo "Healthcare ETL Platform - Deploy Script"
echo "=========================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verificar prerequisitos
check_prerequisites() {
    log_info "Verificando prerequisitos..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 no está instalado"
        exit 1
    fi

    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 no está instalado"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        log_warn "Docker no está instalado. Se usará instalación local."
        USE_DOCKER=false
    else
        USE_DOCKER=true
    fi

    log_info "Prerequisitos OK"
}

# Setup con Docker
setup_docker() {
    log_info "Iniciando despliegue con Docker..."

    if [ ! -f .env ]; then
        cp .env.example .env
        log_warn "Archivo .env creado desde .env.example. Revise la configuración."
    fi

    docker-compose build
    docker-compose up -d

    log_info "Ejecutando migraciones..."
    docker-compose exec backend python manage.py migrate

    log_info "Creando superusuario por defecto..."
    docker-compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@healthcare.com', 'admin123')
    print('Superusuario creado: admin / admin123')
else:
    print('Superusuario ya existe')
"

    log_info "Despliegue completado!"
    echo ""
    echo "=========================================="
    echo "  Acceso a la plataforma:"
    echo "  Frontend: http://localhost:8000"
    echo "  Admin:    http://localhost:8000/admin/"
    echo "  API Docs: http://localhost:8000/swagger/"
    echo "=========================================="
}

# Setup local
setup_local() {
    log_info "Iniciando despliegue local..."

    if [ ! -d "venv" ]; then
        log_info "Creando entorno virtual..."
        python3 -m venv venv
    fi

    source venv/bin/activate

    log_info "Instalando dependencias..."
    pip install --upgrade pip
    pip install -r backend/requirements.txt

    log_info "Ejecutando migraciones..."
    cd backend
    python manage.py migrate

    log_info "Creando superusuario por defecto..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@healthcare.com', 'admin123')
    print('Superusuario creado: admin / admin123')
else:
    print('Superusuario ya existe')
"

    log_info "Recolectando archivos estáticos..."
    python manage.py collectstatic --noinput

    log_info "Iniciando servidor de desarrollo..."
    echo ""
    echo "=========================================="
    echo "  Plataforma iniciada en:"
    echo "  http://localhost:8000"
    echo "  Admin: http://localhost:8000/admin/"
    echo "=========================================="
    echo ""
    python manage.py runserver 0.0.0.0:8000
}

# Main
main() {
    check_prerequisites

    if [ "$1" == "docker" ] || [ "$USE_DOCKER" == true ]; then
        setup_docker
    else
        setup_local
    fi
}

main "$@"
