# 🎯 SYSTÈME FINAL - 2 MODES DE CRÉATION D'UE

## 📋 PHILOSOPHIE

**"Un Prof, Une UE, Plusieurs Classes" OU "Plusieurs Profs, Plusieurs UE"**

---

## 🔄 LES 2 MODES DISTINCTS

### MODE 1 : TRONC COMMUN 🌳
```
1 UE UNIQUE → Plusieurs Classes → 1 SEUL Prof
```

**Caractéristiques** :
- ✅ **1 UE créée** pour toutes les classes
- ✅ **Code préservé** (ex: ANG100)
- ✅ **1 seul prof** enseigne à toutes les classes
- ✅ **Économie** : 1 prof au lieu de 3
- ✅ **Cohérence** : Même contenu pour tous

**Exemple** :
```
Créer : ANG100 - Anglais Technique
Mode : [◉ Tronc Commun]
Classes : L1 Info, L1 Génie, L1 Réseau

Résultat : 1 SEULE UE
- ANG100 (partagée entre 3 classes)

Affectation :
- Prof. MARTIN → ANG100
- Prof. MARTIN enseigne aux 3 classes en même temps
```

**Usage idéal** :
- Langues (Anglais, Français)
- Sport
- Éthique et déontologie
- Culture générale
- Droit

---

### MODE 2 : UE FILLES 📚
```
N UE DISTINCTES → 1 UE par Classe → N Profs possibles
```

**Caractéristiques** :
- ✅ **N UE créées** (1 par classe)
- ✅ **Code muté** (MTH100-L1INFO, MTH100-L1GENIE)
- ✅ **Profs différents** possibles
- ✅ **Flexibilité** : Contenu adapté par classe
- ✅ **Indépendance** : Chaque UE autonome

**Exemple** :
```
Créer : MTH100 - Mathématiques I
Mode : [◉ UE Filles]
Classes : L1 Info, L1 Génie

Résultat : 2 UE DISTINCTES
- MTH100-L1INFO (L1 Info)
- MTH100-L1GENIE (L1 Génie)

Affectation :
- Prof. KOFFI → MTH100-L1INFO
- Prof. DUPONT → MTH100-L1GENIE
- Chaque prof enseigne à SA classe
```

**Usage idéal** :
- Mathématiques (niveau différent)
- Programmation (langages différents)
- Cours spécialisés
- Projets spécifiques

---

## 🎨 INTERFACE DE CRÉATION

### Écran Principal

```
┌─────────────────────────────────────────────────────┐
│ MODE DE CRÉATION                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [🌳 TRONC COMMUN]    [📚 UE FILLES]              │
│   1 UE → N Classes     1 UE par Classe            │
│   Code: ANG100         Code: MTH100-L1INFO        │
│   1 seul prof          N profs possibles          │
│                                                     │
├─────────────────────────────────────────────────────┤
│ TYPE D'ÉVALUATION                                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [📄 SIMPLE]          [📦 COMPOSITE]              │
│   1 note unique        Note = Sous-UE pondérées   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔢 TYPE D'ÉVALUATION (2ème Choix)

### ÉVALUATION SIMPLE
- **1 note unique** pour l'UE
- Exemple : Examen final
- Plus simple à gérer

### ÉVALUATION COMPOSITE
- **Note calculée** à partir de sous-UE
- Exemple : Optique (60%) + Mécanique (40%)
- Pour projets multi-phases

**Note** : Le type d'évaluation est **indépendant** du mode de création !

---

## 📊 TABLEAU COMPARATIF

| Critère | Tronc Commun | UE Filles |
|---------|--------------|-----------|
| **Nombre d'UE** | 1 (partagée) | N (1 par classe) |
| **Code UE** | Préservé (ANG100) | Muté (MTH100-L1INFO) |
| **Enseignants** | 1 seul prof | N profs possibles |
| **Classes** | Plusieurs | 1 classe/UE |
| **Contenu** | Identique pour tous | Adapté par classe |
| **Économie** | ✅ Oui | ❌ Non |
| **Flexibilité** | ❌ Non | ✅ Oui |

---

## 🎯 CAS D'USAGE RÉELS

### Cas 1 : École avec Anglais Commun

**Problème** : Anglais identique pour toutes les L1

**Solution** : **TRONC COMMUN**
```
Créer : ANG100
Mode : [◉ Tronc Commun]
Classes : L1 Info, L1 Génie, L1 Réseau, L1 Civil

Résultat :
- 1 UE : ANG100
- Affecter à Prof. DUPONT
- Prof. DUPONT enseigne aux 4 classes

Économie : 3 enseignants économisés !
```

### Cas 2 : Mathématiques Niveau Différent

**Problème** : Math adapté au niveau de chaque filière

**Solution** : **UE FILLES**
```
Créer : MTH100
Mode : [◉ UE Filles]
Classes : L1 Info, L1 Génie

Résultat :
- MTH100-L1INFO → Prof. KOFFI (Math pour Info)
- MTH100-L1GENIE → Prof. MARTIN (Math pour Génie)

