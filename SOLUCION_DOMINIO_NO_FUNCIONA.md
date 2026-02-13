# 🔧 Solución: La aplicación funciona con IP pero no con el dominio

Si la aplicación funciona con la IP (`http://94.143.140.75`) pero no con el dominio (`http://avmontealto.es`), el problema está en la configuración de Nginx.

## 🔍 Diagnóstico Rápido

Ejecuta estos comandos en el servidor:

```bash
# 1. Verificar que el archivo de configuración existe y está enlazado
ls -la /etc/nginx/sites-available/asociacion
ls -la /etc/nginx/sites-enabled/asociacion

# 2. Ver el contenido del archivo de configuración
cat /etc/nginx/sites-available/asociacion

# 3. Verificar qué tiene configurado en server_name
grep server_name /etc/nginx/sites-available/asociacion
```

## ✅ Solución Paso a Paso

### Paso 1: Verificar y editar la configuración de Nginx

```bash
# Editar el archivo de configuración
sudo nano /etc/nginx/sites-available/asociacion
```

**Asegúrate de que la línea `server_name` tenga tu dominio:**

```nginx
server_name avmontealto.es www.avmontealto.es;
```

**NO debe tener:**
- `server_name _;`
- `server_name 94.143.140.75;`
- Solo la IP

### Paso 2: Verificar que el archivo está enlazado correctamente

```bash
# Verificar que existe el enlace simbólico
ls -la /etc/nginx/sites-enabled/ | grep asociacion

# Si NO existe, créalo:
sudo ln -s /etc/nginx/sites-available/asociacion /etc/nginx/sites-enabled/

# Si existe el sitio por defecto, elimínalo (opcional pero recomendado):
sudo rm /etc/nginx/sites-enabled/default
```

### Paso 3: Verificar que la configuración es válida

```bash
sudo nginx -t
```

**Debe mostrar:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Paso 4: Recargar Nginx

```bash
sudo systemctl reload nginx
# o
sudo systemctl restart nginx
```

### Paso 5: Verificar que funciona

```bash
# Probar con el dominio desde el servidor
curl -H "Host: avmontealto.es" http://localhost

# Debe mostrar HTML de la aplicación
```

## 🔍 Verificación Completa

Ejecuta este script completo:

```bash
#!/bin/bash
echo "=== Verificación de Configuración Nginx ==="
echo ""

echo "1. Archivo de configuración existe:"
ls -la /etc/nginx/sites-available/asociacion && echo "✅" || echo "❌ NO EXISTE"
echo ""

echo "2. Enlace simbólico existe:"
ls -la /etc/nginx/sites-enabled/asociacion && echo "✅" || echo "❌ NO EXISTE - Ejecuta: sudo ln -s /etc/nginx/sites-available/asociacion /etc/nginx/sites-enabled/"
echo ""

echo "3. Configuración server_name:"
grep server_name /etc/nginx/sites-available/asociacion
echo ""

echo "4. Configuración válida:"
sudo nginx -t
echo ""

echo "5. Estado de Nginx:"
systemctl status nginx --no-pager | head -3
echo ""
```

## 🐛 Problemas Comunes y Soluciones

### Problema 1: El archivo no está enlazado en sites-enabled

**Síntoma:** La configuración existe pero Nginx no la usa

**Solución:**
```bash
sudo ln -s /etc/nginx/sites-available/asociacion /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Problema 2: server_name tiene la IP en lugar del dominio

**Síntoma:** `server_name 94.143.140.75;` en lugar de `server_name avmontealto.es;`

**Solución:**
```bash
sudo nano /etc/nginx/sites-available/asociacion
# Cambiar a: server_name avmontealto.es www.avmontealto.es;
sudo nginx -t
sudo systemctl reload nginx
```

### Problema 3: Hay múltiples configuraciones conflictivas

**Síntoma:** Varios archivos en sites-enabled

**Solución:**
```bash
# Ver qué archivos están activos
ls -la /etc/nginx/sites-enabled/

# Si hay default u otros, elimínalos o desactívalos
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### Problema 4: El sitio por defecto tiene prioridad

**Síntoma:** El sitio por defecto de Nginx está interceptando las peticiones

**Solución:**
```bash
# Eliminar o desactivar el sitio por defecto
sudo rm /etc/nginx/sites-enabled/default

# O renombrarlo
sudo mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.disabled

sudo nginx -t
sudo systemctl reload nginx
```

## 📝 Configuración Correcta Completa

El archivo `/etc/nginx/sites-available/asociacion` debe verse así:

```nginx
server {
    listen 80;
    server_name avmontealto.es www.avmontealto.es;
    
    client_max_body_size 10M;
    
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    access_log /var/log/nginx/asociacion_access.log;
    error_log /var/log/nginx/asociacion_error.log;
    
    location /static {
        alias /home/asociacion/asociacion_vps/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(db|sqlite|sqlite3|env|pyc|py)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

## ✅ Verificación Final

Después de aplicar los cambios:

1. **Verifica la configuración:**
   ```bash
   sudo nginx -t
   ```

2. **Recarga Nginx:**
   ```bash
   sudo systemctl reload nginx
   ```

3. **Prueba desde el navegador:**
   - Abre: `http://avmontealto.es`
   - Debe cargar la aplicación

4. **Si aún no funciona, revisa los logs:**
   ```bash
   sudo tail -f /var/log/nginx/asociacion_error.log
   ```

## 🔍 Debug Avanzado

Si después de todo esto aún no funciona:

```bash
# Ver todas las configuraciones activas
sudo nginx -T | grep -A 20 "server_name"

# Ver qué configuración está usando Nginx para el dominio
curl -v http://avmontealto.es 2>&1 | grep -i "server\|host"

# Ver logs en tiempo real
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/asociacion_error.log
```






