#!/usr/bin/env python3
"""
TimeLocal Flask Application - Version simplifiée pour Railway
"""

import os
import sqlite3
import json
from datetime import datetime
from functools import wraps
import hashlib
import random
import string

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration simple
class SimpleConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-railway-2024')
    DATABASE_PATH = 'timelocal.db'
    CORS_ORIGINS = ['*']  # Permissif pour les tests

# Création de l'app Flask
app = Flask(__name__)
app.config.from_object(SimpleConfig)

# CORS
CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

# Initialisation base de données
def init_db():
    """Initialise la base de données SQLite"""
    with sqlite3.connect(app.config['DATABASE_PATH']) as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                address TEXT,
                time_credits INTEGER DEFAULT 100,
                level TEXT DEFAULT 'new_user',
                points INTEGER DEFAULT 0,
                rating REAL DEFAULT 5.0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL,
                time_required INTEGER,
                price REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        ''')

def get_db():
    """Obtient une connexion à la base de données"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Décorateur pour vérifier la connexion utilisateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes principales
@app.route('/')
def index():
    """Page d'accueil de l'API"""
    return jsonify({
        'app': 'TimeLocal API',
        'version': '2.0.0',
        'status': 'running',
        'message': 'API déployée avec succès sur Railway!',
        'endpoints': {
            'health': '/health',
            'register': '/auth/register',
            'login': '/auth/login',
            'requests': '/requests'
        }
    })

@app.route('/health')
def health():
    """Endpoint de santé pour Railway"""
    try:
        # Test de connexion à la base de données
        with get_db() as conn:
            conn.execute('SELECT 1').fetchone()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'railway': 'ok'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Routes d'authentification
@app.route('/auth/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Validation des données
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email et password requis'}), 400
        
        with get_db() as conn:
            # Vérifier si l'utilisateur existe déjà
            existing = conn.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (data['username'], data['email'])
            ).fetchone()
            
            if existing:
                return jsonify({'error': 'Utilisateur déjà existant'}), 409
            
            # Créer l'utilisateur
            password_hash = generate_password_hash(data['password'])
            cursor = conn.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', (
                data['username'],
                data['email'],
                password_hash,
                data.get('full_name', data['username'])
            ))
            
            user_id = cursor.lastrowid
            
            # Créer une session
            session['user_id'] = user_id
            session['username'] = data['username']
            
            return jsonify({
                'message': 'Utilisateur créé avec succès',
                'user_id': user_id,
                'username': data['username']
            }), 201
            
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Connexion utilisateur"""
    try:
        data = request.get_json() if request.is_json else {}
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email et password requis'}), 400
        
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE email = ? AND is_active = TRUE',
                (data['email'],)
            ).fetchone()
            
            if not user or not check_password_hash(user['password_hash'], data['password']):
                return jsonify({'error': 'Identifiants invalides'}), 401
            
            # Créer une session
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            return jsonify({
                'message': 'Connexion réussie',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'time_credits': user['time_credits'],
                    'points': user['points'],
                    'level': user['level']
                }
            })
            
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """Déconnexion utilisateur"""
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'})

# Routes des demandes
@app.route('/requests', methods=['GET'])
def get_requests():
    """Obtenir les demandes/offres"""
    try:
        with get_db() as conn:
            requests = conn.execute('''
                SELECT r.*, u.username, u.full_name, u.rating
                FROM requests r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'active'
                ORDER BY r.created_at DESC
                LIMIT 20
            ''').fetchall()
            
            return jsonify({
                'requests': [dict(req) for req in requests],
                'count': len(requests)
            })
            
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@app.route('/requests', methods=['POST'])
@login_required
def create_request():
    """Créer une nouvelle demande/offre"""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Validation des données
        required_fields = ['title', 'description', 'category', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} requis'}), 400
        
        with get_db() as conn:
            cursor = conn.execute('''
                INSERT INTO requests (
                    user_id, title, description, category, type, 
                    time_required, price
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                data['title'],
                data['description'],
                data['category'],
                data['type'],
                data.get('time_required', 60),
                data.get('price', 0)
            ))
            
            request_id = cursor.lastrowid
            
            return jsonify({
                'message': 'Demande créée avec succès',
                'request_id': request_id
            }), 201
            
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

# Test endpoint
@app.route('/test', methods=['GET', 'POST'])
def test():
    """Endpoint de test"""
    return jsonify({
        'message': 'Test OK',
        'method': request.method,
        'railway_deployment': 'success',
        'timestamp': datetime.utcnow().isoformat()
    })

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint non trouvé'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur interne du serveur'}), 500

# Initialisation
with app.app_context():
    init_db()

# Point d'entrée pour Railway/Gunicorn
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Export pour Gunicorn
application = app