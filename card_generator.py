from PIL import Image, ImageDraw, ImageFont
import os

def create_member_card(membre_data, output_path):
    """
    Créer une carte de membre pour l'association ALUBILLES

    Args:
        membre_data: dict avec les infos du membre
        output_path: chemin où sauvegarder la carte
    """

    # Dimensions de la carte (format carte de crédit en pixels, 300 DPI)
    card_width = 1011  # 85.6mm
    card_height = 638  # 54mm

    # Créer l'image de base
    card = Image.new('RGB', (card_width, card_height), color='#FFFFFF')
    draw = ImageDraw.Draw(card)

    # Couleurs ALUBILLES
    primary_color = '#1E3A5F'  # Bleu foncé
    secondary_color = '#C9A227'  # Or
    text_color = '#333333'

    # Dessiner l'en-tête
    draw.rectangle([0, 0, card_width, 120], fill=primary_color)

    # Charger les polices (utiliser les polices par défaut si non disponibles)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_number = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_info = ImageFont.load_default()
        font_number = ImageFont.load_default()

    # Titre de l'association
    draw.text((card_width // 2, 35), "ALUBILLES", fill='#FFFFFF', font=font_title, anchor='mm')
    draw.text((card_width // 2, 80), "Association des Anciens Élèves", fill=secondary_color, font=font_subtitle, anchor='mm')

    # Zone photo (à gauche)
    photo_x = 40
    photo_y = 150
    photo_size = 180

    # Cadre pour la photo
    draw.rectangle([photo_x - 3, photo_y - 3, photo_x + photo_size + 3, photo_y + photo_size + 3],
                   outline=primary_color, width=3)

    # Charger et redimensionner la photo si elle existe
    if membre_data.get('photo_path') and os.path.exists(membre_data['photo_path']):
        try:
            photo = Image.open(membre_data['photo_path'])
            photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)
            card.paste(photo, (photo_x, photo_y))
        except Exception:
            # Photo par défaut si erreur
            draw.rectangle([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size],
                          fill='#E0E0E0')
            draw.text((photo_x + photo_size // 2, photo_y + photo_size // 2), "Photo",
                     fill='#999999', font=font_info, anchor='mm')
    else:
        # Placeholder photo
        draw.rectangle([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size],
                      fill='#E0E0E0')
        draw.text((photo_x + photo_size // 2, photo_y + photo_size // 2), "Photo",
                 fill='#999999', font=font_info, anchor='mm')

    # Informations du membre (à droite de la photo)
    info_x = 260
    info_y = 160

    # Nom et prénom
    nom_complet = f"{membre_data.get('prenom', '')} {membre_data.get('nom', '')}".upper()
    draw.text((info_x, info_y), nom_complet, fill=primary_color, font=font_name)

    # Promotion
    if membre_data.get('promotion'):
        draw.text((info_x, info_y + 45), f"Promotion: {membre_data['promotion']}", fill=text_color, font=font_info)

    # Date de naissance
    if membre_data.get('date_naissance'):
        draw.text((info_x, info_y + 75), f"Né(e) le: {membre_data['date_naissance']}", fill=text_color, font=font_info)

    # Email
    if membre_data.get('email'):
        email_text = membre_data['email']
        if len(email_text) > 30:
            email_text = email_text[:27] + "..."
        draw.text((info_x, info_y + 105), f"Email: {email_text}", fill=text_color, font=font_info)

    # Téléphone
    if membre_data.get('telephone'):
        draw.text((info_x, info_y + 135), f"Tél: {membre_data['telephone']}", fill=text_color, font=font_info)

    # Ligne de séparation en bas
    draw.rectangle([0, card_height - 80, card_width, card_height], fill=primary_color)

    # Numéro de membre
    draw.text((40, card_height - 50), f"N° {membre_data.get('numero_membre', 'N/A')}", fill='#FFFFFF', font=font_number)

    # Date d'inscription
    if membre_data.get('date_inscription'):
        date_text = membre_data['date_inscription'].split(' ')[0] if ' ' in membre_data['date_inscription'] else membre_data['date_inscription']
        draw.text((card_width - 40, card_height - 50), f"Membre depuis: {date_text}",
                 fill=secondary_color, font=font_info, anchor='rm')

    # Bande décorative
    draw.rectangle([0, 120, card_width, 125], fill=secondary_color)

    # Sauvegarder la carte
    card.save(output_path, 'PNG', quality=95)

    return output_path


if __name__ == '__main__':
    # Test de génération
    test_data = {
        'numero_membre': 'ALU-2024-0001',
        'nom': 'DIALLO',
        'prenom': 'Mamadou',
        'date_naissance': '1990-05-15',
        'promotion': '2010',
        'email': 'mamadou.diallo@email.com',
        'telephone': '+221 77 123 45 67',
        'date_inscription': '2024-01-15',
        'photo_path': None
    }

    output = 'test_card.png'
    create_member_card(test_data, output)
    print(f"Carte de test créée: {output}")
