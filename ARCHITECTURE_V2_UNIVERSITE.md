# 🏗️ ARCHITECTURE UNIVERSITAIRE V2 - DOCUMENTATION TECHNIQUE

## Date : 18 Février 2026 - 22:00
## Refonte majeure du système de gestion pédagogique

---

## 🎯 VUE D'ENSEMBLE

Cette V2 transforme l'application en une vraie structure universitaire LMD (Licence-Master-Doctorat) avec une hiérarchie claire et des règles métier précises.

---

## 📊 HIÉRARCHIE (Structure Arborescente)

```
🏢 UNIVERSITÉ
    ├── 🏛️ DÉPARTEMENT (Informatique, Mathématiques, Gestion...)
    │   ├── 👔 Chef de département (Un enseignant)
    │   ├── 🎓 FILIÈRE 1 (Génie Logiciel - Professionnel)
    │   │   ├── 📚 Classes
    │   │   └── 👨‍🎓 Étudiants
    │   ├── 🎓 FILIÈRE 2 (Intelligence Artificielle - Fondamental)
    │   └── 📖 UE du département
    └── ... Autres départements
```

---

## 🗄️ NOUVEAUX MODÈLES

### 1. 🏛️ Département

**Table** : `departements`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | Clé primaire |
| `nom` | String(100) | Ex: "Informatique et Technologies" |
| `code` | String(10) | Ex: "INFO", "MATH", "GESTION" |
| `chef_id` | Foreign Key | Lien vers `enseignants.id` |
| `description` | Text | Description du département |
| `active` | Boolean | Actif ou archivé |
| `date_creation` | DateTime | Date de création |

**Relations :**
- `chef` → Enseignant (One-to-One)
- `filieres` → Filiere (One-to-Many)
- `ues` → UE (One-to-Many)

**Exemple de données :**
```python
dept_info = Departement(
    nom="Informatique et Technologies",
    code="INFO",
    chef_id=5  # M. Anderson
)
```

---

### 2. 🎓 Filière (Refonte)

**Table** : `filieres`

**NOUVEAU champs :**

| Champ | Type | Valeurs | Description |
|-------|------|---------|-------------|
| `departement_id` | Foreign Key | - | Département parent |
| `type_diplome` | String(20) | `'fondamental'` ou `'professionnel'` | Type de formation |

**Types de diplôme :**
- **Fondamental** : Axé recherche, théorie (Master Recherche)
- **Professionnel** : Axé pratique, entreprise (Master Pro, Ingénieur)

**Exemple :**
```python
filiere_gl = Filiere(
    nom_filiere="Génie Logiciel",
    code_filiere="GL",
    departement_id=1,  # Département INFO
    type_diplome="professionnel",
    cycle="Master"
)

filiere_ia = Filiere(
    nom_filiere="Intelligence Artificielle",
    code_filiere="IA",
    departement_id=1,
    type_diplome="fondamental",  # Recherche
    cycle="Master"
)
```

---

### 3. 📖 UE (Refonte Majeure)

**Table** : `ues`

**NOUVEAUX champs critiques :**

| Champ | Type | Valeurs possibles | Description |
|-------|------|-------------------|-------------|
| `categorie` | String(20) | `'fondamentale'`, `'specialite'`, `'transversale'`, `'libre'` | **Catégorie métier** |
| `nature` | String(20) | `'simple'`, `'composite'` | **Structure de l'UE** |
| `departement_id` | Foreign Key | - | Département propriétaire |
| `est_ouverte_a_tous` | Boolean | True/False | Accessible depuis tous les départements ? |
| `type_affectation` | String(20) | `'classe'`, `'tronc_commun'`, `'libre'` | Mode d'assignation |

---

## 🏷️ CATÉGORIES D'UE (Business Logic)

### 🔴 FONDAMENTALE - Le Core

**Analogie** : La fondation d'un bâtiment  
**En code** : Le kernel, la classe mère `AbstractUser`  
**Règle** : OBLIGATOIRE pour tous les étudiants de la filière

**Exemples :**
- Mathématiques pour l'informatique
- Algorithmique
- Architecture des ordinateurs
- Droit constitutionnel pour la gestion

**Caractéristiques :**
- `categorie = 'fondamentale'`
- `est_ouverte_a_tous = False` (Spécifique au département)
- Généralement `type_affectation = 'tronc_commun'`

