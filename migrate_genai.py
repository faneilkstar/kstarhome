#!/usr/bin/env python3
"""
Script pour migrer tous les fichiers de google.generativeai vers google.genai
"""

import os
import re

# Fichiers à mettre à jour
fichiers = [
    'app/services/ia_laboratoire_avancee.py',
    'app/services/ia_laboratoire_ultra.py',
    'app/services/ia_bibliotheque.py',
    'app/services/ia_rapports_enseignant.py',
    'app/services/ia_laboratoire_v2.py',
]

print("🔄 Migration vers google.genai...")
print("=" * 60)

for fichier in fichiers:
    if not os.path.exists(fichier):
        print(f"⚠️  {fichier} introuvable, ignoré")
        continue

    print(f"\n📝 Traitement de {fichier}...")

    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            contenu = f.read()

        # Sauvegarder l'original
        backup = fichier + '.backup'
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(contenu)

        # Remplacements
        modifications = 0

        # 1. Import
        if 'import google.generativeai as genai' in contenu:
            contenu = contenu.replace(
                'import google.generativeai as genai',
                'from google import genai\n    from google.genai import types'
            )
            modifications += 1
            print("   ✅ Import mis à jour")

        # 2. genai.configure() → Client
        pattern_config = r'genai\.configure\(api_key=([^)]+)\)'
        if re.search(pattern_config, contenu):
            # Rechercher la création du model après configure
            if 'GenerativeModel' in contenu:
                # Remplacer par Client
                contenu = re.sub(
                    r"genai\.configure\(api_key=([^)]+)\)\s+self\.model\s*=\s*genai\.GenerativeModel\('([^']+)'\)",
                    r"self.client = genai.Client(api_key=\1)",
                    contenu
                )
                modifications += 1
                print("   ✅ Configuration convertie en Client")

        # 3. self.model.generate_content() → self.client.models.generate_content()
        if 'self.model.generate_content(' in contenu:
            # Rechercher tous les appels
            pattern = r'self\.model\.generate_content\(([^)]+)\)'
            matches = re.findall(pattern, contenu)

            for match in matches:
                old_call = f'self.model.generate_content({match})'
                new_call = f"self.client.models.generate_content(\n                model='gemini-2.0-flash-exp',\n                contents={match}\n            )"
                contenu = contenu.replace(old_call, new_call)
                modifications += 1

            if modifications > 0:
                print(f"   ✅ {modifications} appels generate_content mis à jour")

        # Écrire le fichier modifié
        with open(fichier, 'w', encoding='utf-8') as f:
            f.write(contenu)

        if modifications > 0:
            print(f"   ✅ {fichier} mis à jour ({modifications} modifications)")
        else:
            print(f"   ℹ️  Aucune modification nécessaire")
            os.remove(backup)  # Supprimer le backup si aucune modif

    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        if os.path.exists(backup):
            # Restaurer le backup en cas d'erreur
            os.rename(backup, fichier)

print("\n" + "=" * 60)
print("✅ Migration terminée !")
print("\nLes backups sont dans *.backup (à supprimer si tout fonctionne)")

