from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.utils import secure_filename
from functools import wraps
import os
from database import (
    init_db, add_membre, get_membre, get_all_membres, update_carte_path,
    search_membres, delete_membre, verify_admin, get_admin, get_stats,
    get_membres_en_attente, get_membres_approuves, get_membres_refuses,
    approuver_membre, refuser_membre
)
from card_generator import create_modern_member_card

app = Flask(__name__)
app.secret_key = 'alubilles_secret_key_2024'

# ✅ INITIALISER LA BASE DE DONNÉES (IMPORTANT POUR GUNICORN/RENDER)
init_db()

# Configuration
UPLOAD_FOLDER = 'static/uploads'
CARDS_FOLDER = 'cards'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CARDS_FOLDER'] = CARDS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Créer les dossiers s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARDS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Décorateur pour protéger les routes admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES MEMBRES ====================

@app.route('/')
def index():
    """Page principale avec le formulaire d'inscription"""
    return render_template('index.html')

@app.route('/inscription', methods=['POST'])
def inscription():
    """Traiter le formulaire d'inscription"""
    try:
        # Récupérer les données du formulaire
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        date_naissance = request.form.get('date_naissance', '').strip()
        promotion = request.form.get('promotion', '').strip()
        programme = request.form.get('programme', '').strip()
        email = request.form.get('email', '').strip()
        telephone = request.form.get('telephone', '').strip()
        adresse = request.form.get('adresse', '').strip()

        # Validation des champs obligatoires
        if not nom or not prenom:
            flash('Le nom et le prénom sont obligatoires!', 'error')
            return redirect(url_for('index'))

        # Traiter la photo
        photo_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{nom}_{prenom}_{file.filename}")
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(photo_path)

        # Ajouter le membre à la base de données (statut en_attente)
        membre_id, numero_membre = add_membre(
            nom, prenom, date_naissance, promotion, programme,
            email, telephone, adresse, photo_path
        )

        flash(f'Inscription envoyée! Votre numéro de dossier: {numero_membre}. Vous recevrez votre carte après validation par l\'administration.', 'success')
        return redirect(url_for('inscription_confirmee', membre_id=membre_id))

    except Exception as e:
        flash(f'Erreur lors de l\'inscription: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/inscription-confirmee/<int:membre_id>')
def inscription_confirmee(membre_id):
    """Page de confirmation d'inscription (en attente)"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Inscription non trouvée', 'error')
        return redirect(url_for('index'))

    return render_template('inscription_confirmee.html', membre=membre)

@app.route('/verifier-statut', methods=['GET', 'POST'])
def verifier_statut():
    """Permettre aux membres de vérifier le statut de leur inscription"""
    membre = None
    if request.method == 'POST':
        numero = request.form.get('numero_membre', '').strip()
        if numero:
            # Rechercher par numéro de membre
            from database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM membres WHERE numero_membre = ?', (numero,))
            membre = cursor.fetchone()
            conn.close()

            if not membre:
                flash('Numéro de dossier non trouvé', 'error')

    return render_template('verifier_statut.html', membre=membre)

@app.route('/telecharger-carte/<int:membre_id>')
def telecharger_carte(membre_id):
    """Télécharger la carte de membre (seulement si approuvé)"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('index'))

    if membre['statut'] != 'approuve':
        flash('Votre inscription n\'est pas encore validée', 'error')
        return redirect(url_for('verifier_statut'))

    if not membre['carte_path']:
        flash('Carte non encore générée', 'error')
        return redirect(url_for('verifier_statut'))

    return send_file(
        membre['carte_path'],
        as_attachment=True,
        download_name=f"carte_membre_{membre['numero_membre']}.png"
    )

