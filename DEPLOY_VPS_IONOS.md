# Guía de Despliegue en VPS IONOS con Ubuntu 24.04

Esta guía te ayudará a desplegar la aplicación de Asociación en un servidor VPS de IONOS con Ubuntu 24.04.

## 📋 Requisitos Previos

- VPS de IONOS con Ubuntu 24.04
- Acceso SSH al servidor
- Dominio configurado (opcional, pero recomendado)
- Conocimientos básicos de Linux

## 🔧 Paso 1: Conectar al Servidor

Conéctate a tu servidor VPS usando SSH:

```bash
ssh root@tu_ip_servidor
# o
ssh root@tu_dominio.com
```

## 🔧 Paso 2: Actualizar el Sistema

Actualiza los paquetes del sistema:

```bash
apt update
apt upgrade -y
```

## 🔧 Paso 3: Instalar Dependencias del Sistema

Instala Python, pip y otras dependencias necesarias:

```bash
apt install -y python3 python3-pip python3-venv nginx supervisor git build-essential
```

## 🔧 Paso 4: Crear Usuario para la Aplicación

Crea un usuario dedicado para ejecutar la aplicación (más seguro que usar root):

```bash
adduser --disabled-password --gecos "" asociacion
usermod -aG www-data asociacion
```

## 🔧 Paso 5: Configurar Directorio de la Aplicación

Crea el directorio y configura los permisos:

```bash
mkdir -p /home/asociacion/asociacion_vps
mkdir -p /home/asociacion/asociacion_vps/instance
mkdir -p /var/log/asociacion
chown -R asociacion:www-data /home/asociacion/asociacion_vps
chown -R asociacion:www-data /var/log/asociacion
chmod -R 755 /home/asociacion/asociacion_vps
```

## 🔧 Paso 6: Subir el Código al Servidor

Tienes varias opciones:

### Opción A: Usando Git (si tienes un repositorio privado)

```bash
cd /home/asociacion/asociacion_vps
git clone https://github.com/tu-usuario/tu-repositorio.git .
```

### Opción B: Usando SCP desde tu máquina local

Desde tu máquina local (Windows PowerShell o CMD):

```powershell
# Navega a la carpeta del proyecto
cd C:\Users\jmm87\Trabajos\asociacion_vps

# Sube todos los archivos (excluyendo venv y __pycache__)
scp -r -o StrictHostKeyChecking=no *.py *.txt *.md asociacion@tu_ip_servidor:/home/asociacion/asociacion_vps/
scp -r -o StrictHostKeyChecking=no blueprints templates static asociacion@tu_ip_servidor:/home/asociacion/asociacion_vps/
scp -o StrictHostKeyChecking=no gunicorn_config.py asociacion@tu_ip_servidor:/home/asociacion/asociacion_vps/
```

### Opción C: Usando rsync (más eficiente)

Desde tu máquina local:

```bash
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.db' --exclude '.git' \
  ./ asociacion@tu_ip_servidor:/home/asociacion/asociacion_vps/
```

## 🔧 Paso 7: Crear Entorno Virtual

Crea y activa el entorno virtual de Python:

