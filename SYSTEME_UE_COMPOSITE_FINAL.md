# ✅ SYSTÈME FINAL - UE COMPOSITE AVEC SOUS-UE

## 🎯 FONCTIONNEMENT UE COMPOSITE

### Structure Parent-Enfants

```
UE PARENT (GEC1220)
├── Nom : "Algèbre et Pratique"
├── Crédits : 5 ECTS (somme des enfants)
├── Heures : 60h (auto)
├── Coefficient : 5 (auto)
└── Semestre : 1

    ├─ SOUS-UE 1 (1GEC1220)
    │  ├── Nom : "Algèbre Linéaire"
    │  ├── Crédits : 3 ECTS
    │  ├── Prof : KOFFI (peut être différent)
    │  └── Semestre : 1
    │
    ├─ SOUS-UE 2 (2GEC1220)
    │  ├── Nom : "TP Algèbre"
    │  ├── Crédits : 2 ECTS
    │  ├── Prof : MARTIN (peut être différent)
    │  └── Semestre : 1
    │
    └─ SOUS-UE 3 (3GEC1220) [Optionnel]
       ├── Nom : "Projet"
       ├── Crédits : 1 ECTS
       └── Prof : DUPONT (peut être différent)
```

---

## 📊 EXEMPLES CONCRETS

### Exemple 1 : UE Composite Spécifique

```
Mode : UE Spécifique
Type : Composite
Code : GEC1220
Nom Parent : Algèbre et Pratique
Semestre : 1
Classe : L1 Génie Civil

Sous-UE :
1. 1GEC1220 "Algèbre Linéaire" (3 ECTS)
2. 2GEC1220 "TP Algèbre" (2 ECTS)

Résultat créé :
- GEC1220 (Parent, 5 ECTS)
- 1GEC1220 (Sous-UE, 3 ECTS) → Affectable à Prof. KOFFI
- 2GEC1220 (Sous-UE, 2 ECTS) → Affectable à Prof. MARTIN
```

### Exemple 2 : UE Composite Tronc Commun

```
Mode : Tronc Commun
Type : Composite
Code : PHY100
Nom Parent : Physique Générale
Semestre : 2
Classes : L1 Info, L1 Génie, L1 Réseau

Sous-UE :
1. 1PHY100 "Optique" (3 ECTS)
2. 2PHY100 "Mécanique" (3 ECTS)

Résultat créé :
- PHY100 (Parent Tronc Commun L1, 6 ECTS)
- 1PHY100 (Optique, 3 ECTS) → Affectable à Prof. BERNARD
- 2PHY100 (Mécanique, 3 ECTS) → Affectable à Prof. CLAUDE

Note : Les 2 sous-UE sont aussi en Tronc Commun L1
```

### Exemple 3 : UE Composite UE Filles

```
Mode : UE Filles
Type : Composite
Code : MTH100
Nom Parent : Mathématiques I
Semestre : 1
Classes : L1 Info, L1 Génie

Sous-UE :
1. 1MTH100 "Analyse" (4 ECTS)
2. 2MTH100 "Algèbre" (3 ECTS)

Résultat créé (pour L1 Info) :
- MTH100-L1INFO (Parent, 7 ECTS)
- 1MTH100-L1INFO (Analyse, 4 ECTS) → Prof. KOFFI
- 2MTH100-L1INFO (Algèbre, 3 ECTS) → Prof. MARTIN

Résultat créé (pour L1 Génie) :
- MTH100-L1GENIE (Parent, 7 ECTS)
- 1MTH100-L1GENIE (Analyse, 4 ECTS) → Prof. DUPONT
- 2MTH100-L1GENIE (Algèbre, 3 ECTS) → Prof. BERNARD
```

---

## 🎨 INTERFACE FORMULAIRE

### Section Composite (Apparaît si Type = Composite)

```
┌─────────────────────────────────────────────┐
│ 📦 CONFIGURATION UE COMPOSITE               │
├─────────────────────────────────────────────┤
│                                             │
│ SOUS-UE 1 (Préfixe: 1)                     │
│ Intitulé : [Algèbre Linéaire____________]  │
│ Crédits  : [3▼]                            │
│                                             │
│ SOUS-UE 2 (Préfixe: 2)                     │
│ Intitulé : [TP Algèbre__________________]  │
│ Crédits  : [2▼]                            │
│                                             │
│ SOUS-UE 3 (Préfixe: 3) [Optionnelle]       │
│ Intitulé : [Projet______________________]  │
│ Crédits  : [0▼]                            │
│                                             │
│ Total Crédits Parent : 5 ECTS              │
└─────────────────────────────────────────────┘
```