```python
ue_algo = UE(
    code_ue="INF101",
    intitule="Algorithmique et Structures de Données",
    categorie="fondamentale",
    nature="simple",
    departement_id=1,
    credits=6,
    est_ouverte_a_tous=False
)
```

---

### 🔵 SPÉCIALITÉ - L'Implémentation

**Analogie** : Les pièces spécifiques d'un moteur  
**En code** : `class BackendDeveloper extends Developer`  
**Règle** : Définit l'expertise précise de l'étudiant

**Exemples :**
- Java Avancé (pour Génie Logiciel)
- Routage CISCO (pour Réseaux)
- Machine Learning (pour IA)
- Comptabilité approfondie (pour Finance)

**Caractéristiques :**
- `categorie = 'specialite'`
- `est_ouverte_a_tous = False`
- Liée à une ou plusieurs classes précises

```python
ue_java = UE(
    code_ue="GL301",
    intitule="Java Avancé et Spring Boot",
    categorie="specialite",
    nature="simple",
    departement_id=1,
    credits=5,
    est_ouverte_a_tous=False
)
```

---

### 🟢 TRANSVERSALE - Les Utils Partagées

**Analogie** : Le lubrifiant, les outils communs  
**En code** : Les shared libraries (`import utils`)  
**Règle** : Nécessaire pour intégrer le monde professionnel

**Exemples :**
- Anglais technique
- Communication professionnelle
- Gestion de projet Agile
- Droit de l'informatique
- Entrepreneuriat

**Caractéristiques :**
- `categorie = 'transversale'`
- `est_ouverte_a_tous = True` (Souvent)
- Peut être gérée par un département "Humanités" ou "Transversal"

```python
ue_anglais = UE(
    code_ue="TRV201",
    intitule="Anglais Technique et Communication",
    categorie="transversale",
    nature="simple",
    departement_id=5,  # Département Langues
    credits=3,
    est_ouverte_a_tous=True,
    type_affectation="tronc_commun"
)
```

---

### 🟡 LIBRE - Les Plugins Optionnels

**Analogie** : La customisation, les paillettes  
**En code** : Un plugin VS Code optionnel  
**Règle** : Choix personnel de l'étudiant, n'importe quel domaine

**Exemples :**
- Poterie
- Astronomie
- Sport
- Psychologie
- Cinéma
- Comptabilité (pour un informaticien)

**Caractéristiques CRITIQUES :**
- `categorie = 'libre'`
- `nature = 'simple'` (**TOUJOURS**, jamais composite)
- `est_ouverte_a_tous = True` (**OBLIGATOIRE**)
- L'étudiant peut choisir depuis N'IMPORTE QUEL département

```python
ue_poterie = UE(
    code_ue="ART101",
    intitule="Introduction à la Poterie",
    categorie="libre",
    nature="simple",  # TOUJOURS simple
    departement_id=7,  # Département Arts
    credits=2,
    est_ouverte_a_tous=True,  # TOUJOURS true
    type_affectation="libre"
)
```

**RÈGLE MÉTIER CRITIQUE :**
```python
# Dans le code de validation
if ue.categorie == 'libre' and ue.nature == 'composite':
    raise ValidationError("Une UE libre ne peut pas être composite !")
```

---

## 📦 NATURE D'UE (Structure)

### SIMPLE

UE atomique classique avec une seule évaluation.

```python
ue = UE(nature='simple', ...)
```

### COMPOSITE

UE parent composée de plusieurs sous-UE avec coefficients.

**Exemple :** Physique = Optique (60%) + Mécanique (40%)

```python
ue_physique = UE(
    code_ue="PHY200",
    intitule="Physique Générale",
    categorie="fondamentale",
    nature="composite",
    credits=6
)

# Sous-UE 1
ue_optique = UE(
    code_ue="PHY201",
    intitule="Optique",
    ue_parent_id=ue_physique.id,
    credits=3
)

# Sous-UE 2
ue_mecanique = UE(
    code_ue="PHY202",
    intitule="Mécanique",
    ue_parent_id=ue_physique.id,
    credits=3
)
```

---

## ⚙️ LOGIQUE MÉTIER (Business Logic)

### Récupérer les UE disponibles pour un étudiant

