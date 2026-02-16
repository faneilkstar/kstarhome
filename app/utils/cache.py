"""
Système de cache avec Redis
"""

import redis
import json
import os
from functools import wraps
from flask import current_app

# Configuration Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    print("⚠️ Redis non disponible, cache désactivé")


def cache_result(timeout=300, key_prefix=''):
    """
    Décorateur pour mettre en cache les résultats de fonctions

    Args:
        timeout: Durée du cache en secondes (défaut: 5min)
        key_prefix: Préfixe pour la clé de cache
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return f(*args, **kwargs)

            # Générer la clé de cache
            cache_key = f"{key_prefix}:{f.__name__}:{str(args)}:{str(kwargs)}"

            # Vérifier le cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Exécuter la fonction
            result = f(*args, **kwargs)

            # Mettre en cache
            redis_client.setex(
                cache_key,
                timeout,
                json.dumps(result, default=str)
            )

            return result

        return decorated_function

    return decorator


def invalidate_cache(pattern):
    """Invalide les clés de cache correspondant au pattern"""
    if not REDIS_AVAILABLE:
        return

    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)


def get_cache_stats():
    """Récupère les statistiques du cache"""
    if not REDIS_AVAILABLE:
        return {'error': 'Redis non disponible'}

    info = redis_client.info()

    return {
        'total_keys': redis_client.dbsize(),
        'used_memory': info.get('used_memory_human', 'N/A'),
        'connected_clients': info.get('connected_clients', 0),
        'hit_rate': 'N/A'  # Calculer si nécessaire
    }