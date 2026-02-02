#!/bin/bash
# Script de despliegue para VPS IONOS
# Este script ayuda a automatizar algunos pasos del despliegue

set -e

echo "=========================================="
echo "Script de Despliegue - Asociación VPS"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    print_error "Por favor, ejecuta este script como root o con sudo"
    exit 1
fi

# Verificar que el usuario asociacion existe
if ! id "asociacion" &>/dev/null; then
    print_info "Creando usuario asociacion..."
    adduser --disabled-password --gecos "" asociacion
    usermod -aG www-data asociacion
else
    print_info "Usuario asociacion ya existe"
fi

# Crear directorios necesarios
print_info "Creando directorios..."
mkdir -p /home/asociacion/asociacion_vps/instance
mkdir -p /var/log/asociacion
chown -R asociacion:www-data /home/asociacion/asociacion_vps
chown -R asociacion:www-data /var/log/asociacion
chmod -R 755 /home/asociacion/asociacion_vps

# Verificar si existe el archivo .env
if [ ! -f "/home/asociacion/asociacion_vps/.env" ]; then
    print_warning "Archivo .env no encontrado. Creando uno de ejemplo..."
    cat > /home/asociacion/asociacion_vps/.env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=production
PORT=8000
EOF
    chmod 600 /home/asociacion/asociacion_vps/.env
    chown asociacion:asociacion /home/asociacion/asociacion_vps/.env
    print_info "Archivo .env creado. Por favor, revísalo y ajusta si es necesario."
else
    print_info "Archivo .env ya existe"
fi

# Configurar systemd service
print_info "Configurando servicio systemd..."
if [ -f "/home/asociacion/asociacion_vps/systemd/asociacion.service" ]; then
    cp /home/asociacion/asociacion_vps/systemd/asociacion.service /etc/systemd/system/
    systemctl daemon-reload
    print_info "Servicio systemd configurado"
else
    print_warning "Archivo systemd/asociacion.service no encontrado. Configúralo manualmente."
fi

# Configurar Nginx
print_info "Configurando Nginx..."
if [ -f "/home/asociacion/asociacion_vps/nginx/asociacion.conf" ]; then
    cp /home/asociacion/asociacion_vps/nginx/asociacion.conf /etc/nginx/sites-available/asociacion
    
    # Preguntar por el dominio
    read -p "¿Cuál es tu dominio o IP del servidor? (presiona Enter para usar IP por defecto): " DOMAIN
    if [ -z "$DOMAIN" ]; then
        DOMAIN="_"
    fi
    
    # Reemplazar server_name en la configuración
    sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/sites-available/asociacion
    
    if [ -f "/etc/nginx/sites-enabled/default" ]; then
        rm /etc/nginx/sites-enabled/default
    fi
    
    if [ ! -L "/etc/nginx/sites-enabled/asociacion" ]; then
        ln -s /etc/nginx/sites-available/asociacion /etc/nginx/sites-enabled/
    fi
    
    # Verificar configuración de Nginx
    if nginx -t; then
        print_info "Configuración de Nginx válida"
    else
        print_error "Error en la configuración de Nginx. Revisa /etc/nginx/sites-available/asociacion"
        exit 1
    fi
else
    print_warning "Archivo nginx/asociacion.conf no encontrado. Configura Nginx manualmente."
fi

# Configurar firewall
print_info "Configurando firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
    ufw --force enable
    print_info "Firewall configurado"
else
    print_warning "UFW no está instalado. Configura el firewall manualmente."
fi

echo ""
print_info "=========================================="
print_info "Configuración básica completada"
print_info "=========================================="
echo ""
print_warning "PASOS MANUALES RESTANTES:"
echo ""
echo "1. Asegúrate de que el código esté en /home/asociacion/asociacion_vps"
echo "2. Crea el entorno virtual:"
echo "   cd /home/asociacion/asociacion_vps"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Revisa y ajusta el archivo .env si es necesario"
echo ""
echo "4. Inicia el servicio:"
echo "   systemctl enable asociacion.service"
echo "   systemctl start asociacion.service"
echo ""
echo "5. Reinicia Nginx:"
echo "   systemctl restart nginx"
echo ""
echo "6. Verifica el estado:"
echo "   systemctl status asociacion.service"
echo "   curl http://localhost"
echo ""




