# ✅ SYSTÈME D'AFFECTATION PAR CHECKBOXES

## 🎯 Fonctionnement

### Interface Simplifiée
Au lieu de sélectionner un prof puis une UE dans des dropdowns, tu vois maintenant :

**1 SECTION PAR ENSEIGNANT** avec **TOUTES LES UE EN CHECKBOXES**

---

## 📊 Exemple Visuel

```
┌──────────────────────────────────────────────────────────────┐
│ 👨‍🏫 KOFFI Kodjo                                               │
│ Professeur - Cybersécurité              [3 UE actuellement] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │☑ MTH100-L1IN │  │☐ PHY101-L1GE │  │☑ INF200-L2IN │     │
│  │Math I        │  │Physique I    │  │Algo Avancé   │     │
│  │3 ECTS  36h   │  │4 ECTS  48h   │  │5 ECTS  60h   │     │
│  │L1 Info    ✓  │  │L1 Génie      │  │L2 Info    ✓  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │☐ ANG100-L1IN │  │☑ MTH200-L2GE │                        │
│  │Anglais I     │  │Math II       │                        │
│  │2 ECTS  24h   │  │4 ECTS  48h   │                        │
│  │L1 Info       │  │L2 Génie   ✓  │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                              │
│                    [💾 Enregistrer les affectations]         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 👨‍🏫 DUPONT Marie                                             │
│ Maître de Conférences - Physique        [2 UE actuellement] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │☐ MTH100-L1IN │  │☑ PHY101-L1GE │  │☐ INF200-L2IN │     │
│  │Math I        │  │Physique I ✓  │  │Algo Avancé   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│                    [💾 Enregistrer les affectations]         │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎨 Affichage des UE

Chaque card d'UE affiche :
- **Code UE** : MTH100-L1INFO (avec mutation classe)
- **Intitulé** : Mathématiques I
- **Crédits** : 3 ECTS
- **Heures** : 36h (calculé auto)
- **Classe** : L1 Info (badge jaune)
- **Filière** : Licence Informatique
- **Icône ✓** : Si déjà affectée à ce prof

---

## 🔄 Processus d'Affectation

### Étape 1 : Accès
```
Directeur → Dashboard → "Affectations UE"
Ou directement : /directeur/affectations-simplifiees
```

### Étape 2 : Sélection
```
1. Tu vois une section par enseignant
2. Pour Prof. KOFFI :
   - Tu coches MTH100-L1INFO
   - Tu coches MTH100-L1GENIE
   - Tu coches INF200-L2INFO
3. Clique sur "Enregistrer les affectations"
```

### Étape 3 : Résultat
```
✅ Prof. KOFFI enseigne maintenant 3 UE :
   - MTH100 en L1 Info
   - MTH100 en L1 Génie
   - INF200 en L2 Info
```

---

## 💡 Avantages du Système

### 1. Vue Globale
- Tu vois **toutes** les UE disponibles d'un coup
- Tu vois ce qui est **déjà affecté** (bordure verte + ✓)

### 2. Affectation Multiple
- Cocher plusieurs UE d'un coup pour un prof
- Un seul clic "Enregistrer" pour tout sauvegarder

### 3. Flexibilité Totale
- **MTH100-L1INFO** peut être affecté à Prof. KOFFI
- **MTH100-L1GENIE** peut être affecté à Prof. DUPONT
- **MTH100-L1RESEAU** peut être affecté à Prof. MARTIN
- Chaque UE est indépendante !

### 4. Interface Intuitive
- **Cliquer sur la card** = Cocher/Décocher
- **Bordure verte** = UE affectée
- **Badge jaune** = Classe concernée
- **Icône ✓** = Confirmation visuelle

---

## 🎯 Cas d'Usage

### Cas 1 : Un Prof pour Toutes les Classes
```
Prof. KOFFI enseigne MTH100 dans TOUTES les classes
→ Cocher MTH100-L1INFO, MTH100-L1GENIE, MTH100-L1RESEAU, etc.
```

### Cas 2 : Spécialisation par Classe
```
Prof. KOFFI  → MTH100-L1INFO + MTH100-L1GENIE
Prof. DUPONT → MTH100-L1RESEAU + MTH100-L2INFO
```

### Cas 3 : Un Prof, Une UE
```
Prof. MARTIN → Seulement INF300-M1RESEAU
```

---

## 🔧 Technique

### Route d'Affichage
**URL** : `/directeur/affectations-simplifiees`

```python
@bp.route('/affectations-simplifiees')
def affectations_simplifiees():
    ues = UE.query.order_by(UE.code_ue).all()
    enseignants = Enseignant.query.filter_by(actif=True).all()
    return render_template('directeur/affecter_ues_enseignants.html', 
                         ues=ues, enseignants=enseignants)
