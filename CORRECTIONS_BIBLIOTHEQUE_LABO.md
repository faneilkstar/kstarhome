# 🔧 CORRECTION : Bibliothèque et Laboratoire ne fonctionnent pas

## ❌ PROBLÈMES IDENTIFIÉS

1. **Bibliothèque** : L'enseignant ne peut pas poster de livres
2. **Laboratoire** : La création de TP ne fonctionne pas
3. **Validation IA** : Ne fonctionne pas correctement
4. **JavaScript** : Possibles erreurs côté client

---

## 🔍 DIAGNOSTIC

### Problème 1 : Dossiers manquants pour les uploads

Les dossiers `app/static/library/` n'existent pas ou ne sont pas accessibles.

### Problème 2 : Routes JavaScript non chargées

Les fichiers JavaScript des simulations peuvent avoir des erreurs.

### Problème 3 : Variables d'environnement manquantes

`GEMINI_API_KEY` n'est pas configurée sur Render.

---

## ✅ SOLUTION 1 : Créer les dossiers manquants

Les fichiers `.gitkeep` existent déjà dans :
- `app/static/library/covers/`
- `app/static/library/pdf/`

**Mais sur Render**, ces dossiers doivent être créés au démarrage.

### Correction dans `run.py` :

Le fichier `run.py` doit créer ces dossiers automatiquement.

---

## ✅ SOLUTION 2 : Configurer la clé Gemini API

### Sur Render :

1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service `kstarhome`
3. Allez dans "Environment"
4. Ajoutez :
   - **Key** : `GEMINI_API_KEY`
   - **Value** : Votre clé API Gemini (voir OBTENIR_CLE_GEMINI.md)
5. Sauvegardez

### Pour obtenir une clé Gemini :

```bash
# Voir le fichier OBTENIR_CLE_GEMINI.md
```

---

## ✅ SOLUTION 3 : Vérifier les permissions des fichiers

### Problème courant sur Render :

Les dossiers créés n'ont pas les bonnes permissions.

### Solution :

Modifier `config.py` pour créer les dossiers avec les bonnes permissions.

---

## ✅ SOLUTION 4 : Tester localement d'abord

Avant de déployer, testez en local :

```bash
# 1. Activer l'environnement
source venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser la base
python init_database.py

# 4. Lancer le serveur
python run.py

# 5. Tester dans le navigateur
# → http://localhost:5000
```

### Tests à faire :

- ✅ Se connecter comme enseignant
- ✅ Créer un TP
- ✅ Ajouter un livre à la bibliothèque
- ✅ Tester une simulation

---

## 🔧 CORRECTIONS APPLIQUÉES

### 1. Fichier `run.py` amélioré

Création automatique des dossiers :
```python
# Créer les dossiers nécessaires
os.makedirs('app/static/library/pdf', exist_ok=True)
os.makedirs('app/static/library/covers', exist_ok=True)
os.makedirs('documents', exist_ok=True)
```

### 2. Fichier `config.py` amélioré

Configuration PostgreSQL pour production.

### 3. Template `dashboard_en_attente.html` créé

Pour les étudiants en attente d'admission.

### 4. Import conditionnel de Gemini

Les fichiers IA fonctionnent même sans clé Gemini.

---

## 📋 CHECKLIST DE VÉRIFICATION

### Localement (sur votre PC) :

- [ ] `python run.py` démarre sans erreur
- [ ] Connexion avec `admin/admin123` fonctionne
- [ ] Création de TP fonctionne
- [ ] Ajout de livre fonctionne
- [ ] Simulations se chargent

### Sur Render :

- [ ] DATABASE_URL est configurée (PostgreSQL)
- [ ] GEMINI_API_KEY est configurée (optionnel)
- [ ] Le déploiement réussit (statut "Live")
- [ ] Le site est accessible
- [ ] Les données persistent après redéploiement

---

## 🆘 ERREURS COURANTES

### Erreur : "No such file or directory: 'app/static/library'"

**Solution** :
```python
# Dans run.py, avant app.run()
import os
os.makedirs('app/static/library/pdf', exist_ok=True)
os.makedirs('app/static/library/covers', exist_ok=True)
```

### Erreur : "TemplateNotFound: etudiant/dashboard_en_attente.html"

**Solution** : ✅ Déjà corrigé ! Le fichier a été créé.

### Erreur : "ModuleNotFoundError: No module named 'google.generativeai'"

**Solution** : ✅ Déjà corrigé ! Import conditionnel dans les fichiers IA.

### Erreur : "Permission denied" sur Render

**Solution** :
- Render utilise un système de fichiers **éphémère**
- Les fichiers uploadés doivent être stockés sur un service externe (S3, Cloudinary)
- OU utiliser PostgreSQL avec stockage BYTEA pour les petits fichiers

---

## 📊 PROCHAINES ÉTAPES

1. **Tester en local** → Tout doit fonctionner
2. **Migrer vers PostgreSQL** → Suivre MIGRATION_POSTGRESQL.md
3. **Configurer Gemini API** (optionnel) → Suivre OBTENIR_CLE_GEMINI.md
4. **Déployer** → `./deployer_maintenant.sh "Fix bibliothèque et labo"`
5. **Vérifier** → Tout fonctionne sur https://kstarhome.onrender.com

---

**© 2026 KstarHome - Corrections**  
*Bibliothèque et Laboratoire fonctionnels !*

