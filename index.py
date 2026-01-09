"""
Vercel serverless entry point
"""
from app import app

# Export for Vercel
application = app
