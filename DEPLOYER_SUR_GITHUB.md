# 📤 Mettre votre projet sur GitHub et le déployer
## Étape 1 : Préparer Git (si pas déjà fait)
```bash
cd /home/kstar-de-la-kartz/PycharmProjects/PythonProject3
# Initialiser Git
git init
# Vérifier le statut
git status
```
## Étape 2 : Ajouter tous les fichiers
```bash
# Ajouter tous les fichiers (le .gitignore exclura automatiquement les fichiers inutiles)
git add .
# Vérifier ce qui sera commité
git status
# Faire le premier commit
git commit -m "🎓 Initial commit - Système de gestion académique complet"
```
## Étape 3 : Créer un repository sur GitHub
### Via le navigateur :
1. **Allez sur** https://github.com
2. **Cliquez** sur le bouton `+` en haut à droite
3. **Sélectionnez** "New repository"
4. **Remplissez** :
   - **Repository name** : `academique-polytech` (ou autre nom)
   - **Description** : "Système de gestion académique pour établissements d'enseignement supérieur"
   - **Visibilité** : 
     - ✅ **Public** - Si vous voulez partager
     - ✅ **Private** - Si vous voulez garder privé
   - ⚠️ **NE cochez PAS** "Initialize this repository with a README"
5. **Cliquez** sur "Create repository"
## Étape 4 : Connecter votre projet local à GitHub
GitHub vous affichera des commandes. Copiez-collez dans votre terminal :
```bash
# Remplacez 'votre-username' et 'academique-polytech' par vos valeurs
git remote add origin https://github.com/votre-username/academique-polytech.git
# Renommer la branche en 'main' (standard GitHub)
git branch -M main
# Pousser votre code
git push -u origin main
```
### Si demandé, authentifiez-vous :
**Option A : Avec token GitHub (recommandé)**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Cochez `repo` (accès complet aux repositories)
4. Générez et copiez le token
5. Utilisez-le comme mot de passe lors du push
**Option B : Avec SSH**
```bash
# Générer une clé SSH
ssh-keygen -t ed25519 -C "votre-email@example.com"
# Copier la clé publique
cat ~/.ssh/id_ed25519.pub
# Ajouter sur GitHub : Settings → SSH and GPG keys → New SSH key
# Puis modifier l'URL remote:
git remote set-url origin git@github.com:votre-username/academique-polytech.git
```
## Étape 5 : Vérifier que le code est en ligne
1. Rafraîchissez votre page GitHub
2. Vous devriez voir tous vos fichiers !
3. Le README.md s'affichera automatiquement en page d'accueil
## Étape 6 : Déployer sur Render.com
Maintenant que votre code est sur GitHub, suivez le guide **DEPLOY_RENDER.md** qui vous guidera étape par étape pour mettre votre site en ligne gratuitement !
```bash
# Ouvrir le guide
cat DEPLOY_RENDER.md
```
## 🔄 Mises à jour futures
Chaque fois que vous modifiez votre code :
```bash
# Voir les changements
git status
# Ajouter les changements
git add .
# Commiter avec un message descriptif
git commit -m "✨ Ajout de la fonctionnalité X"
# Pousser sur GitHub
git push
# Si déployé sur Render, il redéploiera automatiquement ! 🎉
```
## 📝 Messages de commit recommandés
```bash
git commit -m "✨ Ajout d'une nouvelle fonctionnalité"
git commit -m "🐛 Correction du bug X"
git commit -m "🎨 Amélioration de l'interface"
git commit -m "📝 Mise à jour de la documentation"
git commit -m "🚀 Optimisation des performances"
git commit -m "🔒 Amélioration de la sécurité"
git commit -m "♻️ Refactorisation du code"
```
## 🎯 Résumé rapide
```bash
# 1. Initialiser et commit
git init
git add .
git commit -m "🎓 Initial commit"
# 2. Connecter à GitHub
git remote add origin https://github.com/VOTRE-USERNAME/VOTRE-REPO.git
git branch -M main
git push -u origin main
# 3. Déployer (voir DEPLOY_RENDER.md)
# → Render.com détectera automatiquement votre code !
```
## ✅ Checklist avant de pousser
- [ ] Vérifier que .gitignore est présent
- [ ] Vérifier que les fichiers secrets ne sont pas inclus
- [ ] Tester que l'application fonctionne localement
- [ ] Relire le README.md
- [ ] S'assurer que requirements.txt est à jour
## 🆘 Problèmes courants
### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/votre-username/votre-repo.git
```
### "Permission denied"
→ Vérifiez vos identifiants GitHub ou utilisez un token d'accès
### "Repository not found"
→ Vérifiez l'URL du repository et vos permissions
### Fichiers volumineux rejetés
```bash
# Supprimer le fichier du commit
git rm --cached fichier-volumineux
git commit --amend
```
## 🎉 Félicitations !
Votre code est maintenant sauvegardé sur GitHub et prêt à être déployé ! 
**Prochaine étape** : Lisez `DEPLOY_RENDER.md` pour mettre votre site en ligne en 15 minutes ! 🚀
