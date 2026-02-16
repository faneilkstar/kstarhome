# ✅ SECTION UE NON AFFECTÉES

## 🎯 Fonctionnalité Ajoutée

Une **section d'alerte** affiche maintenant les UE qui n'ont **aucun enseignant affecté** en haut de la page d'affectations.

---

## 📊 Interface

### Cas 1 : UE Non Affectées Détectées

```
┌──────────────────────────────────────────────────────────┐
│ ⚠️ UE sans enseignant assigné                            │
│                                                           │
│ 5 UE n'ont pas encore d'enseignant affecté               │
│                                      [👁️ Voir la liste]  │
└──────────────────────────────────────────────────────────┘

Clic sur "Voir la liste" ▼

┌──────────────────────────────────────────────────────────┐
│ ⚠️ UE sans enseignant assigné                            │
│                                                           │
│ 5 UE n'ont pas encore d'enseignant affecté               │
│                                      [🙈 Masquer]         │
├───────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ MTH100-L1IN  │  │ PHY101-L1GE  │  │ INF200-L2IN  │  │
│  │ Math I       │  │ Physique I   │  │ Algo Avancé  │  │
│  │ 3 ECTS  36h  │  │ 4 ECTS  48h  │  │ 5 ECTS  60h  │  │
│  │ [L1 Info]    │  │ [L1 Génie]   │  │ [L2 Info]    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Cas 2 : Toutes les UE Affectées

```
┌──────────────────────────────────────────────────────────┐
│ ✅ Excellent ! Toutes les UE ont un enseignant assigné.  │
└──────────────────────────────────────────────────────────┘
```

---

## 🔍 Détection Automatique

### Logique Jinja2

```jinja2
{% set ues_non_affectees = [] %}
{% for ue in ues %}
    {% if ue.enseignants|length == 0 %}
        {% set _ = ues_non_affectees.append(ue) %}
    {% endif %}
{% endfor %}
```

**Explication** :
- Parcourt toutes les UE
- Vérifie si `ue.enseignants` est vide
- Ajoute l'UE à la liste `ues_non_affectees`

---

## 🎨 Affichage des UE Non Affectées

### Card UE

Chaque UE non affectée est affichée dans une card jaune :

```html
<div class="card border-warning">
    <div class="card-body">
        <h6>🔵 MTH100-L1INFO</h6>
        <p>Mathématiques I</p>
        <div>
            <span class="badge bg-info">3 ECTS</span>
            <span class="badge bg-secondary">36h</span>
            <span class="badge bg-warning">L1 Info</span>
        </div>
    </div>
</div>
```

**Informations affichées** :
- Code UE (avec bordure jaune)
- Intitulé
- Crédits ECTS
- Volume horaire
- Classe concernée

---

## 📈 Statistiques Affichées

### Compteur

```
5 UE n'ont pas encore d'enseignant affecté
```

**Calcul** : `{{ ues_non_affectees|length }}`

---

## 💡 Utilisation

### Workflow Directeur

```
1. Aller sur : Directeur → Affectations UE
   ↓
2. Voir en haut :
   - Alerte jaune si UE non affectées
   - Message vert si tout est OK
   ↓
3. Cliquer "Voir la liste"
   ↓
4. Liste des UE sans prof s'affiche
   ↓
5. Descendre et affecter ces UE aux enseignants
```

---

## 🔄 Fonctionnement du Bouton

### JavaScript

```javascript
function toggleUENonAffectees() {
    const list = document.getElementById('liste-non-affectees');
    const icon = document.getElementById('icon-non-affectees');
    const text = document.getElementById('text-non-affectees');
    
    if (list.classList.contains('show')) {
        // Masquer
        list.classList.remove('show');
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
        text.textContent = 'Voir la liste';
    } else {
        // Afficher
        list.classList.add('show');
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
        text.textContent = 'Masquer';
    }
}
```

**Changements** :
- Icône : 👁️ (Voir) ↔ 🙈 (Masquer)
- Texte : "Voir la liste" ↔ "Masquer"
- Collapse Bootstrap pour l'animation

---

## 🎨 Style Visuel

### Alerte Jaune (UE non affectées)

```html
<div class="alert alert-warning shadow-sm">
    <h5>⚠️ UE sans enseignant assigné</h5>
    <p>5 UE n'ont pas encore d'enseignant affecté</p>
    <button class="btn btn-warning">Voir la liste</button>
</div>
```

### Alerte Verte (Tout OK)

```html
<div class="alert alert-success shadow-sm">
    ✅ Excellent ! Toutes les UE ont un enseignant assigné.
