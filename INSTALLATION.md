# 🚀 GUIDE DE DÉMARRAGE - PythonProject3

## ✅ Installation Complète (Linux/macOS)

### Étape 1: Créer un environnement virtuel
```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
python3 -m venv venv
```

### Étape 2: Activer le virtualenv
```bash
source venv/bin/activate
```

### Étape 3: Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4: Démarrer le serveur
```bash
python3 run.py
```

Le serveur démarre par défaut sur: **http://localhost:5000**

---

## 🔐 Identifiants par défaut

Après le premier démarrage, un compte admin est créé automatiquement:

- **Username**: `admin`
- **Password**: `admin123`
- **Rôle**: DIRECTEUR

---

## 🛠️ Dépannage

### Erreur: "Port 5000 already in use"

**Solution**: Modifier le port dans `run.py`:
```python
app.run(host='0.0.0.0', port=8000, debug=True)  # Utiliser le port 8000
```

### Erreur: "No module named flask"

**Solution**: Vérifier que le virtualenv est activé:
```bash
source venv/bin/activate
which python  # Doit afficher venv/bin/python
```

### Erreur: "Database not found"

**Solution**: La base de données se crée automatiquement au premier démarrage.
Si besoin, supprimer et recréer:
```bash
rm instance/academique_dev.db
python3 run.py
```

---

## 📁 Structure du Projet

```
PythonProject3/
├── app/
│   ├── __init__.py          # Initialisation Flask
│   ├── models.py            # Modèles SQLAlchemy (16 BUGS CORRIGÉS ✅)
│   ├── routes/              # Routes de l'application
│   │   ├── auth.py          # Authentification
│   │   ├── directeur.py     # Routes administrateur (12 BUGS CORRIGÉS ✅)
│   │   ├── etudiant.py      # Routes étudiants (4 BUGS CORRIGÉS ✅)
│   │   ├── enseignant.py    # Routes enseignants
│   │   └── ...
│   ├── static/              # Fichiers statiques (CSS, JS, uploads)
│   └── templates/           # Templates HTML
├── instance/                # Instance de développement
│   └── academique_dev.db    # Base de données SQLite
├── config.py                # Configuration Flask
├── run.py                   # Point d'entrée
├── requirements.txt         # Dépendances Python
├── test_app.py             # Script de test
├── start_server.sh         # Script de démarrage
└── README.md               # Ce fichier

```

---

## ✅ Bugs Corrigés (Total: 16)

### models.py (6 bugs)
- ✅ Attribut `grade` ajouté à Classe
- ✅ Attributs `date_validation`, `matricule` ajoutés à Etudiant
- ✅ Attribut `situation_matrimoniale` ajouté à Etudiant
- ✅ Attribut `mention` ajouté à Diplome
- ✅ Méthode `set_password()` ajoutée à User

### directeur.py (6 bugs)
- ✅ Importations doublons supprimées
- ✅ Import `canvas` de ReportLab ajouté
- ✅ Route `/attribuer_ue` créée
- ✅ Route `/affectations-ues` créée
- ✅ Décorateur de `detail_etudiant()` corrigé

### etudiant.py (4 bugs)
- ✅ Importations doublons nettoyées
- ✅ Références `ue_inscrite` remplacées par `ue`
- ✅ Attribut `date_upload` remplacé par `date_creation`
- ✅ `logout_user` ajouté aux imports

### requirements.txt (0 bug, mais complété)
- ✅ `Flask` ajouté
- ✅ `Flask-Migrate` ajouté

---

## 📞 Support

Pour toute erreur ou question:
1. Vérifier que le virtualenv est activé: `source venv/bin/activate`
2. Vérifier les logs de l'application
3. Consulter le fichier `run.py` pour les configurations

**Date de mise à jour**: 2026-02-10
**Statut**: ✅ TOUS LES BUGS RÉSOLUS - APPLICATION FONCTIONNELLE