```bash
cd /home/asociacion/asociacion_vps
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔧 Paso 8: Configurar Variables de Entorno

Crea un archivo `.env` con las variables de entorno:

```bash
cd /home/asociacion/asociacion_vps
nano .env
```

Añade el siguiente contenido (ajusta según tus necesidades):

```bash
SECRET_KEY=genera_una_clave_secreta_muy_segura_aqui
FLASK_ENV=production
PORT=8000
```

**IMPORTANTE**: Genera una clave secreta segura:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado y úsalo como `SECRET_KEY` en el archivo `.env`.

**NOTA**: La aplicación usará SQLite por defecto. La base de datos se creará en `/home/asociacion/asociacion_vps/instance/asociacion.db` automáticamente.

Protege el archivo `.env`:

```bash
chmod 600 .env
chown asociacion:asociacion .env
```

### 🚀 Alternativa: Usar Script de Despliegue

Puedes usar el script de despliegue incluido para automatizar algunos pasos:

```bash
cd /home/asociacion/asociacion_vps
chmod +x scripts/deploy.sh
sudo ./scripts/deploy.sh
```

Este script creará el usuario, directorios, archivo `.env` con clave secreta generada automáticamente, y configurará systemd y nginx básicamente.

## 🔧 Paso 9: Configurar Gunicorn

El archivo `gunicorn_config.py` ya está en el proyecto. Verifica que esté en su lugar:

```bash
ls -la /home/asociacion/asociacion_vps/gunicorn_config.py
```

Si no está, créalo con el contenido del archivo `gunicorn_config.py` del proyecto.

Asegúrate de que los directorios de logs existan:

```bash
mkdir -p /var/log/asociacion
chown -R asociacion:www-data /var/log/asociacion
```

## 🔧 Paso 10: Configurar Systemd

Copia el archivo de servicio systemd:

```bash
cp /home/asociacion/asociacion_vps/systemd/asociacion.service /etc/systemd/system/
```

**IMPORTANTE**: Edita el archivo de servicio para ajustar las rutas y la clave secreta:

```bash
nano /etc/systemd/system/asociacion.service
```

Asegúrate de que:
- Las rutas sean correctas
- La variable `SECRET_KEY` esté configurada (o mejor, lee desde `.env`)

Si prefieres leer desde `.env`, puedes modificar el servicio para usar `EnvironmentFile`:

```ini
[Unit]
Description=Gunicorn instance para servir la aplicación Asociación
After=network.target

[Service]
User=asociacion
Group=www-data
WorkingDirectory=/home/asociacion/asociacion_vps
EnvironmentFile=/home/asociacion/asociacion_vps/.env
Environment="PATH=/home/asociacion/asociacion_vps/venv/bin"
ExecStart=/home/asociacion/asociacion_vps/venv/bin/gunicorn \
          --config /home/asociacion/asociacion_vps/gunicorn_config.py \
          wsgi:app

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Recarga systemd y habilita el servicio:

```bash
systemctl daemon-reload
systemctl enable asociacion.service
systemctl start asociacion.service
```

Verifica el estado:

```bash
systemctl status asociacion.service
```

Si hay errores, revisa los logs:

```bash
journalctl -u asociacion.service -f
```

## 🔧 Paso 11: Configurar Nginx

Copia la configuración de Nginx:

```bash
cp /home/asociacion/asociacion_vps/nginx/asociacion.conf /etc/nginx/sites-available/asociacion
```

Edita el archivo para ajustar el dominio o IP:

```bash
nano /etc/nginx/sites-available/asociacion
```

Cambia `server_name _;` por tu dominio o IP:

```nginx
server_name tu-dominio.com www.tu-dominio.com;
# o si no tienes dominio:
server_name tu_ip_servidor;
```

Habilita el sitio:

```bash
ln -s /etc/nginx/sites-available/asociacion /etc/nginx/sites-enabled/
```

Elimina el sitio por defecto (opcional):

```bash
rm /etc/nginx/sites-enabled/default
```

Verifica la configuración de Nginx:

```bash
nginx -t
```

Si todo está bien, reinicia Nginx:

```bash
systemctl restart nginx
systemctl enable nginx
```

## 🔧 Paso 12: Configurar Firewall

Permite el tráfico HTTP y HTTPS:

```bash
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw enable
```

Verifica el estado:

```bash
ufw status
```

## 🔧 Paso 13: Inicializar la Base de Datos

La aplicación creará automáticamente la base de datos al iniciar. La base de datos SQLite se creará en:

```
/home/asociacion/asociacion_vps/instance/asociacion.db
```

Verifica que se haya creado:

```bash
ls -la /home/asociacion/asociacion_vps/instance/
```

Deberías ver `asociacion.db` después del primer inicio.

**IMPORTANTE**: Asegúrate de que el directorio `instance/` tenga los permisos correctos:

```bash
chown -R asociacion:www-data /home/asociacion/asociacion_vps/instance
chmod -R 755 /home/asociacion/asociacion_vps/instance
```

## 🔧 Paso 14: Verificar que Todo Funciona

