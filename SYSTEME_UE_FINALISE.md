# ✅ SYSTÈME UE FINALISÉ - Multiplication Automatique

## 🎯 Fonctionnement Final

### Principe
Quand tu crées une UE et coches **5 classes**, le système crée automatiquement **5 UE distinctes** avec :
- Code muté : `MTH100` devient `MTH100-L1INFO`, `MTH100-L1GENIE`, etc.
- Heures calculées : **1 crédit = 12 heures**
- Coefficient automatique : **Coefficient = Crédits**

---

## 📊 Exemple Concret

### Tu crées :
```
Code UE    : MTH100
Intitulé   : Mathématiques I
Crédits    : 3

Classes cochées :
☑ L1 Info (code: L1INFO)
☑ L1 Génie (code: L1GENIE)
☑ L1 Réseau (code: L1RESEAU)
```

### Le système crée automatiquement :

| Code UE            | Classe      | Crédits | Heures (auto) | Coefficient (auto) |
|--------------------|-------------|---------|---------------|-------------------|
| MTH100-L1INFO      | L1 Info     | 3       | 36h           | 3                 |
| MTH100-L1GENIE     | L1 Génie    | 3       | 36h           | 3                 |
| MTH100-L1RESEAU    | L1 Réseau   | 3       | 36h           | 3                 |

**Résultat** : 3 UE indépendantes, chacune avec son propre ID !

---

## 🔢 Calculs Automatiques

### Formules
```python
heures = credits * 12
coefficient = credits
```

### Exemples
| Crédits | Heures | Coefficient |
|---------|--------|-------------|
| 1       | 12h    | 1           |
| 2       | 24h    | 2           |
| 3       | 36h    | 3           |
| 4       | 48h    | 4           |
| 5       | 60h    | 5           |
| 6       | 72h    | 6           |

---

## 📝 Interface Formulaire

### Champs Actifs
- ✅ **Code UE** (base) : Ex: MTH100
- ✅ **Intitulé** : Ex: Mathématiques I
- ✅ **Crédits** : Ex: 3
- ✅ **Classes** (checkboxes) : Cocher autant que nécessaire

### Champs Automatiques (lecture seule)
- 🔒 **Heures** : Calculé en temps réel (crédits × 12)
- 🔒 **Coefficient** : Égal aux crédits

### Affichage Dynamique
```
Crédits ECTS: [3]  ← Tu modifies ce champ
                ↓
Volume Horaire (auto): [36] Heures  ← Se met à jour automatiquement
Coefficient (auto): [3]              ← Se met à jour automatiquement
```

---

## 🎨 Codes UE Mutés

### Format
```
CODE_BASE-CODE_CLASSE
```

### Exemples Réels
```
MTH100 + L1 Info    → MTH100-L1INFO
PHY200 + L2 Génie   → PHY200-L2GENIE
ANG100 + M1 Réseau  → ANG100-M1RESEAU
```

---

## 🔄 Processus Complet

### Étape 1 : Création
```
1. Directeur → UE → Ajouter une UE
2. Remplir :
   - Code : MTH100
   - Intitulé : Mathématiques I
   - Crédits : 3 (heures et coef se calculent auto)
3. Cocher 5 classes
4. Valider
```

### Étape 2 : Multiplication
```
Le système crée 5 UE distinctes :
✅ MTH100-L1INFO   (L1 Info)     - 36h - Coef 3
✅ MTH100-L1GENIE  (L1 Génie)    - 36h - Coef 3
✅ MTH100-L1RESEAU (L1 Réseau)   - 36h - Coef 3
✅ MTH100-L2INFO   (L2 Info)     - 36h - Coef 3
✅ MTH100-L2GENIE  (L2 Génie)    - 36h - Coef 3
```

### Étape 3 : Affectation Enseignant
```
Directeur → Affectations Simplifiées
1. Voir Prof. KOFFI
2. Cocher les UE qu'il enseigne :
   ☑ MTH100-L1INFO
   ☑ MTH100-L1GENIE
   ☐ MTH100-L1RESEAU (pas celle-ci)
3. Enregistrer
```

**Résultat** : Prof. KOFFI enseigne MTH100 dans 2 classes seulement !

---

## ✅ Avantages du Système

### 1. Simplicité
- Créer 1 UE → Obtenir 5 UE automatiquement
- Plus besoin de créer manuellement chaque UE

### 2. Flexibilité
- Chaque UE est indépendante
- Affectation enseignant granulaire (prof différent par classe)

### 3. Clarté
- Code muté unique : MTH100-L1INFO (pas de confusion)
- Relation simple : 1 UE = 1 Classe

### 4. Automatisation
- Heures calculées automatiquement (1 crédit = 12h)
- Coefficient = Crédits (standard universitaire)

---

## 🔧 Modifications Techniques

### 1. Route `ajouter_ue`
**Fichier** : `app/routes/directeur.py`

```python
# Boucle sur chaque classe cochée
for classe_id in classes_ids:
    classe = Classe.query.get(int(classe_id))
    
    # Code muté
    code_ue_unique = f"{code_base}-{classe.code_classe}"
    
    # Calculs auto
    heures = credits * 12
    coefficient = credits
    
    # Créer UE indépendante
    nouvelle_ue = UE(
        code_ue=code_ue_unique,
        intitule=intitule,
        credits=credits,
        coefficient=coefficient,
        heures=heures,
        classe_id=int(classe_id)
    )
    db.session.add(nouvelle_ue)
```

### 2. Template `ajouter_ue.html`
**Modifications** :
- Champ crédits : Input actif
- Champ heures : Input readonly (calculé JS)
- Champ coefficient : Input readonly (calculé JS)
- JavaScript : Calcul temps réel

```javascript
function updateCalculations() {
    const credits = parseInt(creditsInput.value) || 0;
    heuresDisplay.value = credits * 12;
    coefDisplay.value = credits;
}
```

---

## 🧪 Tests

### Test 1 : Création UE Multiple
```
1. Créer UE : MTH100, 4 crédits
2. Cocher 3 classes
3. Vérifier : 3 UE créées avec codes mutés
4. Vérifier : 48h (4×12) et coef 4
```

### Test 2 : Calcul Automatique
```
1. Changer crédits à 5
2. Observer : Heures → 60, Coefficient → 5
3. Changer à 2
4. Observer : Heures → 24, Coefficient → 2
```

### Test 3 : Affectation Enseignant
```
1. Aller dans Affectations Simplifiées
2. Voir les UE avec codes mutés
3. Cocher certaines UE pour un prof
4. Vérifier : Affectation granulaire
```

---

## 📊 Résumé

| Fonctionnalité           | Status |
|--------------------------|--------|
| Multiplication automatique UE | ✅ |
| Code muté (MTH100-L1INFO) | ✅ |
| Heures auto (1 crédit = 12h) | ✅ |
| Coefficient auto (= crédits) | ✅ |
| Checkboxes classes | ✅ |
| Affectation simplifiée | ✅ |
| UE indépendantes | ✅ |

---

## 🎉 Résultat Final

**Le système est maintenant 100% opérationnel !**

- ✅ Créer 1 UE → Obtenir N UE (N = nombre de classes)
- ✅ Codes automatiquement mutés
- ✅ Heures et coefficient calculés automatiquement
- ✅ Affectation granulaire par enseignant
- ✅ Interface intuitive avec checkboxes

**Date** : 13 Février 2026
**Version** : 3.2.0 - Production Ready

