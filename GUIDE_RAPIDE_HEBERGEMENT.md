# 🎯 GUIDE ULTRA-RAPIDE : HÉBERGER KSTARHOME EN 20 MINUTES

---

## 🚀 MÉTHODE RAPIDE (Pour les pressés)

Exécutez simplement cette commande dans votre terminal :

```bash
./heberger_kstarhome.sh
```

Le script fait TOUT automatiquement pour vous ! ✨

---

## 📖 MÉTHODE MANUELLE (Étape par étape)

### 🔹 ÉTAPE 1 : Préparer le code (5 min)

```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
git init
git add .
git commit -m "🎓 KstarHome - Premier commit"
```

---

### 🔹 ÉTAPE 2 : GitHub (5 min)

1. **Créer un compte sur GitHub**
   - Allez sur https://github.com
   - Cliquez sur "Sign up"
   - Remplissez le formulaire

2. **Créer un repository**
   - Cliquez sur "+" → "New repository"
   - Nom : `kstarhome`
   - Cliquez "Create repository"

3. **Envoyer le code**
   ```bash
   git remote add origin https://github.com/VOTRE-USERNAME/kstarhome.git
   git branch -M main
   git push -u origin main
   ```

⚠️ **Important** : GitHub demande un **token** (pas de mot de passe)
- Créez un token : Settings → Developer settings → Personal access tokens
- Cochez "repo"
- Utilisez-le comme mot de passe

---

### 🔹 ÉTAPE 3 : Render.com (8 min)

1. **Créer un compte**
   - Allez sur https://render.com
   - Connectez-vous avec GitHub

2. **Créer un Web Service**
   - Cliquez "New +" → "Web Service"
   - Sélectionnez votre repo "kstarhome"

3. **Configuration**
   ```
   Name: kstarhome
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn run:app
   Plan: Free (0€)
   ```

4. **Variables d'environnement** (cliquez "Advanced")
   ```
   FLASK_ENV = production
   DEBUG = False
   SECRET_KEY = [générez-en une - voir ci-dessous]
   ```

   Pour générer une SECRET_KEY :
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Créer le service**
   - Cliquez "Create Web Service"
   - Attendez 3-5 minutes

---

### 🔹 ÉTAPE 4 : Initialiser la base (2 min)

1. Dans Render, allez dans **Shell** (menu gauche)
2. Exécutez :
   ```bash
   python3 init_database.py
   ```
3. Attendez que ça se termine

---

## 🎉 TERMINÉ !

Votre site est en ligne sur :

### 🌐 https://kstarhome.onrender.com

**Connectez-vous avec :**
- Directeur : `directeur` / `directeur123`
- Enseignant : `prof` / `prof123`
- Étudiant : `etudiant` / `etudiant123`

---

## 🔄 Mises à jour futures

```bash
git add .
git commit -m "Nouvelle fonctionnalité"
git push
```

Render redéploiera automatiquement ! 🚀

---

## 🆘 Problèmes ?

### "Authentication failed" sur GitHub
→ Utilisez un **token** GitHub (pas de mot de passe)

### "Build failed" sur Render
→ Vérifiez que `requirements.txt` contient toutes les dépendances

### Site ne charge pas
→ Vérifiez que vous avez exécuté `python3 init_database.py` dans Shell Render

---

## 💡 Astuce

Pour un hébergement 100% automatique, utilisez le script :

```bash
./heberger_kstarhome.sh
```

Il gère tout pour vous ! ✨

---

**© 2026 KstarHome - Ing. KOISSI-ZO Tonyi Constantin**

