# backend/wsgi.py
from app import app as application

# O nome 'application' é um padrão esperado pela maioria dos servidores WSGI
# (como o que a Hostinger usa para Python).