# ✅ Guía de Verificación Completa del Despliegue

Esta guía te ayudará a verificar que todo está correctamente configurado para que tu aplicación funcione con el dominio.

## 🌐 Paso 1: Verificar que el DNS apunta correctamente

### Desde tu máquina local (Windows):

```powershell
# Verificar que el dominio resuelve a la IP correcta
nslookup avmontealto.es

# O usando ping
ping avmontealto.es
```

**Resultado esperado:**
- Debe mostrar la IP: `94.143.140.75`
- Si muestra otra IP o no resuelve, el DNS aún no se ha propagado

### Desde el servidor:

```bash
# Verificar desde el servidor
nslookup avmontealto.es
# o
host avmontealto.es
```

**Resultado esperado:**
- Debe mostrar: `94.143.140.75`

### Herramientas online (alternativa):

- https://www.whatsmydns.net/#A/avmontealto.es
- https://dnschecker.org/#A/avmontealto.es

Busca `avmontealto.es` y verifica que en la mayoría de servidores DNS muestre `94.143.140.75`.

## 🔧 Paso 2: Verificar que Nginx está corriendo

```bash
# Verificar estado de Nginx
sudo systemctl status nginx

# Debe mostrar: active (running)
```

Si no está corriendo:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 🔧 Paso 3: Verificar que la aplicación está corriendo

```bash
# Verificar estado del servicio
sudo systemctl status asociacion.service

# Debe mostrar: active (running)
```

Si no está corriendo:
```bash
sudo systemctl start asociacion.service
sudo systemctl enable asociacion.service
```

## 🔧 Paso 4: Verificar configuración de Nginx

### Verificar que el archivo de configuración existe:

```bash
ls -la /etc/nginx/sites-available/asociacion
ls -la /etc/nginx/sites-enabled/asociacion
```

### Verificar el contenido del archivo:

```bash
cat /etc/nginx/sites-available/asociacion | grep server_name
```

**Debe mostrar:**
```nginx
server_name avmontealto.es www.avmontealto.es;
```

### Verificar que la configuración es válida:

```bash
sudo nginx -t
```

**Resultado esperado:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

## 🔧 Paso 5: Verificar que Gunicorn responde localmente

```bash
# Probar que Gunicorn responde en el puerto 8000
curl http://127.0.0.1:8000

# Debe mostrar HTML de la aplicación (no error)
```

Si no responde:
```bash
# Verificar logs
sudo journalctl -u asociacion.service -n 50
```

## 🔧 Paso 6: Verificar que Nginx puede acceder a Gunicorn

```bash
# Probar desde el servidor
curl http://localhost

# Debe mostrar HTML de la aplicación
```

Si muestra error 502:
- Verifica que Gunicorn está corriendo (Paso 3)
- Verifica los logs: `sudo tail -f /var/log/nginx/asociacion_error.log`

## 🔧 Paso 7: Verificar permisos de la base de datos

```bash
# Verificar permisos del directorio instance/
ls -la /home/asociacion/asociacion_vps/instance/

# Debe mostrar algo como:
# -rw-rw-r-- 1 asociacion www-data asociacion.db
```

Si los permisos son incorrectos:
```bash
sudo chown -R asociacion:www-data /home/asociacion/asociacion_vps/instance
sudo chmod -R 775 /home/asociacion/asociacion_vps/instance
```

## 🔧 Paso 8: Verificar variables de entorno

```bash
# Verificar que el archivo .env existe
ls -la /home/asociacion/asociacion_vps/.env

# Verificar que tiene los permisos correctos
# Debe mostrar: -rw------- (600)
```

Si los permisos son incorrectos:
```bash
sudo chmod 600 /home/asociacion/asociacion_vps/.env
sudo chown asociacion:asociacion /home/asociacion/asociacion_vps/.env
```

## 🔧 Paso 9: Verificar firewall

