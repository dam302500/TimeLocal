#!/bin/bash

echo "🚀 Installation de TimeLocal pour Hostinger..."

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_requirements() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION 3.8" | awk '{print ($1 < $2)}') )); then
        log_error "Python 3.8+ requis, version détectée: $PYTHON_VERSION"
        exit 1
    fi
    
    log_info "Python $PYTHON_VERSION détecté ✓"
    
    # Vérifier pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 n'est pas installé"
        exit 1
    fi
    
    log_info "pip3 détecté ✓"
}

# Création de l'environnement virtuel
setup_venv() {
    log_info "Création de l'environnement virtuel Python..."
    
    cd "$(dirname "$0")/../app" || exit 1
    
    # Supprimer l'ancien venv s'il existe
    if [ -d "venv" ]; then
        log_warn "Suppression de l'ancien environnement virtuel..."
        rm -rf venv
    fi
    
    # Créer le nouvel environnement
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        log_error "Impossible de créer l'environnement virtuel"
        exit 1
    fi
    
    log_info "Environnement virtuel créé ✓"
}

# Activation de l'environnement virtuel
activate_venv() {
    log_info "Activation de l'environnement virtuel..."
    
    source venv/bin/activate
    
    if [ $? -ne 0 ]; then
        log_error "Impossible d'activer l'environnement virtuel"
        exit 1
    fi
    
    log_info "Environnement virtuel activé ✓"
}

# Installation des dépendances
install_dependencies() {
    log_info "Installation des dépendances Python..."
    
    # Mise à jour pip
    pip install --upgrade pip
    
    # Installation des dépendances
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        log_error "Échec de l'installation des dépendances"
        exit 1
    fi
    
    log_info "Dépendances installées ✓"
}

# Génération de la clé secrète
generate_secret_key() {
    log_info "Génération de la clé secrète..."
    
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    echo "SECRET_KEY=$SECRET_KEY" > .env.tmp
    
    log_info "Clé secrète générée ✓"
}

# Création du fichier .env
create_env_file() {
    log_info "Création du fichier de configuration .env..."
    
    cat > .env << EOL
# Configuration TimeLocal
SECRET_KEY=$(cat .env.tmp)
DATABASE_PATH=timelocal.db

# Application
APP_URL=https://$(hostname -f)
FLASK_CONFIG=production
FLASK_DEBUG=False

# Base de données
DATABASE_URL=sqlite:///timelocal.db

# Stripe (à configurer)
STRIPE_PUBLIC_KEY=pk_test_your_public_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Twilio SMS (à configurer)
TWILIO_SID=your_twilio_sid_here
TWILIO_TOKEN=your_twilio_token_here
TWILIO_PHONE=+1234567890

# Email SMTP (à configurer)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=noreply@timelocal.com

# Google Maps (optionnel)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Configuration avancée
DEFAULT_RADIUS=5
MAX_RADIUS=50
POINTS_PER_HOUR=10
DAILY_MISSION_REFRESH_HOUR=9

# Sécurité
SESSION_COOKIE_SECURE=True
CORS_ORIGINS=https://$(hostname -f)

# Rate limiting
RATELIMIT_DEFAULT=100 per hour

# Logging
LOG_LEVEL=INFO
LOG_FILE=timelocal.log
EOL
    
    rm .env.tmp
    
    # Sécuriser le fichier .env
    chmod 600 .env
    
    log_info "Fichier .env créé ✓"
}

# Initialisation de la base de données
init_database() {
    log_info "Initialisation de la base de données..."
    
    python3 -c "
from app import create_app
app, socketio = create_app('production')
with app.app_context():
    print('Base de données initialisée avec succès')
"
    
    if [ $? -ne 0 ]; then
        log_error "Échec de l'initialisation de la base de données"
        exit 1
    fi
    
    log_info "Base de données initialisée ✓"
}

# Création des dossiers nécessaires
create_directories() {
    log_info "Création des dossiers nécessaires..."
    
    mkdir -p uploads/{profiles,documents,images}
    mkdir -p logs
    mkdir -p backups
    
    # Permissions
    chmod 755 uploads
    chmod 755 logs
    chmod 755 backups
    
    log_info "Dossiers créés ✓"
}

# Test de l'installation
test_installation() {
    log_info "Test de l'installation..."
    
    # Test de démarrage de l'application
    timeout 10s python3 -c "
from app import create_app
import sys
try:
    app, socketio = create_app('production')
    print('Application démarrée avec succès')
    sys.exit(0)
except Exception as e:
    print(f'Erreur: {e}')
    sys.exit(1)
" &> /dev/null
    
    if [ $? -eq 0 ]; then
        log_info "Test d'installation réussi ✓"
    else
        log_error "Test d'installation échoué"
        exit 1
    fi
}

