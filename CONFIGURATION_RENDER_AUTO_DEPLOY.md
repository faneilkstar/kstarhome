# 🎯 CONFIGURATION RENDER - DÉPLOIEMENT AUTOMATIQUE

## 📅 Date : 12 Février 2026

---

## 🎯 OBJECTIF

Configurer Render pour qu'il redéploie **automatiquement** votre site à chaque push sur GitHub, **sans aucune action manuelle**.

---

## ✅ PRÉREQUIS

- ✅ Compte GitHub avec repository créé
- ✅ Compte Render.com créé
- ✅ Service Web Render déjà créé et lié à GitHub

---

## 🔧 CONFIGURATION ÉTAPE PAR ÉTAPE

### Étape 1 : Activer l'Auto-Deploy sur Render

1. **Connectez-vous à Render** : https://dashboard.render.com

2. **Sélectionnez votre service** (K-Star Home)

3. **Allez dans Settings** (Paramètres)

4. **Section "Build & Deploy"**

5. **Trouvez "Auto-Deploy"**

   ```
   Auto-Deploy: [Sélecteur]
   └─ Yes ✅ (Sélectionner cette option)
   ```

6. **Branch** : Assurez-vous que c'est `main`

   ```
   Branch: [main]
   ```

7. **Cliquez sur "Save Changes"**

✅ **C'est tout !** L'auto-deploy est maintenant activé.

---

## 🧪 TESTER L'AUTO-DEPLOY

### Test rapide :

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3

# Modifier un fichier (par ex. README)
echo "# Test auto-deploy" >> README.md

# Déployer avec le script
./deploy_quick.sh "🧪 Test auto-deploy"

# Attendre 30 secondes puis vérifier sur Render Dashboard
```

### Sur Render Dashboard :

1. **Aller dans "Events"**
2. Vous devriez voir :
   ```
   🟡 Deploy started (par GitHub push)
   ⏱️ Building...
   ```

3. Après 3-5 minutes :
   ```
   🟢 Deploy live
   ```

✅ **Succès !** L'auto-deploy fonctionne.

---

## 🔑 (OPTIONNEL) Deploy Hook pour GitHub Actions

Si vous voulez déclencher manuellement depuis GitHub Actions :

### Sur Render :

1. **Settings → Deploy Hook**
2. **Créer un Deploy Hook**
3. **Copier l'URL** (par ex. `https://api.render.com/deploy/srv-xxx?key=yyy`)

### Sur GitHub :

1. **Votre repository → Settings**
2. **Secrets and variables → Actions**
3. **New repository secret**
   - Name : `RENDER_DEPLOY_HOOK`
   - Value : `[Coller l'URL du Deploy Hook]`
4. **Add secret**

✅ Maintenant GitHub Actions peut déclencher les déploiements.

---

## 📊 WORKFLOW FINAL

### Workflow automatique complet :

```
Vous : Modification du code
         ↓
    git add .
    git commit -m "..."
    git push origin main
         ↓
GitHub : Reçoit le push
         ↓
    [SI GitHub Actions activé]
    → Tests automatiques
    → Validation du code
         ↓
Render : Détecte le push (Auto-Deploy)
         ↓
    1. Clone le nouveau code
    2. pip install -r requirements.txt
    3. Build l'application
    4. Tests de santé
    5. Déploiement en production
         ↓
🎉 Site mis à jour ! (3-5 minutes)
```

---

## 🎨 PERSONNALISATION DU BUILD

### Variables d'environnement sur Render :

**Settings → Environment**

Ajouter les variables nécessaires :

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=votre_secret_tres_long_et_complexe

# IA Gemini (optionnel)
GEMINI_API_KEY=votre_cle_api_gemini

# Base de données (Render la crée automatiquement)
DATABASE_URL=[Auto-généré par Render]
```

**Important** : Cliquer sur "Save Changes" après chaque ajout.

---

## 🔍 VÉRIFIER QUE L'AUTO-DEPLOY EST ACTIF

### Méthode 1 : Via Dashboard

```
Render Dashboard
→ Votre Service
→ Settings
→ Build & Deploy
→ Auto-Deploy: Should show "Yes" ✅
```

### Méthode 2 : Via un test

```bash
# Faire une modification mineure
echo "<!-- Test -->" >> app/templates/base.html

