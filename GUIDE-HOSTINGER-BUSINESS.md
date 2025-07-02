# 🚀 Guide Hostinger Business - TimeLocal

**Solution pour plan Business (sans SSH/Python)**

## 📋 Résumé de la solution

✅ **Interface web** → Votre Hostinger  
✅ **API Flask** → Service gratuit externe  
✅ **Base de données** → Incluse avec l'API  

## 🏗️ Étape 1 : Déployer l'API gratuitement

### **Option recommandée : Railway**

1. **Allez sur [railway.app](https://railway.app)**
2. **Cliquez "Start a New Project"**
3. **Connectez-vous avec GitHub** (ou créez un compte)
4. **Cliquez "Deploy from GitHub repo"**

### **Upload du code sur GitHub :**

**Si vous n'avez pas GitHub :**
1. Créez un compte sur [github.com](https://github.com)
2. Cliquez "New repository"
3. Nommez-le "timelocal-api"
4. Uploadez le dossier `app/` complet

**Railway va automatiquement :**
- ✅ Détecter que c'est du Python/Flask
- ✅ Installer les dépendances
- ✅ Créer la base de données
- ✅ Vous donner une URL (ex: `https://timelocal-api.up.railway.app`)

### **Alternative : Render.com**
1. Allez sur [render.com](https://render.com) 
2. "New Web Service"
3. Connectez GitHub
4. Sélectionnez votre repo
5. Render fait le reste automatiquement

**Vous obtenez une URL comme :**
```
https://timelocal-api.onrender.com
```

## 🌐 Étape 2 : Configurer Hostinger

### **1. Upload via File Manager Hostinger**
1. **Connectez-vous à hPanel**
2. **File Manager** → `/domains/votredomaine.com/public_html/`
3. **Uploadez tout le contenu de `public_html/`** :
   - `index.html`
   - `static/` (dossier complet)
   - `manifest.json`

### **2. Configurer .htaccess**
1. **Renommez** `.htaccess-hostinger` en `.htaccess`
2. **Éditez le fichier** et remplacez `YOUR_API_URL` par votre vraie URL

**Exemple :**
```apache
# AVANT
RewriteRule ^app/?(.*)$ https://YOUR_API_URL/$1 [P,L]

# APRÈS (avec Railway)
RewriteRule ^app/?(.*)$ https://timelocal-api.up.railway.app/$1 [P,L]
```

### **3. Configurer le JavaScript**
1. **Dans `static/js/`**, renommez `app-hostinger.js` en `app.js`
2. **Éditez** `app.js` ligne 7 :

```javascript
// AVANT
API_BASE: 'https://YOUR_API_URL',

// APRÈS (avec votre vraie URL)
API_BASE: 'https://timelocal-api.up.railway.app',
```

## ⚙️ Étape 3 : Configurer l'API externe

### **Variables d'environnement sur Railway/Render**

**Dans Railway :**
1. Allez dans votre projet
2. Onglet "Variables" 
3. Ajoutez ces variables :

```env
SECRET_KEY=votre-cle-secrete-tres-longue-ici
FLASK_CONFIG=production
DATABASE_URL=sqlite:///timelocal.db
APP_URL=https://votredomaine.com
CORS_ORIGINS=https://votredomaine.com
```

**Pour les paiements (optionnel au début) :**
```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### **Test de l'API**
Visitez : `https://votre-api-url/health`

Vous devriez voir :
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## 🧪 Étape 4 : Test complet

### **1. Test de l'interface**
- Allez sur `https://votredomaine.com`
- Vérifiez que la page s'affiche correctement
- Vous devriez voir un indicateur de connexion API

### **2. Test de l'application**
- Cliquez sur "Accéder à l'application"
- Vous devriez être redirigé vers l'API
- Créez un compte test

## 🔧 Dépannage

### **Erreur "API déconnectée"**
1. Vérifiez que votre API externe fonctionne
2. Vérifiez l'URL dans `.htaccess` et `app.js`
3. Vérifiez les CORS dans l'API

### **Erreur 500 sur Hostinger**
1. Vérifiez le fichier `.htaccess`
2. Consultez les logs dans hPanel → Error Logs

### **L'application ne charge pas**
1. Ouvrez la console navigateur (F12)
2. Vérifiez les erreurs JavaScript
3. Vérifiez l'URL de l'API

## 💰 Coûts (Gratuit pour commencer)

### **Railway (Gratuit)**
- ✅ 500 heures/mois gratuites
- ✅ Base de données SQLite incluse
- ✅ HTTPS automatique
- ✅ Déploiement automatique

### **Render (Gratuit)**
- ✅ Service web gratuit
- ✅ Auto-sleep après inactivité
- ✅ HTTPS inclus

### **Upgrade payant si nécessaire**
- Railway : $5/mois pour plus de ressources
- Render : $7/mois pour service toujours actif

## 📞 Support

**Si ça ne marche pas :**
1. Vérifiez chaque URL (API, .htaccess, JavaScript)
2. Consultez les logs d'erreur
3. Testez l'API directement dans le navigateur

**Liens utiles :**
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Hostinger Support](https://support.hostinger.com)

## 🎯 Checklist finale

- [ ] API déployée et fonctionnelle
- [ ] URL API notée et sauvegardée  
- [ ] Fichiers uploadés sur Hostinger
- [ ] `.htaccess` configuré avec la bonne URL
- [ ] `app.js` configuré avec la bonne URL
- [ ] Variables d'environnement configurées
- [ ] Test complet effectué
- [ ] Interface accessible sur votre domaine

**Une fois tout configuré, votre TimeLocal sera 100% fonctionnel !** 🎉