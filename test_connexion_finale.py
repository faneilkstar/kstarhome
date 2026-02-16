#!/usr/bin/env python3
"""Test connexion avec aws-1-eu-west-1"""
import psycopg2

DB_URL = "postgresql://postgres.pzzfqduntcmklrakhggy:masqquedemort@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"

print("🔍 Test de connexion Supabase IRLANDE (aws-1-eu-west-1)...")
print(f"🔑 Mot de passe : masqquedemort")
print(f"📍 Région : aws-1-eu-west-1")
print(f"🔌 Port : 6543")
print()

try:
    print("⏳ Connexion en cours...", end="", flush=True)
    conn = psycopg2.connect(DB_URL, connect_timeout=10)
    print(" ✅")

    cursor = conn.cursor()

    # Test 1: Version
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"\n✅ CONNEXION RÉUSSIE!")
    print(f"📦 PostgreSQL: {version[:80]}...")

    # Test 2: Tables
    cursor.execute("""
        SELECT tablename FROM pg_catalog.pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename;
    """)
    tables = cursor.fetchall()
    print(f"\n📊 Tables trouvées: {len(tables)}")
    if tables:
        print("   Premières tables:")
        for table in tables[:15]:
            print(f"   ✓ {table[0]}")
        if len(tables) > 15:
            print(f"   ... et {len(tables) - 15} autres")

    # Test 3: Users
    try:
        cursor.execute("SELECT COUNT(*) FROM users;")
        nb_users = cursor.fetchone()[0]
        print(f"\n👥 Utilisateurs: {nb_users}")
    except:
        print(f"\n👥 Table 'users' non trouvée ou vide")

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("✅ SUPABASE EST CONNECTÉ!")
    print("🚀 Tu peux maintenant lancer: python run.py")
    print("=" * 70)

except Exception as e:
    print(f"\n\n❌ ERREUR:")
    print(f"   {str(e)}")
    print("\n💡 Vérifie:")
    print("   1. Que le mot de passe est bien 'masqquedemort'")
    print("   2. Que la région est bien 'aws-1-eu-west-1'")
    print("   3. Que le pooler est activé sur Supabase")

