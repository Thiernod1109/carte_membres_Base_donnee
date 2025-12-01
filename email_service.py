from flask_mail import Mail, Message
from flask import render_template_string
import os

mail = Mail()


def init_mail(app):
    """Initialiser Flask-Mail avec l'application"""
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    mail.init_app(app)
    return mail


def envoyer_email_inscription(membre_email, membre_nom, membre_prenom, numero_membre):
    """Envoyer un email de confirmation d'inscription au membre"""
    try:
        msg = Message(
            subject="ALUBILLES - Inscription reçue",
            recipients=[membre_email]
        )

        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #1e3a8a; text-align: center;">ALUBILLES</h2>
                <h3 style="color: #666;">Association des Anciens Élèves de BILLES</h3>
                <hr style="border: 1px solid #ddd;">

                <p>Bonjour <strong>{membre_prenom} {membre_nom}</strong>,</p>

                <p>Nous avons bien reçu votre demande d'inscription à ALUBILLES.</p>

                <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #856404;">📋 Statut: EN ATTENTE DE VALIDATION</h4>
                    <p style="color: #856404; margin-bottom: 0;">
                        Votre dossier d'inscription est en cours d'examen par notre administration.
                    </p>
                </div>

                <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Numéro de dossier:</strong> <span style="color: #1e3a8a; font-size: 1.2em;">{numero_membre}</span></p>
                    <p style="margin-bottom: 0;"><small>Conservez ce numéro pour suivre l'évolution de votre dossier.</small></p>
                </div>

                <p><strong>Prochaines étapes:</strong></p>
                <ol>
                    <li>Notre équipe vérifiera votre paiement et vos informations</li>
                    <li>Vous recevrez un email de confirmation une fois votre dossier validé</li>
                    <li>Votre carte de membre sera générée et disponible au téléchargement</li>
                </ol>

                <p style="margin-top: 30px;">
                    Si vous avez des questions, n'hésitez pas à nous contacter.
                </p>

                <hr style="border: 1px solid #ddd; margin-top: 30px;">
                <p style="text-align: center; color: #999; font-size: 0.9em;">
                    ALUBILLES - Association des Anciens Élèves de BILLES<br>
                    © 2025 Tous droits réservés
                </p>
            </div>
        </body>
        </html>
        """

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email inscription: {e}")
        return False


def envoyer_email_approbation(membre_email, membre_nom, membre_prenom, numero_membre):
    """Envoyer un email d'approbation au membre"""
    try:
        msg = Message(
            subject="✅ ALUBILLES - Inscription approuvée!",
            recipients=[membre_email]
        )

        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #1e3a8a; text-align: center;">ALUBILLES</h2>
                <h3 style="color: #666;">Association des Anciens Élèves de BILLES</h3>
                <hr style="border: 1px solid #ddd;">

                <p>Bonjour <strong>{membre_prenom} {membre_nom}</strong>,</p>

                <div style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #155724;">✅ FÉLICITATIONS!</h4>
                    <p style="color: #155724; margin-bottom: 0;">
                        Votre inscription à ALUBILLES a été <strong>APPROUVÉE</strong>!
                    </p>
                </div>

                <p>Nous sommes ravis de vous accueillir parmi les membres de notre association.</p>

                <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Numéro de membre:</strong> <span style="color: #1e3a8a; font-size: 1.2em;">{numero_membre}</span></p>
                </div>

                <p><strong>Votre carte de membre est maintenant disponible!</strong></p>
                <p>Vous pouvez la télécharger en vous rendant sur notre site et en utilisant votre numéro de membre.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://votre-site.com/verifier-statut" 
                       style="background: #1e3a8a; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Télécharger ma carte
                    </a>
                </div>

                <p><strong>Rappel de vos engagements:</strong></p>
                <ul>
                    <li>Respecter les règles et statuts de l'association</li>
                    <li>Honorer vos cotisations mensuelles</li>
                    <li>Participer activement aux activités</li>
                    <li>Répondre aux communications de l'association</li>
                </ul>

                <p style="margin-top: 30px;">
                    Bienvenue dans la famille ALUBILLES!
                </p>

                <hr style="border: 1px solid #ddd; margin-top: 30px;">
                <p style="text-align: center; color: #999; font-size: 0.9em;">
                    ALUBILLES - Association des Anciens Élèves de BILLES<br>
                    © 2025 Tous droits réservés
                </p>
            </div>
        </body>
        </html>
        """

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email approbation: {e}")
        return False


def envoyer_email_refus(membre_email, membre_nom, membre_prenom, motif=''):
    """Envoyer un email de refus au membre"""
    try:
        msg = Message(
            subject="ALUBILLES - Décision concernant votre inscription",
            recipients=[membre_email]
        )

        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #1e3a8a; text-align: center;">ALUBILLES</h2>
                <h3 style="color: #666;">Association des Anciens Élèves de BILLES</h3>
                <hr style="border: 1px solid #ddd;">

                <p>Bonjour <strong>{membre_prenom} {membre_nom}</strong>,</p>

                <div style="background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #721c24;">Information concernant votre inscription</h4>
                    <p style="color: #721c24; margin-bottom: 0;">
                        Après examen de votre dossier, nous ne pouvons malheureusement pas donner suite à votre demande d'inscription pour le moment.
                    </p>
                </div>

                {f'<p><strong>Motif:</strong> {motif}</p>' if motif else ''}

                <p>Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez obtenir plus d'informations, 
                   n'hésitez pas à contacter notre administration.</p>

                <p>Vous êtes libre de soumettre une nouvelle demande ultérieurement.</p>

                <p style="margin-top: 30px;">
                    Cordialement,<br>
                    L'équipe ALUBILLES
                </p>

                <hr style="border: 1px solid #ddd; margin-top: 30px;">
                <p style="text-align: center; color: #999; font-size: 0.9em;">
                    ALUBILLES - Association des Anciens Élèves de BILLES<br>
                    © 2025 Tous droits réservés
                </p>
            </div>
        </body>
        </html>
        """

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email refus: {e}")
        return False


