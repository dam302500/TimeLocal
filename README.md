# TimeLocal - Plateforme d'échange de temps et services

**Version 2.0** - Application web progressive pour l'échange de services entre voisins

## 🌟 Fonctionnalités

- **Échanges flexibles** : Temps, argent ou hybride
- **Géolocalisation** : Services dans un rayon configurable
- **Gamification** : Points, badges, missions quotidiennes
- **Chat temps réel** : WebSocket pour la communication
- **Paiements sécurisés** : Integration Stripe
- **PWA** : Application web progressive installable
- **Notifications** : SMS, email et push

## 📂 Structure du projet

```
timelocal/
├── public_html/          # Interface web statique
│   ├── index.html       # Page d'accueil
│   ├── .htaccess        # Configuration Apache
│   ├── manifest.json    # PWA manifest
│   └── static/          # CSS, JS, images
├── app/                 # Application Flask
│   ├── app.py          # Application principale
│   ├── config.py       # Configuration
│   ├── requirements.txt # Dépendances Python
│   └── timelocal.db    # Base de données SQLite
└── scripts/
    └── setup.sh        # Script d'installation
```

## 🚀 Installation rapide

### 1. Cloner ou télécharger le projet
```bash
git clone https://github.com/votrecompte/timelocal.git
cd timelocal
```

### 2. Lancer l'installation automatique
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Configurer les clés API
Éditer le fichier `app/.env` et configurer :
- Stripe (paiements)
- Twilio (SMS)
- Email SMTP
- Google Maps (optionnel)

### 4. Démarrer l'application
```bash
cd app
./start_timelocal.sh
```

## 🔧 Configuration manuelle

### Prérequis
- Python 3.8+
- pip3
- SQLite3

### Installation étape par étape

1. **Environnement virtuel**
```bash
cd app
python3 -m venv venv
source venv/bin/activate
```

2. **Dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration**
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

4. **Base de données**
```bash
python3 -c "from app import create_app; app, socketio = create_app(); print('DB initialized')"
```

5. **Démarrage**
```bash
python3 app.py
# ou avec Gunicorn en production:
gunicorn -w 4 --worker-class eventlet -b 0.0.0.0:5000 app:app
```

## 🌐 Déploiement Hostinger

### Configuration Apache (.htaccess)
Le fichier `.htaccess` est déjà configuré pour :
- Rediriger `/app` vers Flask (port 5000)
- Servir les fichiers statiques
- Compression et cache
- Headers de sécurité

### Structure pour Hostinger
```
public_html/              # Racine web Hostinger
├── index.html           # Page publique
├── .htaccess           # Configuration Apache
└── static/             # Assets statiques

app/ (hors public_html)  # Application Flask
├── app.py              # Serveur Python
├── venv/               # Environnement virtuel
└── timelocal.db        # Base de données
```

### Configuration serveur
1. **VPS/Cloud Hosting requis** (Python support)
2. **Supervisor** pour maintenir Flask actif
3. **Nginx/Apache** pour proxy vers Flask

## 🔐 Sécurité

### Variables d'environnement
- ✅ Toutes les clés sensibles dans `.env`
- ✅ `.env` exclu du versioning
- ✅ Génération automatique SECRET_KEY

### Web Security
- ✅ Headers de sécurité (CSP, XSS, etc.)
- ✅ Protection CSRF
- ✅ Rate limiting
- ✅ Validation des inputs
- ✅ Hachage sécurisé des mots de passe

## 📊 API Endpoints

### Authentification
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion
- `POST /auth/logout` - Déconnexion

### Utilisateurs
- `GET /users/profile` - Profil utilisateur
- `PUT /users/profile` - Modifier profil

### Demandes/Offres
- `GET /requests` - Liste des demandes
- `POST /requests` - Créer une demande

### WebSocket Events
- `connect` - Connexion temps réel
- `join_exchange` - Rejoindre un échange
- `send_message` - Envoyer un message

## 🛠️ Scripts de gestion

### Démarrage
```bash
./start_timelocal.sh
```

### Arrêt
```bash
./stop_timelocal.sh
```

### Backup
```bash
./backup_timelocal.sh
```

### Logs
```bash
tail -f logs/error.log
tail -f logs/access.log
```

## 📱 Progressive Web App (PWA)

L'application est configurée comme PWA :
- **Installable** sur mobile et desktop
- **Offline capable** (cache des assets)
- **Push notifications** (avec configuration)
- **App-like experience**

## 🎮 Gamification

### Système de points
- +10 points par heure d'échange
- Missions quotidiennes
- Badges d'accomplissement
- Niveaux utilisateur

### Missions quotidiennes
- Créer une demande
- Répondre à une offre
- Compléter un échange
- Évaluer un partenaire

## 🔄 API Tiers

### Stripe (Paiements)
- Paiements sécurisés
- Gestion des abonnements
- Webhooks pour synchronisation

### Twilio (SMS)
- Vérification téléphone
- Notifications urgentes
- Code de vérification

### Google Maps (Géolocalisation)
- Calcul de distances
- Géocodage d'adresses
- Cartes interactives

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Métriques
- Performance requests
- Erreurs applicatives
- Utilisation ressources
- Statistiques échanges

## 🐛 Dépannage

### Problèmes courants

**Port 5000 occupé**
```bash
sudo lsof -i :5000
sudo kill -9 [PID]
```

**Base de données corrompue**
```bash
rm timelocal.db
python3 -c "from app import init_db; init_db('timelocal.db')"
```

**Environnement virtuel**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Logs de debug
```bash
export FLASK_DEBUG=True
python3 app.py
```

## 🤝 Support

### Documentation
- [Configuration Hostinger](docs/hostinger.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)

### Contact
- Email: support@timelocal.com
- Issues: GitHub Issues
- Discord: [Community Server]

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

**TimeLocal v2.0** - Connectons les communautés locales ! 🏘️⏰