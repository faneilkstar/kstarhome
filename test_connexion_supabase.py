#!/usr/bin/env python3
"""Test rapide de connexion Supabase"""
import psycopg2

# Configuration exacte
DB_URL = "postgresql://postgres.pzzfqduntcmklrakhggy:masqquedemort@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

print("🔍 Test de connexion Supabase...")
print(f"🔑 Mot de passe : masqquedemort")
print(f"📍 URL : {DB_URL.split('://')[1].split(':masqquedemort')[0]}...@...")
print()

try:
    conn = psycopg2.connect(DB_URL, connect_timeout=10)
    cursor = conn.cursor()

    # Test 1: Version PostgreSQL
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ CONNEXION RÉUSSIE!")
    print(f"   PostgreSQL: {version[:60]}...")

    # Test 2: Lister les tables
    cursor.execute("""
        SELECT tablename FROM pg_catalog.pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename;
    """)
    tables = cursor.fetchall()
    print(f"\n📊 Tables trouvées ({len(tables)}) :")
    for table in tables[:10]:  # Afficher les 10 premières
        print(f"   - {table[0]}")
    if len(tables) > 10:
        print(f"   ... et {len(tables) - 10} autres")

    # Test 3: Vérifier la table users
    cursor.execute("SELECT COUNT(*) FROM users;")
    nb_users = cursor.fetchone()[0]
    print(f"\n👥 Utilisateurs dans la base : {nb_users}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("✅ SUPABASE EST PRÊT ! Tu peux lancer : python run.py")
    print("=" * 70)

except Exception as e:
    print(f"❌ ERREUR DE CONNEXION:")
    print(f"   {str(e)}")
    print("\n💡 Solutions possibles:")
    print("   1. Vérifie que le mot de passe est bien 'masqquedemort'")
    print("   2. Va sur Supabase > Connect > URI et copie l'URL complète")
    print("   3. Vérifie la région (eu-central-1 vs eu-west-3, etc.)")

