# 🔧 Correction : BuildError - Route affecter_ue_a_prof Manquante
## ❌ Problème
BuildError: Could not build url for endpoint 'directeur.affecter_ue_a_prof'
## ✅ Solutions
### 1. Route Créée dans /app/routes/directeur.py
- Nouvelle route: /ue/<ue_id>/affecter/<enseignant_id>
- Gère l'affectation d'un enseignant à une UE
- Vérifie les doublons et gère les erreurs
### 2. Template Corrigé dans /app/templates/directeur/detail_ue.html
- Formulaire mis à jour avec les 2 paramètres (ue_id, enseignant_id)
- Script JavaScript corrigé pour construire l'URL correcte
- Bouton de retrait d'enseignant corrigé (utilisait supprimer_ue!)
## 🎯 Résultat
✅ Page de détail UE fonctionnelle
✅ Affectation d'enseignant opérationnelle
✅ Retrait sécurisé sans supprimer l'UE
**Bug résolu !** 🚀
