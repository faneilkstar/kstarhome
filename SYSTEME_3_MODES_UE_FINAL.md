# ✅ SYSTÈME FINAL - 3 MODES D'UE

## 🎯 LES 3 MODES DISTINCTS

### MODE 1 : UE SPÉCIFIQUE 📘
```
1 UE pour 1 SEULE classe
Code: MTH100 (préservé)
Classe: L1 Info uniquement
```

**Usage** : Cours spécifique à une seule classe

**Exemple** :
```
Code : MTH100
Intitulé : Mathématiques Avancées
Classe : L1 Info seulement

Résultat : 1 UE (MTH100) pour L1 Info
```

---

### MODE 2 : TRONC COMMUN 🌳
```
1 UE pour PLUSIEURS classes
Code: ANG100 (préservé)
Intitulé: Anglais (Tronc Commun L1/L2)
1 seul prof pour toutes
```

**Usage** : Langues, Sport, Éthique, Culture générale

**Exemple** :
```
Code : ANG100
Intitulé : Anglais Technique
Classes : L1 Info, L1 Génie, L1 Réseau

Résultat : 1 UE (ANG100)
Intitulé : Anglais Technique (Tronc Commun L1)
```

**Affichage automatique du niveau** :
- Classes L1 uniquement → "Tronc Commun L1"
- Classes L2 uniquement → "Tronc Commun L2"
- Classes L1 + L2 → "Tronc Commun L1/L2"
- Classes L1 + L2 + L3 → "Tronc Commun L1/L2/L3"

---

### MODE 3 : UE FILLES 📚
```
N UE distinctes (1 par classe)
Code muté: MTH100-L1INFO, MTH100-L1GENIE
Profs différents possibles
```

**Usage** : Cours similaires mais adaptés par classe

**Exemple** :
```
Code : MTH100
Intitulé : Mathématiques I
Classes : L1 Info, L1 Génie

Résultat : 2 UE
- MTH100-L1INFO (L1 Info)
- MTH100-L1GENIE (L1 Génie)
```

---

## 🎨 INTERFACE

### État Initial
```
[➕ DÉFINIR LA NATURE DE L'UE]
```

### Après Clic - 3 Boutons
```
[✅ NATURE DE L'UE DÉFINIE]

┌────────────────────────────────────────┐
│ [📘 UE SPÉCIFIQUE] [🌳 TRONC COMMUN]  │
│       [📚 UE FILLES]                   │
├────────────────────────────────────────┤
│ [📄 Simple] [📦 Composite]             │
└────────────────────────────────────────┘
```

---

## 📊 TABLEAU COMPARATIF

| Critère | UE Spécifique | Tronc Commun | UE Filles |
|---------|---------------|--------------|-----------|
| **Nombre UE** | 1 | 1 (partagée) | N (1 par classe) |
| **Code** | Préservé (MTH100) | Préservé (ANG100) | Muté (MTH100-L1INFO) |
| **Classes** | 1 seule | Plusieurs | Plusieurs |
| **Enseignants** | 1 prof | 1 seul prof | N profs possibles |
| **Intitulé** | Original | + (Tronc Commun L1) | Original |
| **Cochage** | 1 case | N cases | N cases |

---

## 🎯 CAS D'USAGE

### Cas 1 : Cours Spécifique à L1 Info

**Besoin** : Algorithmique uniquement pour L1 Info

**Solution** : UE SPÉCIFIQUE
```
Mode : [📘 UE Spécifique]
Code : ALG100
Intitulé : Algorithmique Avancée
Cocher : L1 Info SEULEMENT

Résultat : ALG100 pour L1 Info
```

### Cas 2 : Anglais Commun L1

**Besoin** : Anglais identique pour toutes les L1

**Solution** : TRONC COMMUN
```
Mode : [🌳 Tronc Commun]
Code : ANG100
Intitulé : Anglais Technique
Cocher : L1 Info, L1 Génie, L1 Réseau

Résultat : 
- 1 UE : ANG100
- Intitulé : Anglais Technique (Tronc Commun L1)
- 1 prof pour les 3 classes
```

### Cas 3 : Math Adaptée L1 et L2

**Besoin** : Math niveau différent par classe

**Solution** : UE FILLES
```
Mode : [📚 UE Filles]
Code : MTH100
Intitulé : Mathématiques
Cocher : L1 Info, L2 Info

Résultat : 
- MTH100-L1INFO (niveau L1)
- MTH100-L2INFO (niveau L2)
- 2 profs différents possibles
```

### Cas 4 : Sport Tronc Commun Multi-Niveaux

**Besoin** : Sport commun L1, L2, L3

**Solution** : TRONC COMMUN
```
Mode : [🌳 Tronc Commun]
Code : SPORT100
Intitulé : Éducation Physique
Cocher : L1 Info, L2 Info, L3 Info

Résultat :
- 1 UE : SPORT100
- Intitulé : Éducation Physique (Tronc Commun L1/L2/L3)
- 1 prof pour toutes les années
```

---

## 💻 LOGIQUE TECHNIQUE

### Détection Niveau (Tronc Commun)

```python
# Récupérer les classes
classes_obj = [Classe.query.get(cid) for cid in classes_ids]

# Extraire les années uniques
annees = set([c.annee for c in classes_obj if c.annee])
# Exemple: {1, 2} pour L1 et L2

# Construire le libellé
if annees:
    niveaux = sorted([f"L{a}" for a in annees])
    # ['L1', 'L2']
    
    libelle = f"Tronc Commun {'/'.join(niveaux)}"
    # "Tronc Commun L1/L2"

# Intégrer au titre
intitule_final = f"{intitule} ({libelle})"
# "Anglais Technique (Tronc Commun L1/L2)"
```

---

## 🔄 WORKFLOWS

### Workflow 1 : UE Spécifique
```
1. Clic "DÉFINIR LA NATURE"
2. Choisir [📘 UE Spécifique]
3. Code: ALG100, Intitulé: Algorithmique
4. Cocher: L1 Info UNIQUEMENT
5. Valider

Résultat : ✅ ALG100 (L1 Info)
```

### Workflow 2 : Tronc Commun
```
1. Clic "DÉFINIR LA NATURE"
2. Choisir [🌳 Tronc Commun]
3. Code: ANG100, Intitulé: Anglais
4. Cocher: L1 Info, L1 Génie, L2 Info
5. Valider

Résultat : ✅ ANG100 (Tronc Commun L1/L2)
Intitulé : Anglais (Tronc Commun L1/L2)
```

### Workflow 3 : UE Filles
```
1. Clic "DÉFINIR LA NATURE"
2. Choisir [📚 UE Filles]
3. Code: MTH100, Intitulé: Mathématiques
4. Cocher: L1 Info, L1 Génie
5. Valider

Résultat : ✅ 2 UE créées
- MTH100-L1INFO
- MTH100-L1GENIE
```

---

## ✅ RÉSUMÉ

| Mode | Classes | Code | Intitulé | Profs |
|------|---------|------|----------|-------|
| **Spécifique** | 1 | MTH100 | Original | 1 |
| **Tronc Commun** | N | ANG100 | + (Tronc L1/L2) | 1 |
| **UE Filles** | N | MTH100-L1INFO | Original | N |

---

**Version** : 6.0.0 - 3 Modes Complets  
**Status** : ✅ OPÉRATIONNEL  
**Test** : ✅ Application OK

🎉 **SYSTÈME COMPLET AVEC 3 MODES + LIBELLÉ AUTOMATIQUE !**

