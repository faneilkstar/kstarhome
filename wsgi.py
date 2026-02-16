"""
WSGI entry point for Vercel deployment
"""
import os
from app import create_app

# Create the application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# This is what Vercel will use
application = app

if __name__ == "__main__":
    app.run()

