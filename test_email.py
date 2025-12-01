#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration des emails
"""

from email_service import init_mail, envoyer_email_inscription, envoyer_notification_admin
from flask import Flask
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Créer une application Flask temporaire pour les tests
app = Flask(__name__)
mail = init_mail(app)


def test_email_configuration():
    """Tester la configuration de base"""
    print("=" * 50)
    print("TEST DE CONFIGURATION EMAIL")
    print("=" * 50)

    print(f"📧 Serveur SMTP: {app.config.get('MAIL_SERVER')}")
    print(f"📧 Port: {app.config.get('MAIL_PORT')}")
    print(f"📧 TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"📧 Username: {app.config.get('MAIL_USERNAME')}")
    print(f"📧 Sender: {app.config.get('MAIL_DEFAULT_SENDER')}")

    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("\n❌ ERREUR: Configuration email incomplète!")
        print("Vérifiez votre fichier .env")
        return False

    print("\n✅ Configuration chargée avec succès!")
    return True


def test_envoi_email():
    """Tester l'envoi d'un email de test"""
    print("\n" + "=" * 50)
    print("TEST D'ENVOI D'EMAIL")
    print("=" * 50)

    email_test = input("\n📧 Entrez votre email pour le test: ").strip()

    if not email_test:
        print("❌ Email invalide!")
        return False

    print(f"\n📤 Envoi d'un email de test à {email_test}...")

    with app.app_context():
        try:
            # Tester l'email d'inscription
            success = envoyer_email_inscription(
                email_test,
                "Test",
                "Utilisateur",
                "ALU-2024-TEST"
            )

            if success:
                print("✅ Email envoyé avec succès!")
                print(f"📬 Vérifiez votre boîte mail: {email_test}")
                print("💡 N'oubliez pas de vérifier les spams!")
                return True
            else:
                print("❌ Échec de l'envoi de l'email")
                return False

        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {e}")
            print("\n💡 Solutions possibles:")
            print("  1. Vérifiez que vous utilisez un mot de passe d'application Gmail")
            print("  2. Activez la validation en 2 étapes sur votre compte Google")
            print("  3. Vérifiez vos paramètres dans le fichier .env")
            return False


def test_notification_admin():
    """Tester l'envoi de notification admin"""
    print("\n" + "=" * 50)
    print("TEST DE NOTIFICATION ADMIN")
    print("=" * 50)

    admin_email = os.getenv('ADMIN_EMAIL')
    print(f"\n📧 Email admin configuré: {admin_email}")

    reponse = input(f"Envoyer un email de test à {admin_email}? (o/n): ").strip().lower()

    if reponse != 'o':
        print("❌ Test annulé")
        return False

    with app.app_context():
        try:
            success = envoyer_notification_admin(
                admin_email,
                "Test",
                "Membre",
                "ALU-2024-TEST"
            )

            if success:
                print("✅ Notification admin envoyée avec succès!")
                return True
            else:
                print("❌ Échec de l'envoi de la notification")
                return False

        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False


def main():
    """Fonction principale"""
    print("\n🔧 OUTIL DE TEST EMAIL - ALUBILLES")
    print("=" * 50)

    # Test 1: Configuration
    if not test_email_configuration():
        print("\n⚠️ Corrigez d'abord la configuration avant de continuer")
        return

    # Test 2: Envoi email
    test_envoi_email()

    # Test 3: Notification admin
    continuer = input("\n\nTester la notification admin? (o/n): ").strip().lower()
    if continuer == 'o':
        test_notification_admin()

    print("\n" + "=" * 50)
    print("✅ Tests terminés!")
    print("=" * 50)


if __name__ == '__main__':
    main()