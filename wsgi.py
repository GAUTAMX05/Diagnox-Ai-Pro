"""WSGI entry point — use: python wsgi.py  OR  waitress-serve --listen=127.0.0.1:5000 wsgi:application"""
from app import app as application

if __name__ == "__main__":
    application.run(host="127.0.0.1", port=5000, debug=False)
