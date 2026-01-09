"""
Vercel serverless entry point
"""
from app import app

# Vercel will call this
def handler(request):
    return app(request.environ, lambda *args: None)