def envoyer_email_suspension(membre_email, membre_nom, membre_prenom, motif=''):
    """Envoyer un email de suspension au membre"""
    try:
        msg = Message(
            subject="⚠️ ALUBILLES - Suspension de votre compte",
            recipients=[membre_email]
        )

        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #1e3a8a; text-align: center;">ALUBILLES</h2>
                <h3 style="color: #666;">Association des Anciens Élèves de BILLES</h3>
                <hr style="border: 1px solid #ddd;">

                <p>Bonjour <strong>{membre_prenom} {membre_nom}</strong>,</p>

                <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #856404;">⚠️ COMPTE SUSPENDU</h4>
                    <p style="color: #856404; margin-bottom: 0;">
                        Votre compte membre a été temporairement suspendu.
                    </p>
                </div>

                {f'<p><strong>Raison de la suspension:</strong> {motif}</p>' if motif else ''}

                <p><strong>Qu'est-ce que cela signifie?</strong></p>
                <ul>
                    <li>Votre carte de membre est temporairement désactivée</li>
                    <li>Vous n'avez plus accès aux avantages membres</li>
                    <li>Votre participation aux événements est suspendue</li>
                </ul>

                <p><strong>Pour réactiver votre compte:</strong></p>
                <ol>
                    <li>Régularisez votre situation (cotisations, paiements, etc.)</li>
                    <li>Contactez l'administration: admin@alubilles.org</li>
                    <li>Attendez la confirmation de réactivation</li>
                </ol>

                <p style="margin-top: 30px;">
                    Nous espérons résoudre cette situation rapidement.
                </p>

                <p>
                    Cordialement,<br>
                    L'équipe ALUBILLES
                </p>

                <hr style="border: 1px solid #ddd; margin-top: 30px;">
                <p style="text-align: center; color: #999; font-size: 0.9em;">
                    ALUBILLES - Association des Anciens Élèves de BILLES<br>
                    © 2025 Tous droits réservés
                </p>
            </div>
        </body>
        </html>
        """

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email suspension: {e}")
        return False


def envoyer_notification_admin(admin_email, membre_nom, membre_prenom, numero_membre):
    """Envoyer une notification à l'admin lors d'une nouvelle inscription"""
    try:
        msg = Message(
            subject="🆕 ALUBILLES - Nouvelle inscription à valider",
            recipients=[admin_email]
        )

        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #1e3a8a; text-align: center;">ALUBILLES - Administration</h2>
                <hr style="border: 1px solid #ddd;">

                <div style="background: #e7f3ff; padding: 15px; border-left: 4px solid #1e3a8a; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #1e3a8a;">🆕 NOUVELLE INSCRIPTION</h4>
                    <p style="margin-bottom: 0;">
                        Un nouveau membre vient de s'inscrire et attend votre validation.
                    </p>
                </div>

                <p><strong>Détails du membre:</strong></p>
                <ul>
                    <li><strong>Nom:</strong> {membre_prenom} {membre_nom}</li>
                    <li><strong>Numéro de dossier:</strong> {numero_membre}</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://votre-site.com/admin/inscriptions" 
                       style="background: #1e3a8a; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Voir les inscriptions en attente
                    </a>
                </div>

                <p style="color: #666; font-size: 0.9em;">
                    Cette notification est envoyée automatiquement à chaque nouvelle inscription.
                </p>

                <hr style="border: 1px solid #ddd; margin-top: 30px;">
                <p style="text-align: center; color: #999; font-size: 0.9em;">
                    ALUBILLES - Système de gestion<br>
                    © 2025 Tous droits réservés
                </p>
            </div>
        </body>
        </html>
        """

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi notification admin: {e}")
        return False