# ✅ FICHE D'INSCRIPTION UE AVEC PHOTO

## 🎯 Fonctionnalité Implémentée

Après avoir choisi ses UE, l'étudiant peut **télécharger une fiche PDF officielle** contenant :
- 📸 Emplacement pour photo d'identité
- 👤 Informations personnelles (nom, matricule, classe, filière)
- 📚 Liste complète des UE inscrites avec :
  - Code UE
  - Intitulé
  - Crédits ECTS
  - Volume horaire
- 📊 Total des crédits et heures
- ✍️ Zones de signature (étudiant + cachet établissement)

---

## 📄 Structure du PDF

### 1. En-tête
```
╔═══════════════════════════════════════════════════╗
║    FICHE D'INSCRIPTION PÉDAGOGIQUE               ║
║         Année Académique 2025-2026               ║
╚═══════════════════════════════════════════════════╝
```

### 2. Section Identité
```
┌────────┐    INFORMATIONS ÉTUDIANT
│ PHOTO  │    Nom & Prénom : KOFFI Kodjo
│   D'   │    Matricule    : ETU-2026-0042
│IDENTITÉ│    Classe       : L1 Info
└────────┘    Filière      : Licence Informatique
```

### 3. Tableau des UE
```
═══════════════════════════════════════════════════════
CODE UE    INTITULÉ                  CRÉDITS   HEURES
───────────────────────────────────────────────────────
MTH100     Mathématiques I              3       36h
PHY101     Physique I                   4       48h
INF102     Algorithmique                5       60h
ANG100     Anglais I                    2       24h
───────────────────────────────────────────────────────
TOTAL                                  14      168h
═══════════════════════════════════════════════════════
```

### 4. Bas de page
```
Date d'impression : 13/02/2026 à 15:30

Signature de l'étudiant :         Cachet de l'établissement :
_____________________             _____________________

       Document officiel - À conserver précieusement
              Polytech Academy - Année 2026
```

---

## 🔄 Workflow Étudiant

### Étape 1 : Connexion
```
Étudiant se connecte → Dashboard
```

### Étape 2 : Choisir UE
```
Menu → Inscription Modules
↓
Cocher les UE désirées
↓
Cliquer "Confirmer l'inscription"
✅ Inscription enregistrée
```

### Étape 3 : Télécharger la fiche
```
Bouton "📥 Télécharger ma fiche" apparaît
↓
Clic sur le bouton
↓
PDF généré et téléchargé automatiquement
```

---

## 💻 Code Implémenté

### Route de téléchargement
**Fichier** : `app/routes/etudiant.py`

```python
@bp.route('/telecharger-fiche-ue')
@etudiant_required
def telecharger_fiche_ue():
    etudiant = Etudiant.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Récupérer les UE inscrites
    inscriptions = InscriptionUE.query.filter_by(
        etudiant_id=etudiant.id,
        statut='validé'
    ).all()
    
    if not inscriptions:
        flash("Vous devez d'abord choisir vos UE...", "warning")
        return redirect(url_for('etudiant.choisir_ues'))
    
    # Génération PDF avec ReportLab
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # ... (Génération complète du PDF)
    
    return send_file(buffer, as_attachment=True, 
                    download_name=f"Fiche_Inscription_UE_{etudiant.nom}_{etudiant.prenom}.pdf")
```

### Bouton dans le template
**Fichier** : `app/templates/etudiant/choisir_ues.html`

```html
{% if ues_inscrites_ids %}
<a href="{{ url_for('etudiant.telecharger_fiche_ue') }}" 
   class="btn btn-success btn-lg">
    <i class="fas fa-download me-2"></i>Télécharger ma fiche
</a>
{% endif %}
```

---

## 🎨 Fonctionnalités PDF

### 1. Photo d'identité
- Cadre rectangulaire 80x80 pixels
- Bordure bleue
- Texte "PHOTO D'IDENTITÉ" au centre

### 2. Informations personnelles
- Nom & Prénom en majuscules
- Matricule (ou "En attente" si pas encore généré)
- Classe et Filière

### 3. Tableau des UE
- Alternance de couleurs (lignes grise/blanche)
- Code UE
- Intitulé (tronqué si > 35 caractères)
- Crédits ECTS
- Volume horaire

### 4. Calculs automatiques
- **Total crédits** : Somme de tous les crédits
- **Total heures** : Somme de toutes les heures

### 5. Pagination automatique
- Si trop d'UE pour une page → Nouvelle page créée automatiquement

---

## ✅ Validation

### Conditions de téléchargement
```python
if not inscriptions:
    flash("Vous devez d'abord choisir vos UE", "warning")
    return redirect(url_for('etudiant.choisir_ues'))
```

**Logique** :
- Bouton visible SEULEMENT si UE déjà inscrites
- Si clic sans UE → Redirection + message d'avertissement

