# 🔧 Solución: Error "attempt to write a readonly database"

Este error ocurre cuando SQLite no tiene permisos de escritura en el archivo de base de datos o su directorio.

## 🚨 Solución Rápida

Ejecuta estos comandos en el servidor para corregir los permisos:

```bash
# 1. Identificar dónde está la base de datos
# La base de datos debería estar en:
# /home/asociacion/asociacion_vps/instance/asociacion.db

# 2. Corregir permisos del directorio instance/
sudo chown -R asociacion:www-data /home/asociacion/asociacion_vps/instance
sudo chmod -R 775 /home/asociacion/asociacion_vps/instance

# 3. Si el archivo de base de datos ya existe, corregir sus permisos específicamente
sudo chown asociacion:www-data /home/asociacion/asociacion_vps/instance/asociacion.db
sudo chmod 664 /home/asociacion/asociacion_vps/instance/asociacion.db

# 4. Asegurarse de que el directorio padre también tiene permisos correctos
sudo chown -R asociacion:www-data /home/asociacion/asociacion_vps
sudo chmod -R 755 /home/asociacion/asociacion_vps

# 5. Reiniciar el servicio de la aplicación
sudo systemctl restart asociacion.service

# 6. Verificar que funciona
sudo systemctl status asociacion.service
```

## 🔍 Verificación Detallada

### Paso 1: Verificar dónde está la base de datos

```bash
# Verificar si existe el archivo
ls -la /home/asociacion/asociacion_vps/instance/asociacion.db

# Ver los permisos actuales
stat /home/asociacion/asociacion_vps/instance/asociacion.db
```

### Paso 2: Verificar el propietario y permisos

El archivo debe ser propiedad de `asociacion` y tener permisos de lectura y escritura:

```bash
# Debe mostrar algo como:
# -rw-rw-r-- 1 asociacion www-data 123456 fecha asociacion.db
```

Si muestra otro propietario (como `root`), necesitas corregirlo.

### Paso 3: Verificar permisos del directorio

El directorio `instance/` también debe tener permisos correctos:

```bash
ls -ld /home/asociacion/asociacion_vps/instance
# Debe mostrar: drwxrwxr-x asociacion www-data
```

## 🛠️ Solución Completa (Paso a Paso)

### Opción A: Si la base de datos NO existe aún

```bash
# 1. Crear el directorio si no existe
sudo mkdir -p /home/asociacion/asociacion_vps/instance

# 2. Establecer permisos correctos
sudo chown -R asociacion:www-data /home/asociacion/asociacion_vps/instance
sudo chmod -R 775 /home/asociacion/asociacion_vps/instance

# 3. Reiniciar el servicio (la app creará la BD automáticamente)
sudo systemctl restart asociacion.service
```

### Opción B: Si la base de datos YA existe

```bash
# 1. Detener el servicio temporalmente
sudo systemctl stop asociacion.service

# 2. Corregir permisos del archivo de base de datos
sudo chown asociacion:www-data /home/asociacion/asociacion_vps/instance/asociacion.db
sudo chmod 664 /home/asociacion/asociacion_vps/instance/asociacion.db

# 3. Corregir permisos del directorio
sudo chown asociacion:www-data /home/asociacion/asociacion_vps/instance
sudo chmod 775 /home/asociacion/asociacion_vps/instance

# 4. Verificar permisos
ls -la /home/asociacion/asociacion_vps/instance/

# 5. Reiniciar el servicio
sudo systemctl start asociacion.service

# 6. Verificar que funciona
sudo systemctl status asociacion.service
```

## 🔐 Permisos Recomendados

Para producción, estos son los permisos recomendados:

```
/home/asociacion/asociacion_vps/
├── owner: asociacion
├── group: www-data
└── permissions: 755 (drwxr-xr-x)

/home/asociacion/asociacion_vps/instance/
├── owner: asociacion
├── group: www-data
└── permissions: 775 (drwxrwxr-x)

/home/asociacion/asociacion_vps/instance/asociacion.db
├── owner: asociacion
├── group: www-data
└── permissions: 664 (-rw-rw-r--)
```

## 🐛 Solución de Problemas Adicionales

### Si el problema persiste después de corregir permisos:

1. **Verificar que el servicio se ejecuta con el usuario correcto:**

```bash
# Verificar el servicio systemd
sudo systemctl status asociacion.service

# Verificar el usuario en el archivo de servicio
cat /etc/systemd/system/asociacion.service | grep User
# Debe mostrar: User=asociacion
```

2. **Verificar que no hay archivos WAL bloqueados:**

SQLite con WAL mode crea archivos `.db-wal` y `.db-shm`. Estos también necesitan permisos:

```bash
# Si existen, corregir sus permisos también
sudo chown asociacion:www-data /home/asociacion/asociacion_vps/instance/asociacion.db-wal
sudo chown asociacion:www-data /home/asociacion/asociacion_vps/instance/asociacion.db-shm
sudo chmod 664 /home/asociacion/asociacion_vps/instance/asociacion.db-wal
sudo chmod 664 /home/asociacion/asociacion_vps/instance/asociacion.db-shm
```

3. **Verificar logs para más detalles:**

```bash
# Logs del servicio
sudo journalctl -u asociacion.service -n 50 --no-pager

# Logs de error de Gunicorn
sudo tail -f /var/log/asociacion/error.log
```

4. **Verificar espacio en disco:**

```bash
df -h /home/asociacion/asociacion_vps/instance
```

Si el disco está lleno, SQLite no puede escribir.

## ✅ Verificación Final

Después de aplicar los cambios, prueba crear una solicitud desde la aplicación. Si el error persiste:

1. Verifica los logs: `sudo journalctl -u asociacion.service -f`
2. Verifica permisos: `ls -la /home/asociacion/asociacion_vps/instance/`
3. Verifica que el usuario asociacion puede escribir:

```bash
# Cambiar al usuario asociacion
sudo su - asociacion

# Intentar escribir en el directorio
touch /home/asociacion/asociacion_vps/instance/test.txt
rm /home/asociacion/asociacion_vps/instance/test.txt

# Si esto falla, hay un problema de permisos más profundo
```

## 📝 Nota sobre SELinux (si está activo)

Si tu servidor tiene SELinux activo, puede estar bloqueando el acceso. En Ubuntu normalmente no está activo, pero si lo está:

```bash
# Verificar si SELinux está activo
getenforce

# Si está en "Enforcing", puedes desactivarlo temporalmente o configurar políticas
# (Normalmente no necesario en Ubuntu)
```






