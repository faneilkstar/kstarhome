# 🚀 GUIDE RAPIDE - MIGRATION VERS ARCHITECTURE V2

## ⏱️ Temps estimé : 10 minutes

---

## ÉTAPE 1 : Commit des changements (1 min)

```bash
./commit_architecture_v2.sh
```

Ou manuellement :
```bash
git add app/models.py ARCHITECTURE_V2_UNIVERSITE.md
git commit -m "🏗️ Architecture V2: Départements + Catégories UE"
```

---

## ÉTAPE 2 : Créer la migration de base de données (2 min)

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Créer la migration
flask db migrate -m "Architecture V2: Départements + Catégories UE"
```

**Ce que vous verrez :**
```
INFO  [alembic.autogenerate] Detected added table 'departements'
INFO  [alembic.autogenerate] Detected added column 'filieres.departement_id'
INFO  [alembic.autogenerate] Detected added column 'filieres.type_diplome'
INFO  [alembic.autogenerate] Detected added column 'ues.categorie'
INFO  [alembic.autogenerate] Detected added column 'ues.nature'
INFO  [alembic.autogenerate] Detected added column 'ues.departement_id'
INFO  [alembic.autogenerate] Detected added column 'ues.est_ouverte_a_tous'
...
```

---

## ÉTAPE 3 : Appliquer la migration (1 min)

```bash
flask db upgrade
```

**Résultat attendu :**
```
INFO  [alembic.runtime.migration] Running upgrade ... -> xxxxx, Architecture V2: Départements + Catégories UE
```

---

## ÉTAPE 4 : Créer les premières données (5 min)

### Via Python Shell

```bash
python
```

```python
from app import create_app, db
from app.models import Departement, Filiere, UE, Enseignant

app = create_app()
with app.app_context():
    # 1. Créer un département
    dept_info = Departement(
        nom="Informatique et Technologies",
        code="INFO",
        description="Département des sciences informatiques",
        active=True
    )
    db.session.add(dept_info)
    db.session.commit()
    print(f"✅ Département créé : {dept_info.code}")
    
    # 2. Créer une filière
    filiere_gl = Filiere(
        nom_filiere="Génie Logiciel",
        code_filiere="GL",
        departement_id=dept_info.id,
        type_diplome="professionnel",
        cycle="Master"
    )
    db.session.add(filiere_gl)
    db.session.commit()
    print(f"✅ Filière créée : {filiere_gl.nom_filiere}")
    
    # 3. Créer une UE fondamentale
    ue_algo = UE(
        code_ue="INF101",
        intitule="Algorithmique et Structures de Données",
        categorie="fondamentale",
        nature="simple",
        departement_id=dept_info.id,
        credits=6,
        heures=60,
        semestre=1,
        est_ouverte_a_tous=False
    )
    db.session.add(ue_algo)
    db.session.commit()
    print(f"✅ UE créée : {ue_algo.code_ue} ({ue_algo.categorie})")
    
    # 4. Créer une UE libre
    ue_sport = UE(
        code_ue="SPORT101",
        intitule="Sport et Bien-être",
        categorie="libre",
        nature="simple",
        departement_id=None,  # Peut être None pour les UE libres
        credits=2,
        heures=24,
        semestre=1,
        est_ouverte_a_tous=True  # OBLIGATOIRE pour UE libre
    )
    db.session.add(ue_sport)
    db.session.commit()
    print(f"✅ UE libre créée : {ue_sport.code_ue}")
    
    print("\n🎉 Migration réussie !")
```

### Via Interface Admin (À implémenter)

Vous devrez créer les formulaires pour :
- Créer des départements
- Assigner un chef de département
- Créer des filières avec type de diplôme
- Créer des UE avec catégorie

---

## ÉTAPE 5 : Vérifier la structure (1 min)

```python
from app import create_app, db
from app.models import Departement, Filiere, UE

app = create_app()
with app.app_context():
    # Compter les départements
    nb_dept = Departement.query.count()
    print(f"📊 Départements : {nb_dept}")
    
    # Compter les filières par type
    nb_fondamental = Filiere.query.filter_by(type_diplome='fondamental').count()
    nb_professionnel = Filiere.query.filter_by(type_diplome='professionnel').count()
    print(f"📊 Filières fondamentales : {nb_fondamental}")
    print(f"📊 Filières professionnelles : {nb_professionnel}")
    
    # Compter les UE par catégorie
    for cat in ['fondamentale', 'specialite', 'transversale', 'libre']:
        nb = UE.query.filter_by(categorie=cat).count()
        print(f"📊 UE {cat} : {nb}")
```

---

## ⚠️ EN CAS DE PROBLÈME

### Erreur lors de la migration

```bash
# Annuler la dernière migration
flask db downgrade

# Supprimer le fichier de migration
rm migrations/versions/xxxxx_architecture_v2.py

# Recommencer
flask db migrate -m "Architecture V2: Départements + Catégories UE"
flask db upgrade
```

### Conflit avec données existantes

Si vous avez des filières existantes sans `departement_id` :

```python
from app import create_app, db
from app.models import Departement, Filiere

app = create_app()
with app.app_context():
    # Créer un département par défaut
    dept_default = Departement(
        nom="Département Général",
        code="GEN",
        description="Département temporaire pour migration"
    )
    db.session.add(dept_default)
    db.session.commit()
    
    # Assigner toutes les filières orphelines
    filieres_orphelines = Filiere.query.filter_by(departement_id=None).all()
    for f in filieres_orphelines:
        f.departement_id = dept_default.id
        f.type_diplome = 'fondamental'  # Par défaut
    db.session.commit()
    print(f"✅ {len(filieres_orphelines)} filières migrées")
```

---

## 📝 CHECKLIST

- [ ] Modèles créés et testés
- [ ] Migration créée (`flask db migrate`)
- [ ] Migration appliquée (`flask db upgrade`)
- [ ] Au moins 1 département créé
- [ ] Au moins 1 filière avec type_diplome
- [ ] Au moins 1 UE de chaque catégorie créée
- [ ] Chef de département assigné (optionnel)

---

## 🎯 APRÈS LA MIGRATION

**Prochaines tâches :**

1. Créer les formulaires de création :
   - `templates/directeur/creer_departement.html`
   - Modifier `templates/directeur/creer_filiere.html`
   - Modifier `templates/directeur/creer_ue.html`

2. Créer les routes :
   - `POST /directeur/departements/nouveau`
   - `POST /directeur/departements/<id>/chef`

3. Adapter les dashboards :
   - Afficher les départements
   - Filtrer les UE par catégorie
   - Afficher les UE libres disponibles

4. Implémenter la logique d'inscription pédagogique :
   - Fonction `get_ues_disponibles_pour_etudiant()`
   - Validation des choix d'UE libres

---

**Date** : 18 Février 2026  
**Version** : 2.0  
**Status** : Guide de migration prêt