1. **Verifica que Gunicorn esté corriendo:**

```bash
systemctl status asociacion.service
curl http://127.0.0.1:8000
```

2. **Verifica que Nginx esté funcionando:**

```bash
systemctl status nginx
curl http://localhost
```

3. **Accede desde tu navegador:**

Abre tu navegador y visita `http://tu_ip_servidor` o `http://tu-dominio.com`

## 🔒 Paso 15: Configurar SSL/HTTPS (Opcional pero Recomendado)

Para habilitar HTTPS, puedes usar Let's Encrypt con Certbot:

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

Sigue las instrucciones en pantalla. Certbot configurará automáticamente Nginx para usar HTTPS.

## 📝 Comandos Útiles para Mantenimiento

### Ver logs de la aplicación:

```bash
# Logs de systemd
journalctl -u asociacion.service -f

# Logs de Gunicorn
tail -f /var/log/asociacion/error.log
tail -f /var/log/asociacion/access.log

# Logs de Nginx
tail -f /var/log/nginx/asociacion_error.log
tail -f /var/log/nginx/asociacion_access.log
```

### Reiniciar la aplicación:

```bash
systemctl restart asociacion.service
```

### Detener la aplicación:

```bash
systemctl stop asociacion.service
```

### Actualizar la aplicación:

```bash
# Detener el servicio
systemctl stop asociacion.service

# Actualizar código (según tu método)
cd /home/asociacion/asociacion_vps
# git pull  # si usas git
# o subir nuevos archivos

# Actualizar dependencias si es necesario
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar el servicio
systemctl start asociacion.service
```

### Hacer backup de la base de datos:

```bash
# Crear directorio de backups
mkdir -p /home/asociacion/backups

# Backup manual
cp /home/asociacion/asociacion_vps/instance/asociacion.db \
   /home/asociacion/backups/asociacion_$(date +%Y%m%d_%H%M%S).db
```

## 🐛 Solución de Problemas

### La aplicación no inicia:

1. Verifica los logs:
```bash
journalctl -u asociacion.service -n 50
```

2. Verifica que el entorno virtual esté activo y las dependencias instaladas:
```bash
cd /home/asociacion/asociacion_vps
source venv/bin/activate
pip list
```

3. Verifica los permisos:
```bash
ls -la /home/asociacion/asociacion_vps
```

### Nginx muestra error 502:

1. Verifica que Gunicorn esté corriendo:
```bash
systemctl status asociacion.service
curl http://127.0.0.1:8000
```

2. Verifica que el puerto 8000 esté correcto en `gunicorn_config.py`

3. Verifica los logs de Nginx:
```bash
tail -f /var/log/nginx/asociacion_error.log
```

### Error de permisos:

Asegúrate de que los permisos sean correctos:

```bash
chown -R asociacion:www-data /home/asociacion/asociacion_vps
chmod -R 755 /home/asociacion/asociacion_vps
chmod 600 /home/asociacion/asociacion_vps/.env
```

## 📧 Credenciales por Defecto

La aplicación crea automáticamente estos usuarios administradores:

- **coco** / admin123
- **lidia** / admin123
- **bego** / admin123
- **david** / admin123
- **jmurillo** / 7GMZ%elA

**⚠️ IMPORTANTE**: Cambia estas contraseñas después del primer inicio de sesión en producción.

## ✅ Checklist Final

- [ ] Sistema actualizado
- [ ] Dependencias instaladas
- [ ] Usuario creado
- [ ] Código subido al servidor
- [ ] Entorno virtual creado y dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Gunicorn configurado y funcionando
- [ ] Systemd service configurado y activo
- [ ] Nginx configurado y funcionando
- [ ] Firewall configurado
- [ ] Base de datos inicializada
- [ ] Aplicación accesible desde el navegador
- [ ] SSL/HTTPS configurado (opcional pero recomendado)
- [ ] Contraseñas por defecto cambiadas

## 🎉 ¡Listo!

Tu aplicación debería estar funcionando en tu VPS de IONOS. Si encuentras algún problema, revisa la sección de solución de problemas o los logs del sistema.

