# 🎓 CARTES ENSEIGNANTS - GUIDE COMPLET

## ✅ CE QUI A ÉTÉ AJOUTÉ

### Nouveaux fichiers
1. ✅ **`app/templates/cartes/ma_carte_enseignant.html`** - Template carte enseignant
2. ✅ **Méthodes dans `carte_etudiant_service.py`** :
   - `generer_carte_enseignant()`
   - `_dessiner_bandeau_enseignant()`
   - `_ajouter_photo_enseignant()`
   - `_creer_avatar_initiales_enseignant()`
   - `_ajouter_informations_enseignant()`
   - `_ajouter_qr_code_enseignant()`
   - `_ajouter_badge_professionnel()`

### Routes ajoutées
1. ✅ **`/cartes/ma-carte-enseignant`** - Afficher la carte
2. ✅ **`/cartes/telecharger-enseignant/<id>`** - Télécharger

---

## 📊 MODÈLE ENSEIGNANT (DÉJÀ EXISTANT)

Le modèle `Enseignant` contient déjà tous les champs nécessaires :

```python
class Enseignant(db.Model):
    id
    user_id
    nom                 ✅
    prenom              ✅
    date_naissance      ✅
    sexe                ✅
    telephone           ✅
    adresse             ✅
    grade               ✅
    specialite          ✅
    date_embauche
    actif
    mot_de_passe_initial
```

---

## 🎨 CARTE ENSEIGNANT VS CARTE ÉTUDIANT

### Différences visuelles

| Élément | Carte Étudiant | Carte Enseignant |
|---------|----------------|------------------|
| **Bandeau** | Bleu clair | Doré plus intense |
| **Titre** | "Carte Étudiant" | "Carte Enseignant" |
| **Photo** | Fond or clair | Fond or foncé |
| **Matricule** | ETU12345 | ENS00001 |
| **Info 1** | Classe/Filière | Grade académique |
| **Info 2** | Année | Spécialité |
| **Badge** | NFC simple | Badge professionnel (grade) |
| **QR Code** | Données étudiant | Données enseignant + "ENSEIGNANT" |

---

## 📸 STRUCTURE CARTE ENSEIGNANT

```
┌────────────────────────────────────────────────┐
│ 🟡 POLYTECH INFINITY (Bandeau doré foncé)     │
│ Carte Enseignant 2025-2026                     │
├────────────────────────────────────────────────┤
│                                                │
│  [Photo]    M./Mme NOM PRÉNOM                  │
│  150x150    Matricule: ENS00001          [QR]  │
│             Grade: Professeur            Code  │
│             Spécialité: Informatique           │
│                                          [P]   │
│                                     (Badge)    │
├────────────────────────────────────────────────┤
│ www.polytech-infinity.com  |  Émise le...     │
│ Le Directeur: Admin                            │
└────────────────────────────────────────────────┘
```

---

## 🚀 UTILISATION

### Pour un enseignant

**Accéder à sa carte** :
```
http://localhost:5000/cartes/ma-carte-enseignant
```

**Télécharger** :
```
http://localhost:5000/cartes/telecharger-enseignant/{enseignant_id}
```

### Dans le dashboard enseignant

Ajouter ce lien :
```html
<a href="{{ url_for('cartes.ma_carte_enseignant') }}" class="btn btn-gold">
    <i class="fas fa-id-badge me-2"></i>Ma carte enseignant
</a>
```

---

## 💻 EXEMPLE D'UTILISATION

### Générer une carte enseignant

```python
from app.services.carte_etudiant_service import CarteEtudiantService

service = CarteEtudiantService()
enseignant = Enseignant.query.get(1)

carte_path = service.generer_carte_enseignant(enseignant)
# Retourne: app/static/cartes/carte_enseignant_ENS00001_20260216.png
```

---

## 📋 INFORMATIONS SUR LA CARTE

### Affichées sur la carte :
- ✅ Titre (M./Mme)
- ✅ Nom et prénom
- ✅ Matricule (ENS00001)
- ✅ Grade académique
- ✅ Spécialité
- ✅ QR Code
- ✅ Badge professionnel
- ✅ Signature du directeur

### Dans le template (infos complémentaires) :
- ✅ Date de naissance
- ✅ Téléphone
- ✅ Date d'émission
- ✅ Nom du directeur

---

## 🎯 FONCTIONNALITÉS