</div>
```

### Cards UE

- **Bordure** : Jaune (warning)
- **Badges** : Info (crédits), Secondary (heures), Warning (classe)
- **Layout** : 3 colonnes sur desktop, 2 sur tablette, 1 sur mobile

---

## 📊 Exemples

### Scénario 1 : École avec 15 UE

```
Total UE : 15
- 12 UE affectées à des enseignants
- 3 UE non affectées

Affichage :
┌───────────────────────────────────────┐
│ ⚠️ 3 UE sans enseignant [Voir liste] │
└───────────────────────────────────────┘
```

### Scénario 2 : École avec 20 UE

```
Total UE : 20
- 20 UE affectées

Affichage :
┌────────────────────────────────────────────┐
│ ✅ Toutes les UE ont un enseignant assigné │
└────────────────────────────────────────────┘
```

### Scénario 3 : Nouvelle école

```
Total UE : 10
- 0 UE affectées

Affichage :
┌────────────────────────────────────────┐
│ ⚠️ 10 UE sans enseignant [Voir liste] │
└────────────────────────────────────────┘

Liste complète des 10 UE affichée
```

---

## ✅ Avantages

### 1. Vue d'ensemble rapide
- Voir immédiatement si des UE n'ont pas de prof
- Compteur clair du nombre d'UE concernées

### 2. Action ciblée
- Liste détaillée des UE à traiter
- Informations complètes pour chaque UE

### 3. Suivi de l'affectation
- Validation visuelle quand tout est OK
- Alerte permanente tant qu'il reste des UE

### 4. Interface propre
- Section masquée par défaut
- Clic pour afficher/masquer
- Pas de surcharge visuelle

---

## 🔧 Code Technique

### Template Jinja2

**Fichier** : `app/templates/directeur/affecter_ues_enseignants.html`

```jinja2
<!-- Détection des UE non affectées -->
{% set ues_non_affectees = [] %}
{% for ue in ues %}
    {% if ue.enseignants|length == 0 %}
        {% set _ = ues_non_affectees.append(ue) %}
    {% endif %}
{% endfor %}

<!-- Affichage conditionnel -->
{% if ues_non_affectees %}
    <!-- Alerte jaune avec liste -->
{% else %}
    <!-- Message de succès -->
{% endif %}
```

### JavaScript

```javascript
// Fonction toggle pour afficher/masquer
function toggleUENonAffectees() {
    // Toggle de la classe 'show' Bootstrap
    // Changement d'icône et de texte
}
```

---

## 📱 Responsive

### Desktop (> 992px)
- 3 cards par ligne
- Affichage côte à côte

### Tablette (768px - 992px)
- 2 cards par ligne
- Adapté à la largeur

### Mobile (< 768px)
- 1 card par ligne
- Pleine largeur

---

## 🧪 Tests

### Test 1 : Aucune UE
```
Créer 0 UE
→ Pas d'alerte affichée
→ ✅ OK
```

### Test 2 : Toutes affectées
```
Créer 5 UE
Affecter les 5 à des profs
→ Message vert "Toutes les UE ont un enseignant"
→ ✅ OK
```

### Test 3 : Certaines non affectées
```
Créer 10 UE
Affecter 7 UE
→ Alerte jaune "3 UE sans enseignant"
→ Clic "Voir liste" → 3 cards affichées
→ ✅ OK
```

### Test 4 : Affichage dynamique
```
État initial : 5 UE non affectées
Affecter 1 UE
Recharger la page
→ "4 UE sans enseignant"
→ ✅ Mise à jour automatique
```

---

## 📊 Résumé

| Fonctionnalité | Status |
|----------------|--------|
| Détection automatique UE non affectées | ✅ |
| Compteur d'UE | ✅ |
| Alerte visuelle (jaune/vert) | ✅ |
| Bouton afficher/masquer | ✅ |
| Liste détaillée des UE | ✅ |
| Cards avec infos complètes | ✅ |
| Design responsive | ✅ |
| Animation collapse | ✅ |

---

## 🎯 Impact

### Avant
- Pas de visibilité sur les UE non affectées
- Risque d'oublier des UE
- Vérification manuelle nécessaire

### Maintenant
- ✅ Alerte immédiate en haut de page
- ✅ Compteur précis
- ✅ Liste détaillée accessible en 1 clic
- ✅ Validation visuelle quand tout est OK

---

**Date** : 13 Février 2026  
**Version** : 3.2.3  
**Status** : ✅ OPÉRATIONNEL

🎉 **Section UE non affectées implémentée avec succès !**

