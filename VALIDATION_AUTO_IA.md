# 🤖 Système de Validation Automatique des Inscriptions

## Fonctionnement

### 1. Validation Manuelle (Directeur)
Le directeur peut valider ou refuser manuellement les inscriptions depuis l'interface web.

### 2. Validation Automatique par IA (48h)
Si le directeur ne traite pas une inscription sous **48 heures**, l'IA la valide automatiquement selon les critères suivants :

- ✅ **ACCEPTÉ** : Moyenne ≥ 12/20
- ❌ **REFUSÉ** : Moyenne < 12/20

## Configuration

### Champs ajoutés pour les enseignants :
- Date de naissance ✅
- Sexe ✅  
- Téléphone ✅
- Adresse ✅

Ces champs sont maintenant obligatoires lors de la création d'un enseignant.

## Lancement du Script de Validation Auto

### Manuellement
```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
source venv/bin/activate
python validation_auto_inscriptions.py
```

### Avec Cron (Automatique)
Pour exécuter le script automatiquement tous les jours à 2h du matin :

```bash
crontab -e
```

Ajouter cette ligne :
```
0 2 * * * cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3 && /home/kstar-de-la-kartz/PycharmProjects/PythonProject3/venv/bin/python validation_auto_inscriptions.py >> /tmp/validation_auto.log 2>&1
```

## Résultat

Le script affiche :
```
🤖 VALIDATION AUTOMATIQUE DES INSCRIPTIONS PAR IA
======================================================================

📋 5 inscription(s) en attente depuis plus de 48h

🔄 Traitement de DUPONT Jean... ✅ ACCEPTÉ (Score: 85/100)
🔄 Traitement de MARTIN Sophie... ✅ ACCEPTÉ (Score: 78/100)
🔄 Traitement de DURAND Paul... ❌ REFUSÉ (Moyenne insuffisante)
🔄 Traitement de BERNARD Marie... ✅ ACCEPTÉ (Score: 92/100)
🔄 Traitement de PETIT Lucas... ❌ REFUSÉ (Moyenne insuffisante)

======================================================================
📊 RÉSULTATS DE LA VALIDATION AUTOMATIQUE
======================================================================
✅ Acceptés : 3
❌ Refusés  : 2
⚠️  Erreurs  : 0
======================================================================
```

## Interface Directeur

Le directeur peut toujours :
1. Valider manuellement en masse : Bouton "Validation IA Auto" dans la liste des étudiants
2. Valider individuellement : Bouton "Valider" sur la fiche de l'étudiant

## Notes Techniques

- Le champ `date_inscription` est automatiquement rempli lors de l'inscription
- Le délai de 48h est paramétrable dans le script `validation_auto_inscriptions.py`
- L'IA Gemini est utilisée si la clé API est configurée, sinon le système utilise une validation basique par moyenne

