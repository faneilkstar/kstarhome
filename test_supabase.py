#!/usr/bin/env python3
"""
Script de test de connexion Supabase
Aide à diagnostiquer les problèmes de connexion
"""

import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

print("🔍 Diagnostic Connexion Supabase")
print("=" * 60)

# Récupérer l'URL
url = os.getenv('SUPABASE_DB_URL')

if not url:
    print("❌ SUPABASE_DB_URL non définie dans .env")
    print("\n📝 Allez sur Supabase:")
    print("   1. https://supabase.com/dashboard/project/pzzfqduntcmklrakhggy/settings/database")
    print("   2. Copiez la 'Connection string' (mode Transaction pooling)")
    print("   3. Collez-la dans .env")
    exit(1)

print(f"\n✅ URL trouvée")
print(f"URL (tronquée): {url[:60]}...")

# Parser l'URL
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

try:
    from urllib.parse import urlparse
    parsed = urlparse(url)

    print(f"\n📋 Détails de connexion:")
    print(f"   Protocol: {parsed.scheme}")
    print(f"   Host: {parsed.hostname}")
    print(f"   Port: {parsed.port}")
    print(f"   User: {parsed.username}")
    print(f"   Password: {'*' * len(parsed.password) if parsed.password else 'NON DÉFINI'}")
    print(f"   Database: {parsed.path[1:]}")

    # Tester la connexion
    print(f"\n🔌 Test de connexion...")

    try:
        import psycopg2

        # Décoder le mot de passe
        password = urllib.parse.unquote(parsed.password) if parsed.password else ""

        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=password,
            database=parsed.path[1:],
            connect_timeout=10
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]

        print(f"✅ CONNEXION RÉUSSIE!")
        print(f"\n🎉 PostgreSQL version: {version[:50]}...")

        cursor.close()
        conn.close()

        print("\n✨ Votre configuration Supabase est CORRECTE!")
        print("   Vous pouvez lancer: flask db upgrade")

    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ ERREUR DE CONNEXION")
        print(f"\n{error_msg}")

        if "Tenant or user not found" in error_msg:
            print("\n🔍 Problème identifié:")
            print("   • Le mot de passe ou l'ID de projet est INCORRECT")
            print("\n📝 Solution:")
            print("   1. Allez sur: https://supabase.com/dashboard")
            print("   2. Sélectionnez votre projet")
            print("   3. Settings → Database")
            print("   4. Section 'Connection string'")
            print("   5. Sélectionnez 'Transaction' mode (port 6543)")
            print("   6. Copiez l'URL COMPLÈTE")
            print("   7. Remplacez [YOUR-PASSWORD] par votre vrai mot de passe")
            print("   8. Collez dans .env: SUPABASE_DB_URL=...")

        elif "timeout" in error_msg.lower():
            print("\n🔍 Problème identifié:")
            print("   • Timeout de connexion (problème réseau)")
            print("\n📝 Solution:")
            print("   • Vérifiez votre connexion internet")
            print("   • Le firewall bloque peut-être le port 6543")

except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

