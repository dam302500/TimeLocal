#!/usr/bin/env python3
"""
TimeLocal Flask Application
Version web de l'application desktop TimeLocal
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from functools import wraps
import hashlib
import random
import string

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import config, Config

# Initialisation Flask
def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    
    # Extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    socketio = SocketIO(
        app,
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS']
    )
    
    # Initialisation base de données
    init_db(app.config['DATABASE_PATH'])
    
    return app, socketio

app, socketio = create_app()

# Utilitaires
def get_db():
    """Obtient une connexion à la base de données"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    """Initialise la base de données"""
    with sqlite3.connect(db_path) as conn:
        conn.executescript('''
            -- Table des utilisateurs
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                address TEXT,
                latitude REAL,
                longitude REAL,
                bio TEXT,
                skills TEXT,
                availability TEXT,
                time_credits INTEGER DEFAULT 100,
                level TEXT DEFAULT 'new_user',
                points INTEGER DEFAULT 0,
                rating REAL DEFAULT 5.0,
                rating_count INTEGER DEFAULT 0,
                profile_picture TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Table des demandes/offres
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL, -- 'request' ou 'offer'
                time_required INTEGER, -- en minutes
                price REAL DEFAULT 0,
                exchange_type TEXT DEFAULT 'time', -- 'time', 'money', 'hybrid'
                location TEXT,
                latitude REAL,
                longitude REAL,
                deadline TIMESTAMP,
                status TEXT DEFAULT 'active', -- 'active', 'completed', 'cancelled'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            -- Table des échanges
            CREATE TABLE IF NOT EXISTS exchanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                requester_id INTEGER NOT NULL,
                provider_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending', -- 'pending', 'accepted', 'in_progress', 'completed', 'disputed', 'cancelled'
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                time_spent INTEGER, -- en minutes
                amount_paid REAL DEFAULT 0,
                rating_requester INTEGER,
                rating_provider INTEGER,
                comment_requester TEXT,
                comment_provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES requests (id),
                FOREIGN KEY (requester_id) REFERENCES users (id),
                FOREIGN KEY (provider_id) REFERENCES users (id)
            );
            
            -- Table des messages
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text', -- 'text', 'image', 'file'
                file_path TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exchange_id) REFERENCES exchanges (id),
                FOREIGN KEY (sender_id) REFERENCES users (id)
            );
            
            -- Table des notifications
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                data TEXT, -- JSON data
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            -- Table des badges
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                criteria TEXT -- JSON criteria
            );
            
            -- Table des badges utilisateurs
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (badge_id) REFERENCES badges (id),
                UNIQUE(user_id, badge_id)
            );
            
            -- Table des missions quotidiennes
            CREATE TABLE IF NOT EXISTS daily_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mission_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                target_value INTEGER NOT NULL,
                current_value INTEGER DEFAULT 0,
                reward_points INTEGER DEFAULT 0,
                date DATE NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            -- Index pour les performances
            CREATE INDEX IF NOT EXISTS idx_users_location ON users(latitude, longitude);
            CREATE INDEX IF NOT EXISTS idx_requests_location ON requests(latitude, longitude);
            CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
            CREATE INDEX IF NOT EXISTS idx_exchanges_status ON exchanges(status);
            CREATE INDEX IF NOT EXISTS idx_messages_exchange ON messages(exchange_id);
            CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);
        ''')

def login_required(f):
    """Décorateur pour vérifier la connexion utilisateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def generate_token(length=32):
    """Génère un token aléatoire"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Routes principales
@app.route('/')
def index():
    """Page d'accueil de l'API"""
    return jsonify({
        'app': app.config['APP_NAME'],
        'version': app.config['APP_VERSION'],
        'status': 'running',
        'endpoints': {
            'auth': '/auth',
            'users': '/users',
            'requests': '/requests',
            'exchanges': '/exchanges',
            'messages': '/messages',
            'notifications': '/notifications'
        }
    })

@app.route('/health')
def health():
    """Endpoint de santé pour les vérifications"""
    try:
        # Test de connexion à la base de données
        with get_db() as conn:
            conn.execute('SELECT 1').fetchone()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
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
    data = request.get_json()
    
    # Validation des données
    required_fields = ['username', 'email', 'password', 'full_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        with get_db() as conn:
            # Vérifier si l'utilisateur existe déjà
            existing = conn.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (data['username'], data['email'])
            ).fetchone()
            
            if existing:
                return jsonify({'error': 'User already exists'}), 409
            
            # Créer l'utilisateur
            password_hash = generate_password_hash(data['password'])
            cursor = conn.execute('''
                INSERT INTO users (username, email, password_hash, full_name, phone, address, bio, skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['username'],
                data['email'],
                password_hash,
                data['full_name'],
                data.get('phone', ''),
                data.get('address', ''),
                data.get('bio', ''),
                data.get('skills', '')
            ))
            
            user_id = cursor.lastrowid
            
            # Créer une session
            session['user_id'] = user_id
            session['username'] = data['username']
            
            return jsonify({
                'message': 'User created successfully',
                'user_id': user_id
            }), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Connexion utilisateur"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE email = ? AND is_active = TRUE',
                (data['email'],)
            ).fetchone()
            
            if not user or not check_password_hash(user['password_hash'], data['password']):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Mise à jour de la dernière connexion
            conn.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'],)
            )
            
            # Créer une session
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'time_credits': user['time_credits'],
                    'points': user['points'],
                    'level': user['level'],
                    'rating': user['rating']
                }
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """Déconnexion utilisateur"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

