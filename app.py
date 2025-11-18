from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from database import init_db, add_membre, get_membre, get_all_membres, update_carte_path, search_membres, delete_membre
from card_generator import create_member_card

app = Flask(__name__)
app.secret_key = 'alubilles_secret_key_2024'

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

        # Ajouter le membre à la base de données
        membre_id, numero_membre = add_membre(
            nom, prenom, date_naissance, promotion,
            email, telephone, adresse, photo_path
        )

        # Récupérer les infos complètes du membre
        membre = get_membre(membre_id)

        # Générer la carte de membre
        carte_filename = f"carte_{numero_membre}.png"
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

        create_member_card(membre_data, carte_path)

        # Mettre à jour le chemin de la carte dans la base
        update_carte_path(membre_id, carte_path)

        flash(f'Inscription réussie! Numéro de membre: {numero_membre}', 'success')
        return redirect(url_for('confirmation', membre_id=membre_id))

    except Exception as e:
        flash(f'Erreur lors de l\'inscription: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/confirmation/<int:membre_id>')
def confirmation(membre_id):
    """Page de confirmation avec la carte de membre"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('index'))

    return render_template('confirmation.html', membre=membre)

@app.route('/telecharger-carte/<int:membre_id>')
def telecharger_carte(membre_id):
    """Télécharger la carte de membre"""
    membre = get_membre(membre_id)
    if not membre or not membre['carte_path']:
        flash('Carte non trouvée', 'error')
        return redirect(url_for('index'))

    return send_file(
        membre['carte_path'],
        as_attachment=True,
        download_name=f"carte_membre_{membre['numero_membre']}.png"
    )

@app.route('/membres')
def liste_membres():
    """Liste de tous les membres (page admin)"""
    query = request.args.get('search', '')
    if query:
        membres = search_membres(query)
    else:
        membres = get_all_membres()

    return render_template('membres.html', membres=membres, search_query=query)

@app.route('/membre/<int:membre_id>')
def voir_membre(membre_id):
    """Voir les détails d'un membre"""
    membre = get_membre(membre_id)
    if not membre:
        flash('Membre non trouvé', 'error')
        return redirect(url_for('liste_membres'))

    return render_template('membre_detail.html', membre=membre)

@app.route('/supprimer/<int:membre_id>', methods=['POST'])
def supprimer_membre(membre_id):
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

    return redirect(url_for('liste_membres'))

@app.route('/api/stats')
def api_stats():
    """API pour les statistiques"""
    membres = get_all_membres()
    return jsonify({
        'total_membres': len(membres),
        'membres_actifs': sum(1 for m in membres if m['actif'])
    })

if __name__ == '__main__':
    # Initialiser la base de données
    init_db()
    print("Base de données initialisée!")

    # Lancer l'application
    app.run(debug=True, host='0.0.0.0', port=5000)