```bash
# Verificar que el puerto 80 está abierto
sudo ufw status

# Debe mostrar:
# 80/tcp (Nginx Full)    ALLOW    Anywhere
```

Si no está abierto:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw reload
```

## 🌐 Paso 10: Probar desde el navegador

1. **Abre tu navegador** y visita:
   - `http://avmontealto.es`
   - `http://www.avmontealto.es`

2. **Resultado esperado:**
   - Debe cargar la página de login de la aplicación
   - No debe mostrar errores 502, 503, o 404

3. **Si no carga:**
   - Verifica los logs de Nginx: `sudo tail -f /var/log/nginx/asociacion_error.log`
   - Verifica los logs de la app: `sudo journalctl -u asociacion.service -f`

## 📋 Checklist Completo

Ejecuta este script de verificación rápida:

```bash
#!/bin/bash
echo "=== Verificación del Despliegue ==="
echo ""

echo "1. DNS:"
nslookup avmontealto.es | grep -A 1 "Name:"
echo ""

echo "2. Nginx status:"
systemctl is-active nginx
echo ""

echo "3. Aplicación status:"
systemctl is-active asociacion.service
echo ""

echo "4. Nginx habilitado:"
systemctl is-enabled nginx
echo ""

echo "5. Aplicación habilitada:"
systemctl is-enabled asociacion.service
echo ""

echo "6. Configuración Nginx válida:"
sudo nginx -t 2>&1 | grep -i "successful\|error"
echo ""

echo "7. Gunicorn responde:"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000
echo ""
echo ""

echo "8. Nginx proxy funciona:"
curl -s -o /dev/null -w "%{http_code}" http://localhost
echo ""
echo ""

echo "9. Permisos BD:"
ls -l /home/asociacion/asociacion_vps/instance/asociacion.db 2>/dev/null | awk '{print $1, $3, $4}'
echo ""

echo "10. Firewall:"
sudo ufw status | grep -i "nginx\|80"
echo ""
```

## 🐛 Solución de Problemas Comunes

### El dominio no resuelve a la IP correcta

**Causa:** DNS aún no propagado o configuración incorrecta en IONOS

**Solución:**
1. Verifica en el panel de IONOS que el registro A apunta a `94.143.140.75`
2. Espera 15 minutos - 2 horas para la propagación
3. Limpia la caché DNS local:
   ```powershell
   # En Windows PowerShell (como administrador)
   ipconfig /flushdns
   ```

### Error 502 Bad Gateway

**Causa:** Nginx no puede conectarse a Gunicorn

**Solución:**
```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status asociacion.service

# Si no está corriendo, iniciarlo
sudo systemctl start asociacion.service

# Verificar logs
sudo journalctl -u asociacion.service -n 50
```

### Error 503 Service Unavailable

**Causa:** El servicio está detenido o hay un error en la aplicación

**Solución:**
```bash
# Verificar estado
sudo systemctl status asociacion.service

# Ver logs detallados
sudo journalctl -u asociacion.service -f
```

### La página carga pero muestra errores de base de datos

**Causa:** Permisos incorrectos en la base de datos

**Solución:**
```bash
sudo chown -R asociacion:www-data /home/asociacion/asociacion_vps/instance
sudo chmod -R 775 /home/asociacion/asociacion_vps/instance
sudo systemctl restart asociacion.service
```

### El dominio carga pero es muy lento

**Causa:** Puede ser normal en el primer acceso (carga de módulos Python)

**Verificación:**
```bash
# Verificar uso de recursos
htop
# o
top

# Verificar logs de rendimiento
sudo tail -f /var/log/asociacion/error.log
```

## ✅ Verificación Final desde el Navegador

1. **Accede a:** `http://avmontealto.es`
2. **Debes ver:** La página de login de la aplicación
3. **Prueba hacer login** con un usuario administrador
4. **Verifica que puedes navegar** por la aplicación sin errores

Si todo esto funciona, ¡tu despliegue está completo y funcionando! 🎉




