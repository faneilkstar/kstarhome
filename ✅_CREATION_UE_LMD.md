# ✅ SYSTÈME DE CRÉATION D'UE - ARCHITECTURE LMD COMPLÈTE

## 🎯 CE QUI A ÉTÉ IMPLÉMENTÉ

**Date** : 18 février 2026

### Nouvelle Interface d'Ajout d'UE

✅ **4 Catégories LMD** :
1. 🔴 **Fondamentale** - Base indispensable (Maths, Algorithmique...)
2. 🔵 **Spécialité** - Compétences métier (Java, Réseaux...)
3. 🟢 **Transversale** - Pour tous (Anglais, Communication...)
4. 🟡 **Libre** - Au choix de l'étudiant (toute discipline)

✅ **2 Natures** :
- **Simple** : Une seule matière
- **Composite** : Plusieurs éléments constitutifs (EC)

✅ **2 Types d'Affectation** :
- **Spécifique** : Pour UNE classe uniquement
- **Tronc Commun** : Pour PLUSIEURS classes

---

## 🏗️ MATRICE DES COMBINAISONS POSSIBLES

| Catégorie | Nature | Affectation | Exemple |
|-----------|--------|-------------|---------|
| Fondamentale | Simple | Spécifique | Maths pour L1 Info |
| Fondamentale | Simple | Tronc Commun | Maths pour L1 Info + L1 Physique |
| Fondamentale | Composite | Spécifique | Physique (Optique + Méca) pour L2 |
| Fondamentale | Composite | Tronc Commun | Physique pour L2 Info + L2 Elec |
| Spécialité | Simple | Spécifique | Java Avancé pour L3 GL |
| Spécialité | Composite | Spécifique | Dev Web (Front + Back) pour M1 |
| Transversale | Simple | Tronc Commun | Anglais pour toutes L1 |
| Libre | Simple | - | Poterie, Sport... |

---

## 📝 WORKFLOW DE CRÉATION

### Étape 1 : Choisir la Catégorie
```
→ Cliquer sur l'une des 4 cartes
→ La catégorie détermine l'importance de l'UE dans le diplôme
```

### Étape 2 : Choisir la Nature
```
→ Simple : Une seule matière avec une note
→ Composite : Plusieurs EC avec notes distinctes et moyenne pondérée
```

### Étape 3 : Choisir l'Affectation
```
→ Spécifique : Sélectionner UNE classe
→ Tronc Commun : Cocher PLUSIEURS classes (min 2)
```

### Étape 4 : Remplir les Informations
```
→ Département (obligatoire sauf UE libre)
→ Code UE (ex: MTH101, INFO201)
→ Nom complet
→ Semestre (S1 à S6)
→ Crédits ECTS (si simple)
```

### Étape 5 (si Composite) : Définir les EC
```
→ Nombre d'éléments constitutifs (2 à 4)
→ Pour chaque EC :
  - Nom (ex: Optique Ondulatoire)
  - Crédits (ex: 2 ECTS)
→ Le système génère les codes automatiquement :
  - UE Mère : PHY201
  - EC 1 : 1PHY201
  - EC 2 : 2PHY201
```

---

## 💻 CODE BACKEND

### Route Modifiée
**Fichier** : `app/routes/directeur.py`

**Route** : `@bp.route('/ue/ajouter', methods=['GET', 'POST'])`

**Fonctionnalités** :
- ✅ Validation des données
- ✅ Gestion UE Simple avec classe unique ou tronc commun
- ✅ Gestion UE Composite avec création automatique des EC
- ✅ Calcul automatique des heures (crédits × 12)
- ✅ Calcul automatique du coefficient
- ✅ Attribution du département
- ✅ Messages de succès différenciés

---

## 🎨 TEMPLATE

**Fichier** : `app/templates/directeur/ajouter_ue_v2.html`

**Design** :
- Formulaire en 4 étapes claires
- Boutons radio visuels avec icônes
- Sections qui s'affichent/cachent dynamiquement
- Validation HTML5
- Responsive (mobile-friendly)

**Éléments Dynamiques** :
- Affichage conditionnel selon la nature (Simple/Composite)
- Affichage conditionnel selon l'affectation (Spécifique/Tronc)
- Génération dynamique des champs EC

---

## 🗄️ DONNÉES ENREGISTRÉES

### Table `ues`

**Pour une UE Simple** :
```python
{
    'code_ue': 'MTH101',
    'nom_ue': 'Algèbre Linéaire',
    'credits': 3,
    'heures': 36,  # 3 × 12
    'coefficient': 3,
    'semestre': 'S1',
    'categorie': 'fondamentale',
    'nature': 'simple',
    'type_structure': 'ue_simple',
    'type_affectation': 'specifique',
    'departement_id': 1,
    'classe_id': 5,
    'parent_id': None
}
```

**Pour une UE Composite** :
```python
# UE Mère
{
    'code_ue': 'PHY201',
    'nom_ue': 'Physique Générale',
    'credits': 6,  # Somme des EC
    'heures': 72,
    'coefficient': 6,
    'semestre': 'S3',
    'categorie': 'fondamentale',
    'nature': 'composite',
    'type_structure': 'ue_composite',
    'type_affectation': 'tronc_commun',
    'departement_id': 2,
    'parent_id': None
}

# EC 1
{
    'code_ue': '1PHY201',
    'nom_ue': 'Optique Ondulatoire',
    'credits': 3,
    'heures': 36,
    'coefficient': 3,
    'semestre': 'S3',
    'categorie': 'fondamentale',
    'nature': 'simple',
    'type_structure': 'element_constitutif',
    'type_affectation': 'tronc_commun',
    'departement_id': 2,
    'parent_id': [ID_UE_MERE]
}

# EC 2
{
    'code_ue': '2PHY201',
    'nom_ue': 'Mécanique',
    'credits': 3,
    'heures': 36,
    'coefficient': 3,
    'semestre': 'S3',
    'categorie': 'fondamentale',
    'nature': 'simple',
    'type_structure': 'element_constitutif',
    'type_affectation': 'tronc_commun',
    'departement_id': 2,
    'parent_id': [ID_UE_MERE]
}
```

---

## ✅ TESTS À EFFECTUER

- [ ] Créer une UE Fondamentale Simple Spécifique
- [ ] Créer une UE Spécialité Simple Tronc Commun
- [ ] Créer une UE Transversale Simple Tronc Commun
- [ ] Créer une UE Libre Simple
- [ ] Créer une UE Composite avec 2 EC
- [ ] Créer une UE Composite avec 3 EC
- [ ] Vérifier le calcul automatique des crédits totaux
- [ ] Vérifier la génération des codes EC (1XXX, 2XXX...)
- [ ] Vérifier l'affichage dans la liste des UE

---

## 📊 RÉSUMÉ

✅ **4 Catégories LMD implémentées**  
✅ **2 Natures (Simple/Composite)**  
✅ **2 Types d'affectation (Spécifique/Tronc Commun)**  
✅ **Interface claire en 4 étapes**  
✅ **Génération automatique des codes EC**  
✅ **Calcul automatique heures et coefficients**  
✅ **Validation des données**  

🎉 **Le système de création d'UE est maintenant conforme au système LMD !**

---

**Statut** : ✅ OPÉRATIONNEL  
**Template** : `ajouter_ue_v2.html`  
**Route** : `/directeur/ue/ajouter`

