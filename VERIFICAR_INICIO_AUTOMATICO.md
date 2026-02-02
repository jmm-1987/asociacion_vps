# ✅ Verificar y Configurar Inicio Automático de la Aplicación

## 🔍 Verificar si está configurado para iniciarse automáticamente

Ejecuta este comando en el servidor:

```bash
systemctl is-enabled asociacion.service
```

### Resultados posibles:

- **`enabled`** ✅ → La aplicación se iniciará automáticamente al reiniciar el servidor
- **`disabled`** ❌ → La aplicación NO se iniciará automáticamente
- **`static`** → El servicio está disponible pero no se inicia automáticamente

## 🔧 Habilitar el inicio automático

Si el resultado es `disabled` o `static`, ejecuta:

```bash
sudo systemctl enable asociacion.service
```

Esto creará un enlace simbólico para que el servicio se inicie automáticamente al arrancar el sistema.

## ✅ Verificación Completa

Para verificar que todo está correctamente configurado:

```bash
# 1. Verificar que el servicio está habilitado
systemctl is-enabled asociacion.service
# Debe mostrar: enabled

# 2. Verificar que el servicio está corriendo
systemctl status asociacion.service
# Debe mostrar: active (running)

# 3. Verificar que Nginx también está habilitado
systemctl is-enabled nginx
# Debe mostrar: enabled
```

## 🧪 Probar el inicio automático (sin reiniciar)

Puedes simular un reinicio para verificar que todo funciona:

```bash
# 1. Detener el servicio manualmente
sudo systemctl stop asociacion.service

# 2. Verificar que está detenido
sudo systemctl status asociacion.service
# Debe mostrar: inactive (dead)

# 3. Iniciar el servicio (esto simula lo que haría el sistema al arrancar)
sudo systemctl start asociacion.service

# 4. Verificar que se inició correctamente
sudo systemctl status asociacion.service
# Debe mostrar: active (running)
```

## 📋 Comandos Útiles

### Ver el estado completo del servicio:

```bash
systemctl status asociacion.service
```

### Ver si está habilitado para inicio automático:

```bash
systemctl is-enabled asociacion.service
```

### Habilitar inicio automático:

```bash
sudo systemctl enable asociacion.service
```

### Deshabilitar inicio automático (si no lo quieres):

```bash
sudo systemctl disable asociacion.service
```

### Ver todos los servicios habilitados:

```bash
systemctl list-unit-files --type=service --state=enabled | grep asociacion
```

## 🔄 Configuración del Servicio

El servicio está configurado con:

- **`WantedBy=multi-user.target`**: Se inicia cuando el sistema alcanza el nivel de ejecución multi-usuario (modo normal)
- **`Restart=always`**: Se reinicia automáticamente si se detiene o falla
- **`RestartSec=3`**: Espera 3 segundos antes de reiniciar

Esto significa que:
1. ✅ Se iniciará automáticamente al arrancar el servidor (si está habilitado)
2. ✅ Se reiniciará automáticamente si se detiene inesperadamente
3. ✅ Se reiniciará automáticamente si falla

## 🚨 Si el servicio NO se inicia automáticamente

### Paso 1: Verificar que el archivo de servicio existe

```bash
ls -la /etc/systemd/system/asociacion.service
```

### Paso 2: Recargar systemd

```bash
sudo systemctl daemon-reload
```

### Paso 3: Habilitar el servicio

```bash
sudo systemctl enable asociacion.service
```

### Paso 4: Verificar

```bash
systemctl is-enabled asociacion.service
# Debe mostrar: enabled
```

## 📝 Nota sobre Nginx

Nginx también debe estar habilitado para iniciarse automáticamente:

```bash
# Verificar
systemctl is-enabled nginx

# Habilitar si no lo está
sudo systemctl enable nginx
```

## ✅ Checklist Final

Antes de reiniciar el servidor, verifica:

- [ ] `systemctl is-enabled asociacion.service` muestra `enabled`
- [ ] `systemctl is-enabled nginx` muestra `enabled`
- [ ] `systemctl status asociacion.service` muestra `active (running)`
- [ ] `systemctl status nginx` muestra `active (running)`

Si todos los puntos están marcados, al reiniciar el servidor, tanto Nginx como tu aplicación se iniciarán automáticamente.