# Push
git add .
git commit -m "Test auto-deploy"
git push origin main

# Attendre 1 minute
# Aller sur Render → Events
# Vous devriez voir un nouveau deploy en cours
```

---

## 🐛 DÉPANNAGE

### Problème 1 : "Auto-Deploy ne se déclenche pas"

**Vérifier** :
- [ ] Auto-Deploy est bien sur "Yes"
- [ ] Branch est bien "main"
- [ ] Le repository GitHub est bien lié

**Solution** :
```
Settings → Build & Deploy
→ Reconnecter le repository GitHub si nécessaire
```

---

### Problème 2 : "Build Failed"

**Causes fréquentes** :
1. Erreur de syntaxe Python
2. Dépendance manquante dans `requirements.txt`
3. Variable d'environnement manquante

**Solution** :
```bash
# Tester localement d'abord
python3 run.py

# Vérifier requirements.txt
pip freeze > requirements.txt

# Vérifier les variables d'environnement sur Render
```

---

### Problème 3 : "Deploy réussi mais site ne fonctionne pas"

**Vérifier les logs** :
```
Render Dashboard → Logs
→ Chercher les erreurs dans les logs
```

**Causes fréquentes** :
- Variable d'environnement manquante
- Port incorrect (doit être celui de Render)
- Base de données non migrée

**Solution** :
```python
# Dans run.py, utiliser le port de Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

## 📈 MONITORING

### Surveiller vos déploiements :

1. **Events Tab** : Historique de tous les déploiements
   - 🟢 Réussis
   - 🔴 Échoués
   - 🟡 En cours

2. **Logs Tab** : Logs en temps réel
   - Utile pour déboguer

3. **Metrics Tab** : Performance
   - CPU usage
   - Memory usage
   - Request count

---

## 🔔 NOTIFICATIONS (Optionnel)

### Recevoir des alertes par email :

1. **Settings → Notifications**
2. **Cocher** :
   - ✅ Deploy Started
   - ✅ Deploy Succeeded
   - ✅ Deploy Failed
3. **Save**

Vous recevrez un email à chaque déploiement ! 📧

---

## 🎯 BONNES PRATIQUES

### 1. Toujours tester localement avant de push

```bash
python3 run.py
# Tester le site sur localhost:5000
# Si OK, alors push
```

### 2. Utiliser des messages de commit clairs

```bash
# ✅ BON
git commit -m "🔧 Fix: Correction du bug laboratoire"

# ❌ MAUVAIS
git commit -m "fix"
```

### 3. Faire des commits petits et fréquents

Plutôt que 1 gros commit de 50 fichiers, faire 5 commits de 10 fichiers chacun.

### 4. Utiliser le script deploy_quick.sh

```bash
# Plus rapide et plus sûr
./deploy_quick.sh "Mon message"
```

---

## ✅ CHECKLIST FINALE

Configuration Render pour auto-deploy :

- [ ] ✅ Auto-Deploy activé (Settings → Build & Deploy → Auto-Deploy: Yes)
- [ ] ✅ Branch correcte (main)
- [ ] ✅ Variables d'environnement configurées
- [ ] ✅ Repository GitHub lié
- [ ] ✅ Premier déploiement réussi
- [ ] ✅ Test d'auto-deploy effectué
- [ ] ✅ Notifications configurées (optionnel)

---

## 🎉 RÉSULTAT

**Avant** :
1. Modifier le code
2. Ouvrir Render Dashboard
3. Cliquer sur "Manual Deploy"
4. Attendre...
5. Vérifier le déploiement

**Après** :
1. Modifier le code
2. `./deploy_quick.sh "Mon message"`
3. ☕ Café (le site se met à jour tout seul)

**Gain de temps** : ~5 minutes par déploiement

---

## 📞 SUPPORT

En cas de problème :

1. **Documentation Render** : https://render.com/docs/deploys
2. **Support Render** : https://render.com/support
3. **Logs de votre service** : Dashboard → Logs

---

**🎓 Ing. KOISSI-ZO Tonyi Constantin**  
**📅 12 Février 2026**

---

**🚀 Votre système est maintenant en pilote automatique ! 🚀**

