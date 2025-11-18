import sqlite3
from datetime import datetime
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_membre TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            date_naissance TEXT,
            promotion TEXT,
            email TEXT,
            telephone TEXT,
            adresse TEXT,
            photo_path TEXT,
            carte_path TEXT,
            date_inscription TEXT NOT NULL,
            actif INTEGER DEFAULT 1
        )
    ''')

    conn.commit()
    conn.close()

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

def add_membre(nom, prenom, date_naissance, promotion, email, telephone, adresse, photo_path):
    """Ajouter un nouveau membre à la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()

    numero_membre = generate_member_number()
    date_inscription = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO membres (numero_membre, nom, prenom, date_naissance, promotion,
                           email, telephone, adresse, photo_path, date_inscription)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero_membre, nom, prenom, date_naissance, promotion,
          email, telephone, adresse, photo_path, date_inscription))

    membre_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return membre_id, numero_membre

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

def get_all_membres():
    """Récupérer tous les membres"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM membres ORDER BY date_inscription DESC')
    membres = cursor.fetchall()

    conn.close()
    return membres

def search_membres(query):
    """Rechercher des membres par nom, prénom ou numéro"""
    conn = get_db_connection()
    cursor = conn.cursor()

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

# Initialiser la base de données au démarrage
if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès!")
