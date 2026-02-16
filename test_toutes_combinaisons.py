#!/usr/bin/env python3
"""Test TOUTES les combinaisons possibles"""
import psycopg2

project_id = "pzzfqduntcmklrakhggy"
passwords = ["masqquedemort", "masque%20de%20mort", "masque de mort"]
regions = ["eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "us-east-1", "ap-southeast-1"]
ports = [6543, 5432]

print("🔍 Test de TOUTES les combinaisons possibles...")
print()

for password in passwords:
    print(f"\n🔑 Test avec mot de passe: '{password}'")
    for port in ports:
        print(f"   Port {port}:")
        for region in regions:
            host = f"aws-0-{region}.pooler.supabase.com"
            url = f"postgresql://postgres.{project_id}:{password}@{host}:{port}/postgres"

            print(f"      {region}... ", end="", flush=True)
            try:
                conn = psycopg2.connect(url, connect_timeout=3)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public';")
                nb_tables = cursor.fetchone()[0]
                cursor.close()
                conn.close()

                print(f"✅ CONNEXION OK! ({nb_tables} tables)")
                print("\n" + "=" * 70)
                print(f"✅ URL CORRECTE TROUVÉE:")
                print(f"{url}")
                print("=" * 70)
                exit(0)

            except Exception as e:
                error_msg = str(e)[:40]
                print(f"❌ {error_msg}")

print("\n❌ Aucune combinaison ne fonctionne.")
print("💡 Va sur Supabase > Connect > URI et copie l'URL COMPLÈTE")

