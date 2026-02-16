"""
Rate limiting pour l'API
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Ou Redis: "redis://localhost:6379"
)

# Utilisation dans les routes
# @limiter.limit("10 per minute")
# def route_sensible():
#     pass