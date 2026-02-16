#!/usr/bin/env python3
"""Test de connexion Supabase"""
import psycopg2
from urllib.parse import quote_plus

# Mot de passe encodé
password = quote_plus("masque de mort")
project_id = "pzzfqduntcmklrakhggy"

# Différentes régions à tester
regions = [
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "us-east-1",
    "ap-southeast-1"
]

print("🔍 Test de connexion Supabase...")
print(f"📌 Projet ID: {project_id}")
print(f"🔑 Mot de passe: masque de mort (encodé: {password})")
print()

for port in [6543, 5432]:
    print(f"\n🔌 Testing PORT {port}...")
    for region in regions:
        host = f"aws-0-{region}.pooler.supabase.com"
        connection_string = f"postgresql://postgres.{project_id}:{password}@{host}:{port}/postgres"

        print(f"  {region} (port {port})... ", end="")
        try:
            conn = psycopg2.connect(connection_string, connect_timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ CONNEXION RÉUSSIE!")
            print(f"     Host: {host}")
            print(f"     Port: {port}")
            print(f"     PostgreSQL: {version[0][:50]}...")
            cursor.close()
            conn.close()
            print()
            print("=" * 70)
            print(f"✅ URL DE CONNEXION CORRECTE:")
            print(f"postgresql://postgres.{project_id}:{password}@{host}:{port}/postgres")
            print("=" * 70)
            exit(0)
        except Exception as e:
            print(f"❌ {str(e)[:40]}")

print("\n✅ Test terminé!")

