from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.utils import secure_filename
from functools import wraps
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from dotenv import load_dotenv
from database import (
    init_db, add_membre, get_membre, get_all_membres, update_carte_path,
    search_membres, delete_membre, verify_admin, get_admin, get_stats,
    get_membres_en_attente, get_membres_approuves, get_membres_refuses,
    approuver_membre, refuser_membre, suspendre_membre, reactiver_membre,
    get_membres_suspendus
)
from card_generator import create_alumni_member_card
from email_service import (
    init_mail, envoyer_email_inscription, envoyer_email_approbation,
    envoyer_email_refus, envoyer_email_suspension, envoyer_notification_admin
)

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'alubilles_secret_key_2024')

# Initialiser Flask-Mail
mail = init_mail(app)

# Initialiser la base de données
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
        # Vérifier le consentement
        consent = request.form.get('consent', '')
        if not consent:
            flash('Vous devez accepter les conditions d\'adhésion pour continuer!', 'error')
            return redirect(url_for('index'))

        # Récupérer les données du formulaire
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        date_naissance = request.form.get('date_naissance', '').strip()
        genre = request.form.get('genre', '').strip()
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
            nom, prenom, date_naissance, genre, promotion, programme,
            email, telephone, adresse, photo_path
        )

        # Envoyer un email de confirmation au membre
        if email:
            envoyer_email_inscription(email, nom, prenom, numero_membre)

        # Envoyer une notification à l'admin
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@alubilles.org')
        envoyer_notification_admin(admin_email, nom, prenom, numero_membre)

        flash(f'Inscription envoyée! Votre numéro de dossier: {numero_membre}. Vous recevrez un email de confirmation.', 'success')
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
    stats = get_stats()
    inscriptions = get_membres_en_attente()
    return render_template('admin/inscriptions.html',stats=stats, inscriptions=inscriptions)

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

    # Chemins pour la génération de la carte
    template_path = 'static/images/Carte_membre_base.png'
    carte_filename = f"carte_{membre['numero_membre']}.png"
    output_path = os.path.join(app.config['CARDS_FOLDER'], carte_filename)

    # Préparer les données pour la carte
    membre_data = {
        'numero_membre': membre['numero_membre'],
        'nom': membre['nom'],
        'prenom': membre['prenom'],
        'email': membre['email'],
        'telephone': membre['telephone'],
        'photo_path': membre['photo_path']
    }

    # Générer la carte
    create_alumni_member_card(membre_data, template_path, output_path)
    update_carte_path(membre_id, output_path)

    # Envoyer un email d'approbation
    if membre['email']:
        envoyer_email_approbation(membre['email'], membre['nom'], membre['prenom'], membre['numero_membre'])

    flash(f'✓ Inscription de {membre["prenom"]} {membre["nom"]} approuvée! Email envoyé.', 'success')
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

    # Envoyer un email de refus
    if membre['email']:
        envoyer_email_refus(membre['email'], membre['nom'], membre['prenom'], motif)

    flash(f'Inscription de {membre["prenom"]} {membre["nom"]} refusée. Email envoyé.', 'warning')
    return redirect(url_for('admin_inscriptions'))

@app.route('/admin/suspendre/<int:membre_id>', methods=['POST'])
@admin_required
def admin_suspendre(membre_id):
    """Suspendre un membre"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('admin_membres'))

    motif = request.form.get('motif', 'Défaut de paiement')
    suspendre_membre(membre_id, motif)

    # Envoyer un email de suspension
    if membre['email']:
        envoyer_email_suspension(membre['email'], membre['nom'], membre['prenom'], motif)

    flash(f'Membre {membre["prenom"]} {membre["nom"]} suspendu. Email envoyé.', 'warning')
    return redirect(url_for('admin_membres'))

@app.route('/admin/reactiver/<int:membre_id>', methods=['POST'])
@admin_required
def admin_reactiver(membre_id):
    """Réactiver un membre suspendu"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('admin_suspendus'))

    reactiver_membre(membre_id)

    # Envoyer un email de réactivation (on peut réutiliser l'email d'approbation)
    if membre['email']:
        envoyer_email_approbation(membre['email'], membre['nom'], membre['prenom'], membre['numero_membre'])

    flash(f'Membre {membre["prenom"]} {membre["nom"]} réactivé. Email envoyé.', 'success')
    return redirect(url_for('admin_suspendus'))

@app.route('/admin/suspendus')
@admin_required
def admin_suspendus():
    """Liste des membres suspendus"""
    stats = get_stats()
    membres = get_membres_suspendus()
    return render_template('admin/suspendus.html',stats=stats, membres=membres)

@app.route('/admin/membres')
@admin_required
def admin_membres():
    """Liste de tous les membres approuvés"""
    stats = get_stats()
    query = request.args.get('search', '')
    if query:
        membres = search_membres(query, 'approuve')
    else:
        membres = get_membres_approuves()

    return render_template('admin/membres.html',stats=stats, membres=membres, search_query=query)

@app.route('/admin/refuses')
@admin_required
def admin_refuses():
    """Liste des inscriptions refusées"""
    stats = get_stats()
    membres = get_membres_refuses()
    return render_template('admin/refuses.html',stats=stats, membres=membres)

@app.route('/admin/membre/<int:membre_id>')
@admin_required
def admin_voir_membre(membre_id):
    """Voir les détails d'un membre"""
    stats = get_stats()
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('admin_membres'))

    return render_template('admin/membre_detail.html',stats=stats, membre=membre)

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