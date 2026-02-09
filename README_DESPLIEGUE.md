# 📦 Archivos de Configuración para Despliegue en VPS

Este proyecto incluye todos los archivos necesarios para desplegar la aplicación en un VPS de IONOS con Ubuntu 24.04.

## 📁 Estructura de Archivos Creados

```
asociacion_vps/
├── gunicorn_config.py          # Configuración de Gunicorn
├── wsgi.py                      # Punto de entrada WSGI (ya existía)
├── nginx/
│   └── asociacion.conf         # Configuración de Nginx
├── systemd/
│   └── asociacion.service      # Servicio systemd
├── scripts/
│   └── deploy.sh               # Script de ayuda para despliegue
└── DEPLOY_VPS_IONOS.md         # Documento con instrucciones completas
```

## 🚀 Inicio Rápido

1. **Lee el documento principal**: `DEPLOY_VPS_IONOS.md` contiene todas las instrucciones paso a paso.

2. **Archivos principales**:
   - `gunicorn_config.py`: Configuración del servidor WSGI
   - `nginx/asociacion.conf`: Configuración del servidor web
   - `systemd/asociacion.service`: Servicio para iniciar automáticamente la app

3. **Script de ayuda**: El script `scripts/deploy.sh` puede ayudarte a automatizar algunos pasos básicos.

## 📋 Checklist Pre-Despliegue

Antes de comenzar, asegúrate de tener:

- [ ] VPS de IONOS con Ubuntu 24.04
- [ ] Acceso SSH al servidor
- [ ] Todos los archivos del proyecto listos para subir
- [ ] Dominio configurado (opcional pero recomendado)

## 🔐 Variables de Entorno Necesarias

Crea un archivo `.env` en el servidor con:

```bash
SECRET_KEY=tu_clave_secreta_muy_segura
FLASK_ENV=production
PORT=8000
```

Genera una clave secreta segura con:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 📖 Documentación Completa

Para instrucciones detalladas, consulta: **`DEPLOY_VPS_IONOS.md`**

## ⚙️ Configuración de la Base de Datos

La aplicación usa SQLite por defecto. La base de datos se creará automáticamente en:
```
/home/asociacion/asociacion_vps/instance/asociacion.db
```

Si prefieres usar PostgreSQL, configura la variable `DATABASE_URL` en el archivo `.env`.

## 🆘 Soporte

Si encuentras problemas durante el despliegue:

1. Revisa los logs del servicio: `journalctl -u asociacion.service -f`
2. Revisa los logs de Nginx: `tail -f /var/log/nginx/asociacion_error.log`
3. Consulta la sección de "Solución de Problemas" en `DEPLOY_VPS_IONOS.md`





