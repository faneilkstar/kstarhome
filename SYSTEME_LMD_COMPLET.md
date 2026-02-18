# 🎓 SYSTÈME LMD COMPLET - GUIDE D'IMPLÉMENTATION

## Date : 18 Février 2026

---

## 📚 ARCHITECTURE GLOBALE

### Hiérarchie Universitaire

```
🏢 Université
├── 🏛️ Département (ex: Informatique, Mathématiques)
│   ├── 🎓 Filière (ex: Génie Logiciel, IA)
│   │   ├── 👥 Classe (ex: GL-L2, IA-L1)
│   │   └── 📚 UE (Unités d'Enseignement)
│   │       ├── 📖 UE Standard (simple)
│   │       └── 📦 UE Composite (avec EC)
│   │           ├── 📄 EC 1 (Élément Constitutif)
│   │           ├── 📄 EC 2
│   │           └── 📄 EC 3
```

---

## 📅 SYSTÈME DES SEMESTRES

### Licence (L1, L2, L3) = 6 Semestres

| Année | Semestres | Crédits ECTS |
|-------|-----------|--------------|
| **L1** | S1 + S2 | 30 + 30 = 60 |
| **L2** | S3 + S4 | 30 + 30 = 60 |
| **L3** | S5 + S6 | 30 + 30 = 60 |

### Master (M1, M2) = 4 Semestres

| Année | Semestres | Crédits ECTS |
|-------|-----------|--------------|
| **M1** | S7 + S8 | 30 + 30 = 60 |
| **M2** | S9 + S10 | 30 + 30 = 60 |

**Total Licence :** 180 ECTS  
**Total Master :** 120 ECTS  
**Total LMD :** 300 ECTS

---

## 🏷️ GÉNÉRATION AUTOMATIQUE DES CODES UE

### Format Standard : `PREFIXE + SEMESTRE + NUMÉRO`

### 1. 🔴 UE FONDAMENTALE

**Préfixe :** Code du département (3-4 lettres)

**Exemples :**
- `INF101` : Algorithmique (Informatique, S1, cours 01)
- `INF102` : Architecture Ordinateurs (Informatique, S1, cours 02)
- `MATH201` : Algèbre Linéaire (Mathématiques, S2, cours 01)
- `GC301` : Mécanique des structures (Génie Civil, S3, cours 01)

### 2. 🔵 UE SPÉCIALITÉ

**Préfixe :** Code de la filière (2-3 lettres)

**Exemples :**
- `GL301` : Java Avancé (Génie Logiciel, S3)
- `GL302` : Frameworks Web (Génie Logiciel, S3)
- `IA401` : Machine Learning (Intelligence Artificielle, S4)
- `RES501` : Sécurité Réseaux (Réseaux, S5)

### 3. 🟢 UE TRANSVERSALE

**Préfixe :** Thématique universelle

**Exemples :**
- `LANG101` : Anglais Technique 1 (S1)
- `LANG201` : Anglais Technique 2 (S2)
- `COM301` : Communication Professionnelle (S3)
- `DRT201` : Droit de l'Informatique (S2)
- `MGT401` : Gestion de Projet (S4)

### 4. 🟡 UE LIBRE

**Préfixe :** `LIB`

**Exemples :**
- `LIB101` : Histoire de l'Art (S1)
- `LIB102` : Football (S1)
- `LIB205` : Astronomie (S2)
- `LIB301` : Entrepreneuriat (S3)

---

## 📦 SYSTÈME DES UE COMPOSITES

### Concept

Une **UE Composite** est une UE "mère" qui contient plusieurs **EC (Éléments Constitutifs)**.

- L'**UE Mère** porte les **crédits ECTS**
- Les **EC** portent les **coefficients** pour le calcul de moyenne
- L'étudiant passe **un examen par EC**
- La note de l'UE Mère = **moyenne pondérée des EC**

### Format de Code pour EC

**Format :** `{ORDRE}{CODE_UE_MERE}`

**Exemple Concret :**

```
📦 UE Mère: NUM201 - Analyse Numérique (4 Crédits ECTS)
├── 📄 EC 1: 1NUM201 - Séries Numériques (Coef 2.0)
└── 📄 EC 2: 2NUM201 - Intégrales (Coef 1.0)
```

