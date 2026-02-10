# 🎯 MÉTHODE RAPIDE : HÉBERGER KSTARHOME EN 10 MINUTES

---

## ⚠️ POURQUOI PAS GITHUB PAGES ?

**GitHub Pages** = Sites statiques seulement (HTML/CSS/JS pur)  
**KstarHome** = Application Flask (Python) avec base de données

➡️ **Vous devez utiliser Render.com** (gratuit, supporte Python)

---

## 🚀 MÉTHODE AUTOMATIQUE (Recommandée)

Ouvrez un terminal et exécutez :

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
./deployer_kstarhome.sh
```

Le script fait TOUT pour vous ! ✨

---

## 📖 MÉTHODE MANUELLE (Si le script ne marche pas)

### Étape 1 : GitHub (3 minutes)

```bash
# Terminal
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
git init
git add .
git commit -m "🎓 KstarHome by Ing. KOISSI-ZO Tonyi Constantin"
```

**Sur GitHub** (https://github.com) :
1. Cliquez **"New repository"** (bouton vert)
2. Nom : `kstarhome`
3. Public ✅
4. **Ne cochez RIEN d'autre**
5. Cliquez **"Create repository"**

```bash
# Remplacez VOTRE_USERNAME par votre nom GitHub
git remote add origin https://github.com/VOTRE_USERNAME/kstarhome.git
git branch -M main
git push -u origin main
```

**⚠️ GitHub demandera un TOKEN** (pas un mot de passe) :
- GitHub → Settings → Developer settings → Personal access tokens
- Generate new token → Cochez "repo" → Copy token
- Utilisez ce token comme mot de passe dans le terminal

---

### Étape 2 : Render.com (5 minutes)

1. **Allez sur** : https://render.com
2. **Cliquez** : "Get Started for Free"
3. **Connectez avec GitHub**

4. **Créez un Web Service** :
   - Dashboard → **"New +"** → **"Web Service"**
   - Sélectionnez votre repo **kstarhome**

5. **Configuration** :
   ```
   Name:           kstarhome
   Runtime:        Python 3
   Build Command:  pip install -r requirements.txt
   Start Command:  gunicorn run:app --bind 0.0.0.0:$PORT
   Instance Type:  Free
   ```

6. **Variables d'environnement** (cliquez "Advanced") :
   
   Ajoutez ces 3 variables :
   
   | Clé | Valeur |
   |-----|--------|
   | `FLASK_ENV` | `production` |
   | `DEBUG` | `False` |
   | `SECRET_KEY` | [Générez-en une ci-dessous] |

   **Pour générer une SECRET_KEY** :
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copiez le résultat

7. **Cliquez** : "Create Web Service"
   - ⏳ Attendez 3-5 minutes

---

### Étape 3 : Base de données (1 minute)

Une fois déployé :

1. Dans Render, **onglet "Shell"** (menu gauche)
2. Exécutez :
   ```bash
   python init_database.py
   ```
3. Attendez le "✅ Base de données initialisée"

---

## 🎉 TERMINÉ !

Votre site est en ligne sur :

### 🌐 https://kstarhome.onrender.com

**Connexion** :
- Directeur : `admin` / `admin123`

---

## 🔄 Mettre à jour le site

Chaque fois que vous modifiez le code :

```bash
git add .
git commit -m "Description des modifications"
git push
```

Render redéploie automatiquement ! 🚀

---

## 🆘 PROBLÈMES ?

### "Authentication failed" sur git push
➡️ Utilisez un **Personal Access Token** GitHub (pas votre mot de passe)

### "Build failed" sur Render
➡️ Vérifiez que `gunicorn` est dans `requirements.txt`

### Site affiche une erreur
➡️ Vérifiez les logs dans Render (onglet "Logs")

---

## 📞 SUPPORT

- Guide complet : `HEBERGEMENT_GITHUB_RENDER.md`
- Script automatique : `./deployer_kstarhome.sh`

---

**© 2026 KstarHome - Ing. KOISSI-ZO Tonyi Constantin**  
**Spécialiste en Électronique de Puissance**