# Routes utilisateurs
@app.route('/users/profile', methods=['GET'])
@login_required
def get_profile():
    """Obtenir le profil de l'utilisateur connecté"""
    try:
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (session['user_id'],)
            ).fetchone()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'user': dict(user)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/profile', methods=['PUT'])
@login_required
def update_profile():
    """Mettre à jour le profil utilisateur"""
    data = request.get_json()
    
    try:
        with get_db() as conn:
            # Champs modifiables
            updatable_fields = ['full_name', 'phone', 'address', 'bio', 'skills', 'availability']
            updates = []
            values = []
            
            for field in updatable_fields:
                if field in data:
                    updates.append(f'{field} = ?')
                    values.append(data[field])
            
            if updates:
                values.append(session['user_id'])
                conn.execute(f'''
                    UPDATE users 
                    SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', values)
            
            return jsonify({'message': 'Profile updated successfully'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes des demandes/offres
@app.route('/requests', methods=['GET'])
def get_requests():
    """Obtenir les demandes/offres"""
    try:
        with get_db() as conn:
            requests = conn.execute('''
                SELECT r.*, u.username, u.full_name, u.rating, u.profile_picture
                FROM requests r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'active'
                ORDER BY r.created_at DESC
                LIMIT 50
            ''').fetchall()
            
            return jsonify({
                'requests': [dict(req) for req in requests]
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/requests', methods=['POST'])
@login_required
def create_request():
    """Créer une nouvelle demande/offre"""
    data = request.get_json()
    
    required_fields = ['title', 'description', 'category', 'type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                INSERT INTO requests (
                    user_id, title, description, category, type, 
                    time_required, price, exchange_type, location,
                    latitude, longitude, deadline
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                data['title'],
                data['description'],
                data['category'],
                data['type'],
                data.get('time_required'),
                data.get('price', 0),
                data.get('exchange_type', 'time'),
                data.get('location'),
                data.get('latitude'),
                data.get('longitude'),
                data.get('deadline')
            ))
            
            request_id = cursor.lastrowid
            
            return jsonify({
                'message': 'Request created successfully',
                'request_id': request_id
            }), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Connexion WebSocket"""
    if 'user_id' in session:
        join_room(f"user_{session['user_id']}")
        emit('connected', {'message': 'Connected successfully'})
    else:
        emit('error', {'message': 'Authentication required'})

@socketio.on('disconnect')
def handle_disconnect():
    """Déconnexion WebSocket"""
    if 'user_id' in session:
        leave_room(f"user_{session['user_id']}")

@socketio.on('join_exchange')
def handle_join_exchange(data):
    """Rejoindre une room d'échange"""
    if 'user_id' not in session:
        emit('error', {'message': 'Authentication required'})
        return
    
    exchange_id = data.get('exchange_id')
    if exchange_id:
        join_room(f"exchange_{exchange_id}")
        emit('joined_exchange', {'exchange_id': exchange_id})

@socketio.on('send_message')
def handle_message(data):
    """Envoyer un message"""
    if 'user_id' not in session:
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        with get_db() as conn:
            # Insérer le message
            cursor = conn.execute('''
                INSERT INTO messages (exchange_id, sender_id, content, message_type)
                VALUES (?, ?, ?, ?)
            ''', (
                data['exchange_id'],
                session['user_id'],
                data['content'],
                data.get('message_type', 'text')
            ))
            
            message_id = cursor.lastrowid
            
            # Obtenir les infos du sender
            sender = conn.execute(
                'SELECT username, full_name FROM users WHERE id = ?',
                (session['user_id'],)
            ).fetchone()
            
            # Émettre le message à tous les participants
            socketio.emit('new_message', {
                'id': message_id,
                'exchange_id': data['exchange_id'],
                'sender_id': session['user_id'],
                'sender_name': sender['full_name'],
                'content': data['content'],
                'message_type': data.get('message_type', 'text'),
                'created_at': datetime.utcnow().isoformat()
            }, room=f"exchange_{data['exchange_id']}")
            
    except Exception as e:
        emit('error', {'message': str(e)})

# Pages d'erreur
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Point d'entrée pour les serveurs de production (Gunicorn, etc.)
def create_application():
    """Factory function pour créer l'application Flask"""
    return create_app()[0]

if __name__ == '__main__':
    # Mode développement local
    port = int(os.environ.get('PORT', 5000))
    
    # Validation de la configuration en mode debug seulement
    if app.config.get('DEBUG'):
        errors = Config.validate_config()
        if errors:
            print("Avertissements de configuration:")
            for error in errors:
                print(f"- {error}")
    
    # Démarrage du serveur
    socketio.run(app, host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))

# Export pour Gunicorn
application = app