**Calcul de la note finale :**
```
Si Étudiant a:
  - 1NUM201 (Séries) : 12/20
  - 2NUM201 (Intégrales) : 16/20

Moyenne NUM201 = (12 × 2.0 + 16 × 1.0) / (2.0 + 1.0)
                = (24 + 16) / 3
                = 40 / 3
                = 13.33/20

L'étudiant valide NUM201 avec 13.33 et gagne 4 Crédits ECTS
```

### Types d'Éléments Constitutifs

| Type | Description | Exemple |
|------|-------------|---------|
| `ec_cours` | Cours théorique | Cours de Thermodynamique |
| `ec_td` | Travaux Dirigés | TD de Maths |
| `ec_tp` | Travaux Pratiques | TP Chimie |
| `ec_matiere` | Matière autonome | Séries Numériques, Intégrales |

---

## 💻 UTILISATION DU SERVICE UEService

### Exemple 1 : Créer une UE Simple

```python
from app.services.ue_service import UEService
from app import db
from app.models import UE

# Générer le code automatiquement
code = UEService.generer_code_ue(
    categorie='fondamentale',
    semestre='S1',
    nom_ue='Algorithmique et Structures de Données',
    departement_code='INF'
)
# Résultat: 'INF101'

# Créer l'UE
ue = UE(
    code_ue=code,
    intitule='Algorithmique et Structures de Données',
    semestre='S1',
    credits=6,
    coefficient=1.0,
    categorie='fondamentale',
    nature='simple',
    type_element='ue_standard',
    departement_id=1
)

db.session.add(ue)
db.session.commit()
```

### Exemple 2 : Créer une UE Composite

```python
from app.services.ue_service import UEService

# Créer une UE composite avec ses EC
ue_mere, elements = UEService.creer_ue_composite(
    nom_ue_mere='Analyse Numérique',
    semestre='S2',
    credits=4,
    categorie='fondamentale',
    departement_id=2,  # Département Maths
    elements_constitutifs_data=[
        {
            'nom': 'Séries Numériques',
            'coefficient': 2.0,
            'type': 'ec_matiere'
        },
        {
            'nom': 'Intégrales',
            'coefficient': 1.0,
            'type': 'ec_matiere'
        }
    ]
)

print(f"UE Mère créée : {ue_mere.code_ue}")
# Output: MATH201

for ec in elements:
    print(f"EC créé : {ec.code_ue} - {ec.intitule} (Coef {ec.coefficient})")
# Output:
# EC créé : 1MATH201 - Séries Numériques (Coef 2.0)
# EC créé : 2MATH201 - Intégrales (Coef 1.0)
```

### Exemple 3 : Calculer la Moyenne d'une UE Composite

```python
from app.services.ue_service import UEService

# Calculer la moyenne de l'étudiant ID=5 pour l'UE composite ID=10
moyenne = UEService.calculer_moyenne_ue_composite(
    ue_mere_id=10,
    etudiant_id=5
)

print(f"Moyenne de l'UE Composite : {moyenne}/20")
# Output: Moyenne de l'UE Composite : 13.33/20
```

---

## 🗄️ STRUCTURE DE LA BASE DE DONNÉES

### Table `ues` (Simplifiée)

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | Integer | Clé primaire |
| `code_ue` | String(20) | Code unique (ex: INF101, 1NUM201) |
| `intitule` | String(200) | Nom complet |
| `semestre` | String(5) | S1, S2, ..., S10 |
| `credits` | Integer | Crédits ECTS (0 pour EC) |
| `coefficient` | Float | Coefficient pour moyenne (0 pour UE mère) |
| `categorie` | String(20) | fondamentale/specialite/transversale/libre |
| `nature` | String(20) | simple/composite |
| `type_element` | String(20) | ue_standard/ue_composite/ec_cours/ec_td/ec_tp/ec_matiere |
| `parent_id` | Integer | ID de l'UE mère (NULL si autonome) |
| `ordre` | Integer | Position dans la hiérarchie |
| `departement_id` | Integer | Département propriétaire |