```

### Route d'Enregistrement
**URL** : `/directeur/enseignant/<id>/affecter-ues`

```python
@bp.route('/enseignant/<int:enseignant_id>/affecter-ues', methods=['POST'])
def affecter_ues_a_enseignant(enseignant_id):
    enseignant = Enseignant.query.get_or_404(enseignant_id)
    ues_ids = request.form.getlist('ues_ids')
    
    # Supprimer anciennes affectations
    enseignant.ues.clear()
    
    # Ajouter nouvelles affectations
    for ue_id in ues_ids:
        ue = UE.query.get(ue_id)
        if ue:
            enseignant.ues.append(ue)
    
    db.session.commit()
    flash(f"✅ {len(ues_ids)} UE(s) affectées", "success")
```

---

## 🎨 Design

### Card UE Non Cochée
```
┌─────────────────────┐
│☐ MTH100-L1INFO     │ ← Bordure grise
│ Mathématiques I    │
│ 3 ECTS  36h        │
│ [L1 Info]          │ ← Badge jaune
│ Licence Info       │
└─────────────────────┘
```

### Card UE Cochée
```
┌─────────────────────┐ ← Bordure verte
│☑ MTH100-L1INFO  ✓  │ ← Icône ✓
│ Mathématiques I    │
│ 3 ECTS  36h        │
│ [L1 Info]          │
│ Licence Info       │
└─────────────────────┘
Fond légèrement vert
```

---

## 📱 Interactivité

### JavaScript
```javascript
// Cliquer sur la card = toggle checkbox
card.addEventListener('click', function() {
    checkbox.checked = !checkbox.checked;
    
    if (checkbox.checked) {
        card.classList.add('border-success', 'bg-light');
    } else {
        card.classList.remove('border-success', 'bg-light');
    }
});
```

### Animation
- **Hover** : Card se soulève légèrement
- **Clic** : Bordure change de couleur instantanément
- **Checkbox** : Se met à jour visuellement

---

## 🧪 Test Rapide

### Test 1 : Affectation Simple
```
1. Va sur : Directeur → Affectations UE
2. Cherche "KOFFI Kodjo"
3. Coche 3 UE
4. Clique "Enregistrer"
5. ✅ Voir le message de confirmation
```

### Test 2 : Modification
```
1. Retourne sur Affectations UE
2. Décoche 1 UE, coche 2 nouvelles
3. Enregistrer
4. ✅ Les anciennes sont retirées, nouvelles ajoutées
```

### Test 3 : Vérification
```
1. Va sur : Directeur → Enseignants
2. Clique sur "KOFFI"
3. ✅ Voir la liste de ses UE affectées
```

---

## 📊 Statistiques Affichées

Pour chaque enseignant :
- **Nombre d'UE actuellement** : Badge en haut à droite
- **Grade et spécialité** : Sous le nom
- **UE cochées** : Bordure verte + icône ✓

---

## ✅ Résumé

| Fonctionnalité | Status |
|----------------|--------|
| Checkboxes par UE | ✅ |
| Une section par enseignant | ✅ |
| Affichage classe + filière | ✅ |
| Code UE muté (MTH100-L1INFO) | ✅ |
| Icône ✓ pour UE affectées | ✅ |
| Bordure verte = affecté | ✅ |
| Clic sur card = cocher | ✅ |
| Enregistrement en masse | ✅ |
| Lien dans dashboard | ✅ |

---

## 🎉 Résultat Final

**Tu as maintenant une interface d'affectation ultra-intuitive !**

- ✅ Voir toutes les UE en un coup d'œil
- ✅ Cocher/décocher facilement
- ✅ Enregistrer toutes les affectations d'un prof en 1 clic
- ✅ Code UE muté visible (MTH100-L1INFO)
- ✅ Classe affichée sur chaque UE
- ✅ Interface responsive et moderne

**Accès** : Dashboard Directeur → **Affectations UE**

**Date** : 13 Février 2026
**Version** : 3.2.0