**Calcul automatique** : Le total se met à jour en temps réel

---

## 💡 AFFECTATION DES PROFS

### Cas UE Composite

Les **sous-UE sont affectables indépendamment** :

```
Page Affectations → Prof. KOFFI
Liste des UE disponibles :
☐ 1GEC1220 "Algèbre Linéaire" (3 ECTS)
☐ 2GEC1220 "TP Algèbre" (2 ECTS)

→ KOFFI peut prendre juste 1GEC1220

Page Affectations → Prof. MARTIN
Liste des UE disponibles :
☐ 2GEC1220 "TP Algèbre" (2 ECTS)

→ MARTIN peut prendre juste 2GEC1220
```

**Important** : L'UE parent (GEC1220) n'est **PAS affectable** directement, seules les sous-UE le sont.

---

## 🔄 WORKFLOW COMPLET

### Créer UE Composite Spécifique

```
1. Clic "DÉFINIR LA NATURE DE L'UE"

2. Choisir [📘 UE Spécifique]

3. Choisir [📦 Composite]
   → Section Composite apparaît

4. Remplir :
   Code : GEC1220
   Nom : Algèbre et Pratique
   Semestre : 1
   Classe : L1 Génie Civil
   
5. Sous-UE 1 :
   Intitulé : Algèbre Linéaire
   Crédits : 3
   
6. Sous-UE 2 :
   Intitulé : TP Algèbre
   Crédits : 2
   
7. Total auto : 5 ECTS

8. Valider

Résultat :
✅ 1 UE parent créée : GEC1220 (5 ECTS)
✅ 2 sous-UE créées :
   - 1GEC1220 (3 ECTS)
   - 2GEC1220 (2 ECTS)

9. Affectations :
   - 1GEC1220 → Prof. KOFFI
   - 2GEC1220 → Prof. MARTIN
```

---

## 📊 BASE DE DONNÉES

### Table `ues`

```sql
-- UE Parent
id: 1
code_ue: 'GEC1220'
intitule: 'Algèbre et Pratique'
credits: 5  -- Somme
heures: 60  -- Auto (5 * 12)
coefficient: 5  -- Auto
semestre: 1
type_ue_creation: 'composite'
ue_parent_id: NULL  -- C'est le parent

-- Sous-UE 1
id: 2
code_ue: '1GEC1220'
intitule: 'Algèbre Linéaire'
credits: 3
heures: 36
coefficient: 3
semestre: 1
type_ue_creation: 'simple'
ue_parent_id: 1  -- Référence au parent

-- Sous-UE 2
id: 3
code_ue: '2GEC1220'
intitule: 'TP Algèbre'
credits: 2
heures: 24
coefficient: 2
semestre: 1
type_ue_creation: 'simple'
ue_parent_id: 1  -- Référence au parent
```

### Table `enseignant_ue`

```sql
-- Prof KOFFI enseigne Sous-UE 1
enseignant_id: 10
ue_id: 2  -- 1GEC1220

-- Prof MARTIN enseigne Sous-UE 2
enseignant_id: 11
ue_id: 3  -- 2GEC1220
```

---

## ✅ RÈGLES

1. **Code automatique** : Préfixe 1, 2, 3 devant le code parent
2. **Crédits parent** : Somme automatique des sous-UE
3. **Semestre** : Identique parent et enfants
4. **Classe** : Identique parent et enfants
5. **Affectation** : Les sous-UE sont affectables indépendamment
6. **Profs différents** : ✅ Autorisé et encouragé

---

## 🎯 NOUVEAUTÉS AJOUTÉES

| Fonctionnalité | Status |
|----------------|--------|
| Champ Semestre | ✅ |
| UE Composite parent-enfants | ✅ |
| Code préfixé (1GEC1220) | ✅ |
| Calcul auto crédits parent | ✅ |
| Affichage section si Composite | ✅ |
| 3 sous-UE possibles | ✅ |
| Profs différents par sous-UE | ✅ |

---

**Version** : 7.0.0 - UE Composite Complète  
**Status** : ✅ OPÉRATIONNEL

🎉 **SYSTÈME COMPLET : 3 MODES + COMPOSITE + SEMESTRE + PROFS DIFFÉRENTS !**