---

## ✅ RÈGLES MÉTIER (Validations)

### Règle 1 : UE Libre
```python
categorie == 'libre' 
  => nature DOIT être 'simple' (PAS composite)
  => est_ouverte_a_tous DOIT être True
```

### Règle 2 : UE Composite
```python
nature == 'composite'
  => type_element == 'ue_composite'
  => DOIT avoir au moins 1 EC (parent_id pointant vers elle)
  => credits > 0
  => coefficient == 0 (pas utilisé pour la mère)
```

### Règle 3 : Élément Constitutif (EC)
```python
parent_id NOT NULL
  => type_element IN ('ec_cours', 'ec_td', 'ec_tp', 'ec_matiere')
  => credits == 0 (portés par la mère)
  => coefficient > 0
  => semestre == semestre de l'UE mère
```

### Règle 4 : Cohérence des Coefficients
```python
Pour une UE Composite:
  somme(coefficients des EC) > 0
```

---

## 🧮 CALCUL DE LA MOYENNE GÉNÉRALE

### Étape 1 : Notes des EC
L'étudiant passe des examens pour chaque EC :
```
1NUM201 (Séries) : 12/20
2NUM201 (Intégrales) : 16/20
```

### Étape 2 : Moyenne de l'UE Composite
```python
Moyenne NUM201 = (12 × 2.0 + 16 × 1.0) / 3.0 = 13.33/20
```

### Étape 3 : Moyenne du Semestre
```python
Toutes les UE du semestre S2:
  NUM201 : 13.33/20 (4 Crédits)
  INF201 : 15.00/20 (6 Crédits)
  LANG201 : 14.00/20 (2 Crédits)

Moyenne S2 = (13.33×4 + 15.00×6 + 14.00×2) / (4+6+2)
           = (53.32 + 90 + 28) / 12
           = 171.32 / 12
           = 14.28/20
```

### Étape 4 : Validation
```python
if moyenne_semestre >= 10:
    semestre_validé = True
    credits_obtenus = 30  # Pour un semestre complet
```

---

## 🚀 PROCHAINES ÉTAPES

1. ✅ **Migration de la base de données**
   ```bash
   flask db migrate -m "Système LMD: Semestres + UE Composites"
   flask db upgrade
   ```

2. ✅ **Interface Directeur - Créer UE**
   - Formulaire avec choix Semestre (S1-S10)
   - Choix Nature (Simple/Composite)
   - Si Composite : Formulaire dynamique pour ajouter EC

3. ✅ **Calcul automatique des moyennes**
   - Utiliser `UEService.calculer_moyenne_ue_composite()`
   - Générer bulletins par semestre

4. ✅ **Validation des Semestres**
   - Un étudiant valide S1 si moyenne >= 10
   - Compensation possible entre semestres d'une même année

---

## 📊 EXEMPLE COMPLET

### Département Mathématiques crée :

```
📦 NUM201 - Analyse Numérique (S2, 4 Crédits)
├── 1NUM201 - Séries Numériques (Coef 2.0)
└── 2NUM201 - Intégrales (Coef 1.0)

📦 ALG301 - Algèbre Avancée (S3, 6 Crédits)
├── 1ALG301 - Algèbre Linéaire (Coef 1.5)
├── 2ALG301 - TP Algèbre (Coef 0.5)
└── 3ALG301 - Espaces Vectoriels (Coef 2.0)
```

### Étudiant passe les examens :

| Code | Note |
|------|------|
| 1NUM201 | 12/20 |
| 2NUM201 | 16/20 |
| 1ALG301 | 14/20 |
| 2ALG301 | 18/20 |
| 3ALG301 | 11/20 |

### Résultats :

```
NUM201 = (12×2 + 16×1) / 3 = 13.33/20 ✅ Validé (4 Crédits)
ALG301 = (14×1.5 + 18×0.5 + 11×2) / 4 = 13.25/20 ✅ Validé (6 Crédits)

Total Crédits obtenus : 10 ECTS
```

---

**Auteur :** Architecture V2  
**Date :** 18 Février 2026  
**Version :** 2.0 - Système LMD Complet