# ==================== ROUTES ADMIN ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Page de connexion admin"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = verify_admin(username, password)
        if admin:
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            flash(f'Bienvenue {admin["nom"]}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Identifiants incorrects', 'error')

    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion admin"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Vous êtes déconnecté', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Tableau de bord admin"""
    stats = get_stats()
    inscriptions_en_attente = get_membres_en_attente()
    return render_template('admin/dashboard.html', stats=stats, inscriptions=inscriptions_en_attente)

@app.route('/admin/inscriptions')
@admin_required
def admin_inscriptions():
    """Liste des inscriptions en attente"""
    inscriptions = get_membres_en_attente()
    return render_template('admin/inscriptions.html', inscriptions=inscriptions)

@app.route('/admin/approuver/<int:membre_id>', methods=['POST'])
@admin_required
def admin_approuver(membre_id):
    """Approuver une inscription"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('admin_inscriptions'))

    # Approuver le membre
    approuver_membre(membre_id)

    # Générer la carte de membre
    carte_filename = f"carte_{membre['numero_membre']}.png"
    carte_path = os.path.join(app.config['CARDS_FOLDER'], carte_filename)

    membre_data = {
        'numero_membre': membre['numero_membre'],
        'nom': membre['nom'],
        'prenom': membre['prenom'],
        'date_naissance': membre['date_naissance'],
        'promotion': membre['promotion'],
        'email': membre['email'],
        'telephone': membre['telephone'],
        'date_inscription': membre['date_inscription'],
        'photo_path': membre['photo_path']
    }

    create_modern_member_card(membre_data, carte_path)
    update_carte_path(membre_id, carte_path)

    flash(f'Inscription de {membre["prenom"]} {membre["nom"]} approuvée! Carte générée.', 'success')
    return redirect(url_for('admin_inscriptions'))

@app.route('/admin/refuser/<int:membre_id>', methods=['POST'])
@admin_required
def admin_refuser(membre_id):
    """Refuser une inscription"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('admin_inscriptions'))

    motif = request.form.get('motif', '')
    refuser_membre(membre_id, motif)

    flash(f'Inscription de {membre["prenom"]} {membre["nom"]} refusée.', 'warning')
    return redirect(url_for('admin_inscriptions'))

@app.route('/admin/membres')
@admin_required
def admin_membres():
    """Liste de tous les membres approuvés"""
    query = request.args.get('search', '')
    if query:
        membres = search_membres(query, 'approuve')
    else:
        membres = get_membres_approuves()

    return render_template('admin/membres.html', membres=membres, search_query=query)

@app.route('/admin/refuses')
@admin_required
def admin_refuses():
    """Liste des inscriptions refusées"""
    membres = get_membres_refuses()
    return render_template('admin/refuses.html', membres=membres)

@app.route('/admin/membre/<int:membre_id>')
@admin_required
def admin_voir_membre(membre_id):
    """Voir les détails d'un membre"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('admin_membres'))

    return render_template('admin/membre_detail.html', membre=membre)

@app.route('/admin/supprimer/<int:membre_id>', methods=['POST'])
@admin_required
def admin_supprimer(membre_id):
    """Supprimer un membre"""
    membre = get_membre(membre_id)
    if membre:
        # Supprimer les fichiers associés
        if membre['photo_path'] and os.path.exists(membre['photo_path']):
            os.remove(membre['photo_path'])
        if membre['carte_path'] and os.path.exists(membre['carte_path']):
            os.remove(membre['carte_path'])

        delete_membre(membre_id)
        flash('Membre supprimé avec succès', 'success')

    return redirect(url_for('admin_membres'))

@app.route('/api/stats')
@admin_required
def api_stats():
    """API pour les statistiques"""
    stats = get_stats()
    return jsonify(stats)

if __name__ == '__main__':
    print("=" * 50)
    print("ALUBILLES - Système de Gestion des Membres")
    print("=" * 50)
    print("Base de données initialisée!")
    print("Admin par défaut: username='admin', password='admin123'")
    print("=" * 50)

    # Lancer l'application
    app.run(debug=True, host='0.0.0.0', port=5000)