# 📚 EXEMPLE CONCRET : UE COMPOSITE "OPTIQUE & PHYSIQUE MODERNE"

## Date : 18 Février 2026

---

## 🎯 OBJECTIF

Illustrer la différence entre :
- **UE Simple** : Une seule matière (ex: Anglais)
- **UE Composite** : Regroupement de matières (ex: Optique & Physique)
- **Élément Constitutif (EC)** : Sous-matière (ex: Optique Ondulatoire)

---

## 📦 STRUCTURE DE L'UE COMPOSITE

### UE Mère : PHYS201 - "Optique & Physique Moderne"

**Caractéristiques :**
- **Code** : PHYS201
- **Semestre** : S2
- **Crédits ECTS** : 6
- **Catégorie** : Fondamentale
- **Type Structure** : `ue_composite`
- **Coefficient** : 0 (ne sert pas, la mère ne porte que les crédits)

**Contenu (3 matières distinctes) :**

```
📦 PHYS201 - Optique & Physique Moderne (6 Crédits ECTS)
├── 📄 1PHYS201 - Optique Ondulatoire (Coef 2.0)
├── 📄 2PHYS201 - Optique Géométrique (Coef 2.0)
└── 📄 3PHYS201 - Physique Quantique (Coef 1.0)
```

---

## 📋 DÉTAIL DES ÉLÉMENTS CONSTITUTIFS (EC)

### EC 1 : Optique Ondulatoire (1PHYS201)

| Propriété | Valeur |
|-----------|--------|
| **Code** | 1PHYS201 |
| **Nom** | Optique Ondulatoire |
| **Type Structure** | `element_constitutif` |
| **Coefficient** | 2.0 |
| **Crédits** | 0 (portés par la mère) |
| **Parent** | PHYS201 |
| **Ordre** | 1 |

**Contenu du cours :**
- Ondes électromagnétiques
- Interférences
- Diffraction

---

### EC 2 : Optique Géométrique (2PHYS201)

| Propriété | Valeur |
|-----------|--------|
| **Code** | 2PHYS201 |
| **Nom** | Optique Géométrique |
| **Type Structure** | `element_constitutif` |
| **Coefficient** | 2.0 |
| **Crédits** | 0 |
| **Parent** | PHYS201 |
| **Ordre** | 2 |

**Contenu du cours :**
- Lois de réflexion et réfraction
- Lentilles minces
- Systèmes optiques

---

### EC 3 : Physique Quantique (3PHYS201)

| Propriété | Valeur |
|-----------|--------|
| **Code** | 3PHYS201 |
| **Nom** | Physique Quantique |
| **Type Structure** | `element_constitutif` |
| **Coefficient** | 1.0 |
| **Crédits** | 0 |
| **Parent** | PHYS201 |
| **Ordre** | 3 |

**Contenu du cours :**
- Dualité onde-corpuscule
- Équation de Schrödinger
- Quantification de l'énergie

---

## 🧮 CALCUL DE LA MOYENNE

### Scénario : Notes de l'Étudiant "Marie DUPONT"

Marie passe **3 examens distincts** (un par EC) :

| EC | Matière | Note | Coefficient |
|----|---------|------|-------------|
| 1PHYS201 | Optique Ondulatoire | 12/20 | 2.0 |
| 2PHYS201 | Optique Géométrique | 14/20 | 2.0 |
| 3PHYS201 | Physique Quantique | 10/20 | 1.0 |

### Formule de Calcul

```
Moyenne PHYS201 = (Note1 × Coef1 + Note2 × Coef2 + Note3 × Coef3) / (Coef1 + Coef2 + Coef3)
```

### Application Numérique

```
Moyenne PHYS201 = (12×2 + 14×2 + 10×1) / (2+2+1)
                = (24 + 28 + 10) / 5
                = 62 / 5
                = 12.4/20
```

### Résultat Final

**Marie obtient 12.4/20 pour l'UE PHYS201**

✅ **Validation** : 12.4 ≥ 10 → Marie valide l'UE et gagne **6 Crédits ECTS**

---

## 💻 CODE PYTHON POUR CRÉER CETTE UE

### Utilisation du Service UEService

```python
from app.services.ue_service import UEService
from app import db

# Créer l'UE Composite avec ses 3 EC
ue_mere, elements = UEService.creer_ue_composite(
    nom_ue_mere='Optique & Physique Moderne',
    semestre='S2',
    credits=6,
    categorie='fondamentale',
    departement_id=2,  # ID du département Physique
    elements_constitutifs_data=[
        {
            'nom': 'Optique Ondulatoire',
            'coefficient': 2.0
        },
        {
            'nom': 'Optique Géométrique',
            'coefficient': 2.0
        },
        {
            'nom': 'Physique Quantique',
            'coefficient': 1.0
        }
    ]
)

print(f"✅ UE Mère créée : {ue_mere.code_ue} - {ue_mere.intitule}")
print(f"   Type Structure : {ue_mere.type_structure}")
print(f"   Crédits : {ue_mere.credits} ECTS")
print(f"   Nombre EC : {len(elements)}")
print("")

for ec in elements:
    print(f"   📄 EC : {ec.code_ue} - {ec.intitule}")
    print(f"      Coefficient : {ec.coefficient}")
    print(f"      Type Structure : {ec.type_structure}")
    print("")
```