---

## 📊 Exemple de Fiche Générée

### Pour un étudiant inscrit à 5 UE

```
═════════════════════════════════════════════════════════
    FICHE D'INSCRIPTION PÉDAGOGIQUE
         Année Académique 2025-2026
═════════════════════════════════════════════════════════

┌────────┐    INFORMATIONS ÉTUDIANT
│ PHOTO  │    
│   D'   │    Nom & Prénom : KOUASSI Marie
│IDENTITÉ│    Matricule    : ETU-2026-0123
└────────┘    Classe       : L1 Info
              Filière      : Licence Informatique

═════════════════════════════════════════════════════════
UNITÉS D'ENSEIGNEMENT (UE) INSCRITES
─────────────────────────────────────────────────────────

CODE UE    INTITULÉ                       CRÉDITS  HEURES
─────────────────────────────────────────────────────────
MTH100     Mathématiques I                   3      36h
PHY101     Physique Générale I               4      48h
INF102     Algorithmique et Programmation    5      60h
ANG100     Anglais Technique I               2      24h
COM101     Communication                     2      24h
─────────────────────────────────────────────────────────
TOTAL                                       16     192h
═════════════════════════════════════════════════════════

Date d'impression : 13/02/2026 à 15:45

Signature de l'étudiant :         Cachet de l'établissement :
_____________________             _____________________

       Document officiel - À conserver précieusement
              Polytech Academy - Année 2026
```

---

## 🎯 Utilisation

### Pour l'étudiant
1. Se connecter
2. Aller dans **Inscription Modules**
3. Cocher les UE désirées
4. Cliquer **Confirmer l'inscription**
5. Cliquer **📥 Télécharger ma fiche**
6. PDF téléchargé automatiquement

### Pour l'établissement
- Document officiel à imprimer
- L'étudiant colle sa photo sur le cadre
- Signature de l'étudiant
- Cachet de l'établissement
- Archivage du document

---

## 📁 Fichiers Modifiés

1. ✅ `app/routes/etudiant.py` - Route de téléchargement ajoutée
2. ✅ `app/templates/etudiant/choisir_ues.html` - Bouton ajouté

**Total** : 2 fichiers

---

## ✅ Tests

### Test 1 : Sans UE inscrites
```
Aller sur Inscription Modules
→ Bouton "Télécharger" NON visible
→ ✅ OK
```

### Test 2 : Avec UE inscrites
```
Choisir 3 UE
Confirmer
→ Bouton "Télécharger" visible
→ ✅ OK
```

### Test 3 : Téléchargement
```
Clic sur "Télécharger ma fiche"
→ PDF généré et téléchargé
→ Contient photo, infos, UE, totaux
→ ✅ OK
```

### Test 4 : Pagination
```
Inscrire à 20 UE
Télécharger
→ PDF sur 2 pages
→ ✅ OK
```

---

## 🎨 Design PDF

### Couleurs
- **Titre** : Bleu foncé (#1e3a8a)
- **Bordures** : Bleu
- **Tableau** : Alternance gris clair/blanc
- **Texte** : Noir

### Polices
- **Titres** : Helvetica-Bold
- **Corps** : Helvetica
- **Pied de page** : Helvetica-Oblique

### Mise en page
- **Format** : A4 (210 x 297 mm)
- **Marges** : 50 points (≈ 1.76 cm)
- **Espacements** : Aérés et professionnels

---

## ⚠️ Notes Importantes

### 1. Photo à coller
Le PDF contient un cadre vide. L'étudiant doit :
- Imprimer la fiche
- Coller sa photo d'identité dans le cadre
- Signer le document

### 2. Mise à jour
Si l'étudiant modifie ses UE :
- Télécharger une nouvelle fiche
- La nouvelle fiche remplace l'ancienne

### 3. Document officiel
- À conserver précieusement
- Nécessaire pour l'inscription administrative
- Peut être demandé par l'administration

---

## 🚀 Améliorations Futures (Optionnel)

### 1. Photo uploadée
```python
# Récupérer la photo depuis le profil
if etudiant.photo_url:
    img = ImageReader(etudiant.photo_url)
    c.drawImage(img, photo_x, photo_y, photo_size, photo_size)
```

### 2. QR Code
```python
# Ajouter un QR code pour vérification
import qrcode
qr_data = f"ETU-{etudiant.id}-{datetime.now().year}"
# Générer et ajouter au PDF
```

### 3. Code-barres
```python
# Code-barres du matricule
from reportlab.graphics.barcode import code128
barcode = code128.Code128(etudiant.matricule)
```

---

**Date** : 13 Février 2026  
**Version** : 3.2.2  
**Status** : ✅ FONCTIONNEL

🎉 **La fiche d'inscription UE avec photo est maintenant opérationnelle !**

