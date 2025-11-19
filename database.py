import sqlite3
from datetime import datetime
import hashlib
import os

DATABASE_PATH = 'alubilles.db'

def get_db_connection():
    """Créer une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialiser la base de données avec les tables nécessaires"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table des membres avec statut d'inscription
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_membre TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            date_naissance TEXT,
            promotion TEXT,
            programme TEXT,
            email TEXT,
            telephone TEXT,
            adresse TEXT,
            photo_path TEXT,
            carte_path TEXT,
            date_inscription TEXT NOT NULL,
            statut TEXT DEFAULT 'en_attente',
            date_validation TEXT,
            motif_refus TEXT,
            actif INTEGER DEFAULT 1
        )
    ''')

    # Table des administrateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nom TEXT,
            email TEXT,
            date_creation TEXT NOT NULL,
            actif INTEGER DEFAULT 1
        )
    ''')

    # Créer un admin par défaut s'il n'existe pas
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        default_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password_hash, nom, email, date_creation)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', default_password, 'Administrateur', 'admin@alubilles.org',
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

def hash_password(password):
    """Hasher un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_admin(username, password):
    """Vérifier les identifiants d'un administrateur"""
    conn = get_db_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)
    cursor.execute('''
        SELECT * FROM admins
        WHERE username = ? AND password_hash = ? AND actif = 1
    ''', (username, password_hash))

    admin = cursor.fetchone()
    conn.close()

    return admin

def get_admin(admin_id):
    """Récupérer un admin par son ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admins WHERE id = ?', (admin_id,))
    admin = cursor.fetchone()

    conn.close()
    return admin

def generate_member_number():
    """Générer un numéro de membre unique"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Compter le nombre de membres existants
    cursor.execute('SELECT COUNT(*) FROM membres')
    count = cursor.fetchone()[0]
    conn.close()

    # Format: ALU-ANNÉE-NUMÉRO (ex: ALU-2024-0001)
    year = datetime.now().year
    numero = f"ALU-{year}-{count + 1:04d}"

    return numero

def add_membre(nom, prenom, date_naissance, promotion, programme, email, telephone, adresse, photo_path):
    """Ajouter un nouveau membre à la base de données (statut en_attente par défaut)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    numero_membre = generate_member_number()
    date_inscription = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO membres (numero_membre, nom, prenom, date_naissance, promotion,
                           programme, email, telephone, adresse, photo_path, date_inscription, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'en_attente')
    ''', (numero_membre, nom, prenom, date_naissance, promotion,
          programme, email, telephone, adresse, photo_path, date_inscription))

    membre_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return membre_id, numero_membre

def approuver_membre(membre_id):
    """Approuver l'inscription d'un membre"""
    conn = get_db_connection()
    cursor = conn.cursor()

    date_validation = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE membres
        SET statut = 'approuve', date_validation = ?, motif_refus = NULL
        WHERE id = ?
    ''', (date_validation, membre_id))

    conn.commit()
    conn.close()

def refuser_membre(membre_id, motif=''):
    """Refuser l'inscription d'un membre"""
    conn = get_db_connection()
    cursor = conn.cursor()

    date_validation = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE membres
        SET statut = 'refuse', date_validation = ?, motif_refus = ?
        WHERE id = ?
    ''', (date_validation, motif, membre_id))

    conn.commit()
    conn.close()

def update_carte_path(membre_id, carte_path):
    """Mettre à jour le chemin de la carte de membre"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('UPDATE membres SET carte_path = ? WHERE id = ?', (carte_path, membre_id))

    conn.commit()
    conn.close()

def get_membre(membre_id):
    """Récupérer un membre par son ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM membres WHERE id = ?', (membre_id,))
    membre = cursor.fetchone()

    conn.close()
    return membre

def get_membres_en_attente():
    """Récupérer les membres en attente de validation"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM membres
        WHERE statut = 'en_attente'
        ORDER BY date_inscription ASC
    ''')
    membres = cursor.fetchall()

    conn.close()
    return membres

def get_membres_approuves():
    """Récupérer les membres approuvés"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM membres
        WHERE statut = 'approuve'
        ORDER BY date_validation DESC
    ''')
    membres = cursor.fetchall()

    conn.close()
    return membres

def get_membres_refuses():
    """Récupérer les membres refusés"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM membres
        WHERE statut = 'refuse'
        ORDER BY date_validation DESC
    ''')
    membres = cursor.fetchall()

    conn.close()
    return membres

def get_all_membres():
    """Récupérer tous les membres"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM membres ORDER BY date_inscription DESC')
    membres = cursor.fetchall()

    conn.close()
    return membres

def search_membres(query, statut=None):
    """Rechercher des membres par nom, prénom ou numéro"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if statut:
        cursor.execute('''
            SELECT * FROM membres
            WHERE (nom LIKE ? OR prenom LIKE ? OR numero_membre LIKE ?)
            AND statut = ?
            ORDER BY nom, prenom
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', statut))
    else:
        cursor.execute('''
            SELECT * FROM membres
            WHERE nom LIKE ? OR prenom LIKE ? OR numero_membre LIKE ?
            ORDER BY nom, prenom
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))

    membres = cursor.fetchall()
    conn.close()

    return membres

def delete_membre(membre_id):
    """Supprimer un membre"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM membres WHERE id = ?', (membre_id,))

    conn.commit()
    conn.close()

def get_stats():
    """Obtenir les statistiques des membres"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM membres')
    stats['total'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM membres WHERE statut = "en_attente"')
    stats['en_attente'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM membres WHERE statut = "approuve"')
    stats['approuves'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM membres WHERE statut = "refuse"')
    stats['refuses'] = cursor.fetchone()[0]

    conn.close()
    return stats

# Initialiser la base de données au démarrage
if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès!")
    print("Admin par défaut: username='admin', password='admin123'")