# Génération du script de démarrage
create_start_script() {
    log_info "Création du script de démarrage..."
    
    cat > start_timelocal.sh << 'EOL'
#!/bin/bash

# Script de démarrage TimeLocal
cd "$(dirname "$0")"

# Activer l'environnement virtuel
source venv/bin/activate

# Variables d'environnement
export FLASK_CONFIG=production
export PYTHONPATH=$PWD:$PYTHONPATH

# Démarrage avec Gunicorn
exec gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    --worker-class eventlet \
    --worker-connections 1000 \
    --timeout 120 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --pid timelocal.pid \
    --daemon \
    app:app
EOL
    
    chmod +x start_timelocal.sh
    
    log_info "Script de démarrage créé ✓"
}

# Génération du script d'arrêt
create_stop_script() {
    log_info "Création du script d'arrêt..."
    
    cat > stop_timelocal.sh << 'EOL'
#!/bin/bash

# Script d'arrêt TimeLocal
cd "$(dirname "$0")"

if [ -f timelocal.pid ]; then
    PID=$(cat timelocal.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Arrêt de TimeLocal (PID: $PID)..."
        kill $PID
        rm -f timelocal.pid
        echo "TimeLocal arrêté ✓"
    else
        echo "Processus TimeLocal introuvable"
        rm -f timelocal.pid
    fi
else
    echo "Fichier PID introuvable"
    # Essayer de tuer par nom
    pkill -f "gunicorn.*app:app"
fi
EOL
    
    chmod +x stop_timelocal.sh
    
    log_info "Script d'arrêt créé ✓"
}

# Script de backup
create_backup_script() {
    log_info "Création du script de backup..."
    
    cat > backup_timelocal.sh << 'EOL'
#!/bin/bash

# Script de backup TimeLocal
cd "$(dirname "$0")"

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_FILE="timelocal_backup_$DATE.tar.gz"

echo "Création du backup: $BACKUP_FILE"

# Arrêter l'application
./stop_timelocal.sh

# Créer l'archive
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='backups' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    .

# Redémarrer l'application
./start_timelocal.sh

echo "Backup créé: $BACKUP_DIR/$BACKUP_FILE"

# Nettoyer les anciens backups (garder les 7 derniers)
cd "$BACKUP_DIR"
ls -t timelocal_backup_*.tar.gz | tail -n +8 | xargs -r rm --

echo "Backup terminé ✓"
EOL
    
    chmod +x backup_timelocal.sh
    
    log_info "Script de backup créé ✓"
}

# Affichage des instructions finales
show_final_instructions() {
    echo ""
    echo "=============================================="
    echo "🎉 Installation de TimeLocal terminée !"
    echo "=============================================="
    echo ""
    log_info "📋 Étapes suivantes :"
    echo ""
    echo "1. 🔑 Configurer les clés API dans le fichier .env :"
    echo "   - Stripe (paiements)"
    echo "   - Twilio (SMS)"
    echo "   - Email SMTP"
    echo "   - Google Maps (optionnel)"
    echo ""
    echo "2. 🚀 Démarrer l'application :"
    echo "   ./start_timelocal.sh"
    echo ""
    echo "3. 🛑 Arrêter l'application :"
    echo "   ./stop_timelocal.sh"
    echo ""
    echo "4. 💾 Créer un backup :"
    echo "   ./backup_timelocal.sh"
    echo ""
    echo "5. 📊 Monitoring :"
    echo "   - Logs : tail -f logs/error.log"
    echo "   - Status : http://localhost:5000/health"
    echo ""
    echo "6. 🌐 Configuration web serveur :"
    echo "   - Configurer Apache/Nginx pour rediriger vers localhost:5000"
    echo "   - Copier les fichiers public_html sur votre serveur web"
    echo ""
    log_warn "⚠️  N'oubliez pas de configurer vos clés API avant de démarrer !"
    echo ""
}

# Fonction principale
main() {
    echo "TimeLocal Setup Script v2.0.0"
    echo "=============================="
    echo ""
    
    check_requirements
    setup_venv
    activate_venv
    install_dependencies
    generate_secret_key
    create_env_file
    init_database
    create_directories
    test_installation
    create_start_script
    create_stop_script
    create_backup_script
    
    show_final_instructions
}

# Gestion des erreurs
set -e
trap 'log_error "Installation échouée à la ligne $LINENO"' ERR

# Lancement du script principal
main "$@"