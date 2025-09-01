# Gunicorn configuration file

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 2
preload_app = True

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "myunsejeomju_admin"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
pidfile = "/tmp/gunicorn.pid"
user = "django"
group = "django"
tmp_upload_dir = None