Flexibilité : Contenu adapté par filière
```

### Cas 3 : Physique Composite en Tronc Commun

**Problème** : Physique identique, mais note composée

**Solution** : **TRONC COMMUN + COMPOSITE**
```
Mode : [◉ Tronc Commun]
Type : [◉ Composite]
Créer : PHY100
Classes : L1 Info, L1 Génie

Résultat :
- 1 UE : PHY100 (partagée)
- Sous-UE : Optique (60%) + Mécanique (40%)
- 1 prof : Prof. KOFFI
- Enseigne aux 2 classes
```

---

## 💻 LOGIQUE TECHNIQUE

### Base de Données

#### Table `ues`
```sql
id              INTEGER PRIMARY KEY
code_ue         VARCHAR(20)  -- ANG100 OU MTH100-L1INFO
intitule        VARCHAR(200)
credits         INTEGER
heures          INTEGER
coefficient     INTEGER
type_ue_creation VARCHAR(20) -- 'tronc_commun' ou 'simple'
classe_id       INTEGER      -- NULL si tronc commun
```

#### Table `ue_classe` (Many-to-Many)
```sql
ue_id           INTEGER
classe_id       INTEGER
-- Utilisée SEULEMENT pour tronc commun
```

### Logique Backend

```python
if mode_creation == 'tronc_commun':
    # Créer 1 UE
    ue = UE(code_ue=code_base, ...)  # ANG100
    
    # Associer toutes les classes
    for classe_id in classes_ids:
        ue.classes.append(classe)
    
    # Résultat : 1 UE partagée

elif mode_creation == 'ue_filles':
    # Créer N UE (1 par classe)
    for classe_id in classes_ids:
        code_muté = f"{code_base}-{classe.code}"
        ue = UE(code_ue=code_muté, ...)
    
    # Résultat : N UE indépendantes
```

---

## 🔄 WORKFLOWS COMPLETS

### Workflow 1 : Créer Tronc Commun
```
1. Directeur → UE → Ajouter
2. Choisir [◉ Tronc Commun]
3. Type : [◉ Simple]
4. Code : ANG100
5. Intitulé : Anglais Technique
6. Crédits : 2 (24h auto, coef 2 auto)
7. Cocher : L1 Info, L1 Génie, L1 Réseau
8. Valider

Résultat :
✅ 1 UE créée : ANG100
✅ 3 classes associées
✅ Code préservé

9. Affectations → Prof. MARTIN
10. Cocher ANG100
11. Enregistrer

Résultat Final :
✅ Prof. MARTIN enseigne ANG100 aux 3 classes
```

### Workflow 2 : Créer UE Filles
```
1. Directeur → UE → Ajouter
2. Choisir [◉ UE Filles]
3. Type : [◉ Simple]
4. Code : MTH100
5. Intitulé : Mathématiques I
6. Crédits : 3 (36h auto, coef 3 auto)
7. Cocher : L1 Info, L1 Génie
8. Valider

Résultat :
✅ 2 UE créées :
   - MTH100-L1INFO
   - MTH100-L1GENIE
✅ Codes mutés

9. Affectations → Prof. KOFFI
10. Cocher MTH100-L1INFO
11. Enregistrer

12. Affectations → Prof. DUPONT
13. Cocher MTH100-L1GENIE
14. Enregistrer

Résultat Final :
✅ Prof. KOFFI → MTH100 en L1 Info
✅ Prof. DUPONT → MTH100 en L1 Génie
```

---

## 🎨 AIDE CONTEXTUELLE

### Indicateur Dynamique

**Tronc Commun sélectionné** :
```
Code Unique : [MTH100________]
ℹ️ Code préservé (ex: ANG100)
```

**UE Filles sélectionné** :
```
Code Unique : [MTH100________]
ℹ️ Code sera muté par classe (ex: MTH100-L1INFO)
```

---

## ✅ AVANTAGES DU SYSTÈME

### Clarté Maximale
- ✅ 2 boutons distincts (Tronc Commun vs UE Filles)
- ✅ Aide contextuelle dynamique
- ✅ Impossible de se tromper

### Économie (Tronc Commun)
```
Avant : 3 profs pour 3 classes
Maintenant : 1 prof pour 3 classes
Économie : 66% des coûts enseignants
```

### Flexibilité (UE Filles)
```
Prof A → MTH100-L1INFO (Algo en Python)
Prof B → MTH100-L1GENIE (Algo en C++)
Contenu adapté au public !
```

---

## 📊 RÉSUMÉ

| Fonctionnalité | Status |
|----------------|--------|
| Mode Tronc Commun | ✅ |
| Mode UE Filles | ✅ |
| Type Simple | ✅ |
| Type Composite | ✅ |
| Aide contextuelle | ✅ |
| Calculs automatiques | ✅ |
| Interface intuitive | ✅ |
| Backend adapté | ✅ |

---

**Date** : 13 Février 2026  
**Version** : 5.0.0 - 2 Modes Distincts  
**Status** : ✅ PRODUCTION READY

🎉 **SYSTÈME COMPLET AVEC 2 MODES CLAIRS ET DISTINCTS !**

