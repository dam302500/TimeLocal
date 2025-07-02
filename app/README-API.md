# TimeLocal API - Déploiement Cloud

## 🚀 Déploiement rapide

### Railway (Recommandé)
1. Fork ce repo sur GitHub
2. Connectez Railway à votre GitHub
3. Sélectionnez ce repo
4. Railway détecte automatiquement Flask
5. Configurez les variables d'environnement

### Render
1. Créez un Web Service sur Render
2. Connectez votre repo GitHub
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn -w 4 --worker-class eventlet -b 0.0.0.0:$PORT app:app`

### Heroku
```bash
heroku create votre-app-name
git push heroku main
```

## ⚙️ Variables d'environnement requises

### Minimum viable
```env
SECRET_KEY=your-secret-key-here
FLASK_CONFIG=production
DATABASE_URL=sqlite:///timelocal.db
PORT=5000
```

### Production complète
```env
# Sécurité
SECRET_KEY=your-very-long-secret-key
FLASK_CONFIG=production

# Base de données
DATABASE_URL=sqlite:///timelocal.db

# CORS (remplacez par votre domaine)
CORS_ORIGINS=https://votredomaine.com
APP_URL=https://votredomaine.com

# Stripe (optionnel)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# Email (optionnel)
MAIL_USERNAME=noreply@votredomaine.com
MAIL_PASSWORD=your-app-password
```

## 🧪 Test de l'API

Une fois déployée, testez :
```
GET https://votre-api-url/health
```

Réponse attendue :
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## 📊 Endpoints disponibles

- `GET /` - Info API
- `GET /health` - Health check
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion
- `GET /requests` - Liste des demandes
- WebSocket sur `/socket.io`

## 🔒 Sécurité

✅ Headers de sécurité configurés  
✅ CORS configuré  
✅ Rate limiting  
✅ Validation des inputs  
✅ Hachage sécurisé des mots de passe  

## 📈 Monitoring

### Health Check
```bash
curl https://votre-api-url/health
```

### Logs (Railway/Render)
- Consultez les logs dans le dashboard
- Erreurs automatiquement tracées

## 🔄 Mise à jour

### Déploiement automatique
- Push sur GitHub → Déploiement automatique
- Railway/Render rebuild automatiquement

### Migration base de données
Les migrations sont automatiques au démarrage.

## 💰 Coûts estimés

### Gratuit
- **Railway**: 500h/mois gratuit
- **Render**: Service gratuit avec limitations
- **Heroku**: 550h/mois gratuit (legacy)

### Payant
- **Railway**: $5/mois (recommandé)
- **Render**: $7/mois
- **Heroku**: $7/mois

## 🆘 Dépannage

### Erreur de build
1. Vérifiez `requirements.txt`
2. Vérifiez `runtime.txt` (Python version)
3. Consultez les logs de build

### Erreur de démarrage
1. Vérifiez les variables d'environnement
2. Vérifiez le Procfile
3. Consultez les logs d'application

### Base de données
1. L'API crée automatiquement les tables
2. SQLite est persistant sur Railway/Render
3. Pour PostgreSQL, utilisez DATABASE_URL complet

## 📞 Support

- Railway: [docs.railway.app](https://docs.railway.app)
- Render: [render.com/docs](https://render.com/docs)
- Issues: GitHub Issues de ce repo