### Carte physique
- ✅ Format 85.6 x 54 mm (carte bancaire)
- ✅ Résolution 300 DPI
- ✅ Photo de profil ou initiales
- ✅ QR Code doré
- ✅ Badge professionnel avec initiale du grade
- ✅ Signature du directeur en pied de page

### Template web
- ✅ Prévisualisation HD
- ✅ Effet 3D au survol
- ✅ Bouton télécharger
- ✅ Bouton imprimer
- ✅ Informations détaillées
- ✅ Instructions d'utilisation

---

## 🔒 SÉCURITÉ

### QR Code
**Contenu** : `POLYTECH-ENS00001-NOM-PRENOM-ENSEIGNANT`
- Identifie clairement un enseignant
- Différenciation avec les étudiants
- Vérification rapide par scan

### Badge professionnel
- Affiche l'initiale du grade (P = Professeur, M = Maître, A = Assistant)
- Identification visuelle rapide du statut

---

## 📱 RESPONSIVE

### Impression
```css
@media print {
    /* Seule la carte est imprimée */
    .carte-preview {
        width: 85.6mm;
        height: 54mm;
    }
}
```

### Mobile
- ✅ Interface adaptative
- ✅ Boutons tactiles
- ✅ Zoom sur la carte

---

## 🎨 PERSONNALISATION

### Changer le badge professionnel

Dans `_ajouter_badge_professionnel()` :
```python
# Personnaliser selon le grade
if enseignant.grade == "Professeur":
    badge_text = "Prof"
    badge_color = self.color_gold
elif enseignant.grade == "Maître":
    badge_text = "MC"
    badge_color = (184, 134, 11)  # Or foncé
```

### Ajouter le département

Dans `_ajouter_informations_enseignant()` :
```python
# Département (à ajouter au modèle Enseignant)
if enseignant.departement:
    y_start += 50
    draw.text((x, y_start), "Département:", fill=self.color_gray, font=font_label)
    draw.text((x, y_start + 18), enseignant.departement, fill=self.color_black, font=font_info)
```

---

## 🔗 ROUTES COMPLÈTES

| Route | Méthode | Description | Rôle |
|-------|---------|-------------|------|
| `/cartes/ma-carte` | GET | Carte étudiant | ETUDIANT |
| `/cartes/ma-carte-enseignant` | GET | Carte enseignant | ENSEIGNANT |
| `/cartes/telecharger/<id>` | GET | DL carte étudiant | ETUDIANT/DIRECTEUR |
| `/cartes/telecharger-enseignant/<id>` | GET | DL carte enseignant | ENSEIGNANT/DIRECTEUR |
| `/cartes/generer-toutes` | GET | Batch étudiants | DIRECTEUR |

---

## ✅ CHECKLIST

### Déjà fait :
- [x] Modèle Enseignant avec tous les champs
- [x] Service génération carte enseignant
- [x] Routes carte enseignant
- [x] Template carte enseignant
- [x] Support QR code
- [x] Badge professionnel
- [x] Signature directeur

### À faire :
- [ ] Ajouter lien dans dashboard enseignant
- [ ] Tester génération avec photo
- [ ] Tester génération sans photo
- [ ] Tester impression
- [ ] Déployer sur Vercel

---

## 🖨️ IMPRESSION

### Paramètres recommandés
- **Format** : 85.6 x 54 mm
- **Résolution** : 300 DPI minimum
- **Papier** : Photo brillant ou PVC
- **Finition** : Plastification obligatoire (carte professionnelle)

### Différence avec carte étudiant
- ✅ Papier plus épais recommandé
- ✅ Plastification renforcée
- ✅ Badge professionnel en relief (optionnel)

---

## 📊 STATISTIQUES

### Code ajouté
- **~150 lignes** Python (service)
- **~250 lignes** HTML/CSS (template)
- **2 routes** Flask

### Fichiers
- **1 nouveau** template
- **1 fichier** modifié (service)
- **1 fichier** modifié (routes)

---

**Version** : 11.4.0 - Cartes Enseignants  
**Date** : 16 février 2026  
**Statut** : ✅ PRÊT POUR TEST

🎓 **CARTES ENSEIGNANTS CRÉÉES !**  
📸 **PHOTO, QR CODE, BADGE PROFESSIONNEL !**  
✅ **PRÊT POUR IMPRESSION ET UTILISATION !**