```python
def get_ues_disponibles_pour_etudiant(etudiant):
    """
    Retourne les UE que l'étudiant peut prendre
    """
    ma_classe = etudiant.classe
    ma_filiere = ma_classe.filiere
    mon_dept = ma_filiere.departement
    
    # 1. UE Fondamentales + Spécialités (Obligatoires)
    ues_obligatoires = UE.query.filter(
        UE.departement_id == mon_dept.id,
        UE.categorie.in_(['fondamentale', 'specialite'])
    ).all()
    
    # 2. UE Transversales (Partagées, souvent obligatoires)
    ues_transversales = UE.query.filter_by(
        categorie='transversale'
    ).all()
    
    # 3. UE Libres (Marketplace - TOUS les départements)
    ues_libres_disponibles = UE.query.filter_by(
        categorie='libre',
        est_ouverte_a_tous=True,
        active=True
    ).all()
    
    return {
        'obligatoires': ues_obligatoires + ues_transversales,
        'au_choix_libre': ues_libres_disponibles
    }
```

### Validation lors de la création d'UE

```python
def valider_ue(ue_data):
    """
    Valide les règles métier d'une UE
    """
    categorie = ue_data['categorie']
    nature = ue_data['nature']
    est_ouverte = ue_data.get('est_ouverte_a_tous', False)
    
    # RÈGLE 1: UE libre ne peut pas être composite
    if categorie == 'libre' and nature == 'composite':
        raise ValidationError(
            "❌ Une UE libre doit obligatoirement être SIMPLE"
        )
    
    # RÈGLE 2: UE libre doit être ouverte à tous
    if categorie == 'libre' and not est_ouverte:
        raise ValidationError(
            "❌ Une UE libre doit être accessible à tous (est_ouverte_a_tous=True)"
        )
    
    # RÈGLE 3: UE composite doit avoir des sous-UE
    if nature == 'composite' and not ue_data.get('sous_ues'):
        raise ValidationError(
            "❌ Une UE composite doit avoir au moins 2 sous-UE"
        )
    
    return True
```

---

## 📊 EXEMPLE COMPLET DE STRUCTURE

```
🏢 UNIVERSITÉ POLYTECHNIQUE

📁 DÉPARTEMENT INFORMATIQUE (CODE: INFO)
   👔 Chef: Prof. Anderson
   
   📂 FILIÈRE: Génie Logiciel (PROFESSIONNEL)
      ├── 🔴 INF101: Algorithmique (Fondamentale)
      ├── 🔴 INF102: Mathématiques (Fondamentale)
      ├── 🔵 GL301: Java Avancé (Spécialité)
      ├── 🔵 GL302: Spring Boot (Spécialité)
      └── 🟢 TRV201: Anglais (Transversale)
   
   📂 FILIÈRE: Intelligence Artificielle (FONDAMENTAL - Recherche)
      ├── 🔴 INF101: Algorithmique (Fondamentale)
      ├── 🔴 MAT201: Statistiques (Fondamentale)
      ├── 🔵 IA301: Machine Learning (Spécialité)
      └── 🔵 IA302: Deep Learning (Spécialité)

📁 DÉPARTEMENT ARTS (CODE: ART)
   📂 UE Libres:
      └── 🟡 ART101: Poterie (Libre - Accessible à TOUS)

📁 DÉPARTEMENT LANGUES (CODE: LANG)
   📂 UE Transversales:
      ├── 🟢 ANG201: Anglais Technique (Transversale)
      └── 🟢 COM101: Communication (Transversale)
```

---

## 🚀 MIGRATION

### Étapes pour migrer

1. **Sauvegarder la BDD actuelle**
```bash
pg_dump votre_base > backup_avant_v2.sql
```

2. **Créer la migration**
```bash
flask db migrate -m "Architecture V2: Départements + Catégories UE"
```

3. **Appliquer**
```bash
flask db upgrade
```

4. **Migrer les données existantes**
```python
# Script de migration (à exécuter une fois)
python scripts/migrate_to_v2.py
```

---

## 📝 TODO - IMPLÉMENTATION

- [ ] Créer les formulaires de création de Département
- [ ] Ajouter "Chef de département" dans interface admin
- [ ] Modifier formulaire Filière (ajouter type_diplome)
- [ ] Refondre formulaire UE (catégorie + nature + règles)
- [ ] Créer la logique d'inscription pédagogique
- [ ] Ajouter filtres UE par catégorie dans dashboards
- [ ] Créer rapport "UE libres disponibles"
- [ ] Valider les règles métier côté backend

---

**Version** : 2.0  
**Date** : 18 Février 2026  
**Status** : 🏗️ Modèles créés - En attente migration BDD

