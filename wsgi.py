"""Entry point for production servers:  gunicorn wsgi:application   (PythonAnywhere imports `application` too)."""
from app import create_app

application = create_app()