**Output Attendu :**

```
✅ UE Mère créée : PHYS201 - Optique & Physique Moderne
   Type Structure : ue_composite
   Crédits : 6 ECTS
   Nombre EC : 3

   📄 EC : 1PHYS201 - Optique Ondulatoire
      Coefficient : 2.0
      Type Structure : element_constitutif

   📄 EC : 2PHYS201 - Optique Géométrique
      Coefficient : 2.0
      Type Structure : element_constitutif

   📄 EC : 3PHYS201 - Physique Quantique
      Coefficient : 1.0
      Type Structure : element_constitutif
```

---

## 🧪 CALCULER LA MOYENNE D'UN ÉTUDIANT

### Code Python

```python
from app.services.ue_service import UEService

# Calculer la moyenne de Marie (ID=5) pour PHYS201 (ID=10)
moyenne = UEService.calculer_moyenne_ue(
    ue_id=10,
    etudiant_id=5
)

print(f"Moyenne de Marie pour PHYS201 : {moyenne}/20")

# Vérifier si validé
if moyenne and moyenne >= 10:
    ue = UE.query.get(10)
    print(f"✅ UE Validée ! Marie gagne {ue.credits} Crédits ECTS")
else:
    print("❌ UE Non Validée")
```

**Output :**

```
Moyenne de Marie pour PHYS201 : 12.4/20
✅ UE Validée ! Marie gagne 6 Crédits ECTS
```

---

## 📊 COMPARAISON : UE SIMPLE vs UE COMPOSITE

### UE Simple (ex: Anglais)

```
📖 LANG101 - Anglais Technique (3 Crédits ECTS)
   Type Structure : ue_simple
   
   Étudiant passe 1 examen → Note : 15/20
   Moyenne LANG101 = 15/20 (note directe)
```

### UE Composite (ex: Optique)

```
📦 PHYS201 - Optique & Physique Moderne (6 Crédits ECTS)
   Type Structure : ue_composite
   
   ├── 1PHYS201 - Optique Ondulatoire (Coef 2.0) → Note : 12/20
   ├── 2PHYS201 - Optique Géométrique (Coef 2.0) → Note : 14/20
   └── 3PHYS201 - Physique Quantique (Coef 1.0) → Note : 10/20
   
   Étudiant passe 3 examens distincts
   Moyenne PHYS201 = (12×2 + 14×2 + 10×1) / 5 = 12.4/20 (calculée)
```

---

## 🎯 RÈGLES MÉTIER

### Règle 1 : Validation par type_structure

```python
ue.est_validable()
# → True si type_structure in ['ue_simple', 'ue_composite']
# → False si type_structure == 'element_constitutif'
```

**Explications :**
- **UE Simple** : Validable → Donne des crédits ECTS
- **UE Composite** : Validable → Donne des crédits ECTS
- **EC** : NON validable → Donne une note pour la moyenne de l'UE mère

### Règle 2 : Note directe possible ?

```python
ue.peut_avoir_note_directe()
# → True si type_structure in ['ue_simple', 'element_constitutif']
# → False si type_structure == 'ue_composite'
```

**Explications :**
- **UE Simple** : L'étudiant a UNE note directe
- **EC** : L'étudiant a UNE note directe (pour calculer la moyenne de la mère)
- **UE Composite** : L'étudiant n'a PAS de note directe (calculée automatiquement)

### Règle 3 : Hiérarchie

```python
# UE Simple
parent_id == NULL

# UE Composite
parent_id == NULL
elements_constitutifs.count() > 0

# EC
parent_id != NULL  # Pointe vers l'UE mère
```

---

## ✅ RÉCAPITULATIF

| Type | Code Exemple | Crédits | Coefficient | Parent | Note |
|------|--------------|---------|-------------|--------|------|
| **UE Simple** | LANG101 | 3 | 0 | NULL | Directe |
| **UE Composite** | PHYS201 | 6 | 0 | NULL | Calculée |
| **EC** | 1PHYS201 | 0 | 2.0 | PHYS201 | Directe |
| **EC** | 2PHYS201 | 0 | 2.0 | PHYS201 | Directe |
| **EC** | 3PHYS201 | 0 | 1.0 | PHYS201 | Directe |

---

**Date :** 18 Février 2026  
**Version :** 2.2 - Exemple UE Composite Optique  
**Status :** ✅ Documentation complète

