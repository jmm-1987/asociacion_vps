# 🌐 Guía para Configurar el Dominio en IONOS

Esta guía te ayudará a configurar tu dominio para que apunte a tu VPS.

## 📋 Paso 1: Identificar tu Dominio

Primero, identifica cuál es tu dominio. Basándome en la configuración DNS que veo, parece que tienes un dominio configurado en IONOS.

## 🔧 Paso 2: Modificar el Registro A en IONOS

1. **Accede al panel de gestión de DNS de IONOS:**
   - Ve a tu panel de control de IONOS
   - Navega a la sección de **DNS** o **Gestión de Dominios**
   - Selecciona tu dominio

2. **Localiza el registro A para el dominio raíz (@):**
   - Busca el registro de tipo **A** con el nombre de host `@` (o el nombre de tu dominio raíz)
   - Actualmente apunta a: `216.24.57.1`

3. **Edita el registro A:**
   - Haz clic en el icono de **editar** (lápiz) del registro A
   - Cambia el **VALOR** (IP) de `216.24.57.1` a `94.143.140.75`
   - Guarda los cambios

4. **Configura también el subdominio www (opcional pero recomendado):**
   - Busca el registro **CNAME** para `www`
   - Actualmente apunta a: `asociacion-dw0f.onrender.com`
   - Tienes dos opciones:
     
     **Opción A: Cambiar a registro A (recomendado)**
     - Elimina el registro CNAME de `www`
     - Crea un nuevo registro **A** para `www`
     - Establece el valor a: `94.143.140.75`
     
     **Opción B: Mantener CNAME pero apuntar al dominio**
     - Cambia el CNAME de `www` para que apunte a tu dominio raíz (ej: `tu-dominio.com`)

## ⏱️ Paso 3: Esperar la Propagación DNS

Los cambios DNS pueden tardar entre **5 minutos y 48 horas** en propagarse completamente. Normalmente toma entre 15 minutos y 2 horas.

Puedes verificar la propagación usando:

```bash
# Desde tu máquina local (Windows PowerShell)
nslookup tu-dominio.com
# o
ping tu-dominio.com
```

O usar herramientas online como:
- https://www.whatsmydns.net/
- https://dnschecker.org/

## 🔧 Paso 4: Actualizar Configuración de Nginx

Una vez que sepas cuál es tu dominio exacto, actualiza la configuración de Nginx:

1. **Edita el archivo de configuración de Nginx en el servidor:**

```bash
sudo nano /etc/nginx/sites-available/asociacion
```

2. **Cambia la línea `server_name`:**

Si solo tienes el dominio raíz:
```nginx
server_name tu-dominio.com;
```

Si también quieres el subdominio www:
```nginx
server_name tu-dominio.com www.tu-dominio.com;
```

3. **Verifica y recarga Nginx:**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 📝 Ejemplo Completo

Si tu dominio es, por ejemplo, `asociacion.com`, la configuración quedaría así:

**En IONOS DNS:**
- Registro A para `@` → `94.143.140.75`
- Registro A para `www` → `94.143.140.75`

**En Nginx (`/etc/nginx/sites-available/asociacion`):**
```nginx
server_name asociacion.com www.asociacion.com;
```

## ✅ Verificación Final

Una vez configurado todo:

1. **Verifica que el DNS apunta correctamente:**
   ```bash
   nslookup tu-dominio.com
   # Debe mostrar: 94.143.140.75
   ```

2. **Accede desde el navegador:**
   - Abre: `http://tu-dominio.com`
   - Deberías ver tu aplicación funcionando

3. **Verifica los logs si hay problemas:**
   ```bash
   sudo tail -f /var/log/nginx/asociacion_error.log
   sudo journalctl -u asociacion.service -f
   ```

## 🔒 Paso 5: Configurar SSL/HTTPS (Recomendado)

Una vez que el dominio esté funcionando, configura HTTPS con Let's Encrypt:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

Esto configurará automáticamente HTTPS y redirigirá HTTP a HTTPS.

## 🐛 Solución de Problemas

### El dominio no resuelve a la IP correcta

- Espera más tiempo (hasta 48 horas)
- Verifica que guardaste los cambios en IONOS
- Limpia la caché DNS local:
  ```powershell
  # En Windows PowerShell (como administrador)
  ipconfig /flushdns
  ```

### Nginx muestra error 502

- Verifica que Gunicorn esté corriendo:
  ```bash
  sudo systemctl status asociacion.service
  ```

### El dominio carga pero muestra error

- Verifica los logs:
  ```bash
  sudo tail -f /var/log/nginx/asociacion_error.log
  sudo journalctl -u asociacion.service -f
  ```

## 📌 Notas Importantes

- **No elimines los registros MX** (correo electrónico) a menos que sepas lo que haces
- **No elimines los registros TXT de SPF/DKIM** si usas correo electrónico
- Los registros CNAME de `_domainkey` y `autodiscover` son para correo, déjalos como están
- Solo modifica el registro A del dominio raíz y el CNAME/A de `www`


