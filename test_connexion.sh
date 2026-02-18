#!/bin/bash

echo "=================================================="
echo "🔍 TEST DE CONNEXION SUPABASE"
echo "=================================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Charger l'environnement virtuel
source venv/bin/activate

# Test de connexion avec Python
python3 << 'PYEOF'
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DATABASE_URL', '')

if not db_url:
    print("❌ DATABASE_URL non trouvée dans .env")
    exit(1)

# Extraire les infos
import re
pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(\w+)'
match = re.match(pattern, db_url.split('?')[0])

if match:
    user, password, host, port, database = match.groups()
    print(f"📊 Configuration détectée:")
    print(f"   Hôte: {host}")
    print(f"   Port: {port}")
    print(f"   Base: {database}")
    print(f"   User: {user}")
    print(f"   Pass: {'*' * len(password)} ({len(password)} caractères)")
    print()

    # Test de connexion
    try:
        import psycopg2
        print("🔄 Tentative de connexion...")

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            sslmode='require'
        )

        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()

        print("✅ CONNEXION RÉUSSIE!")
        print(f"   PostgreSQL: {version[0].split(',')[0]}")

        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchone()[0]
        print(f"   Tables: {tables}")

        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        error_str = str(e)
        if 'password authentication failed' in error_str:
            print("❌ MOT DE PASSE INCORRECT!")
            print()
            print("💡 Actions à faire:")
            print("   1. Allez sur https://supabase.com/dashboard")
            print("   2. Settings → Database → Reset database password")
            print("   3. Créez un nouveau mot de passe")
            print("   4. Mettez-le à jour dans le fichier .env")
        elif 'SSL' in error_str:
            print("❌ Erreur SSL - Vérifiez ?sslmode=require")
        else:
            print(f"❌ Erreur de connexion: {error_str}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
PYEOF

echo ""
echo "=================================================="

