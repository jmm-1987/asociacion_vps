"""
Configuración de Gunicorn para producción
"""
import multiprocessing
import os

# Configuración del servidor
bind = f"127.0.0.1:{os.environ.get('PORT', '8000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Configuración de logging
accesslog = "/var/log/asociacion/access.log"
errorlog = "/var/log/asociacion/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de procesos
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de usuario (se configurará en systemd)
# user = "www-data"
# group = "www-data"

# Configuración de threads (si se usa worker_class = "gthread")
# threads = 2





