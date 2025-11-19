from PIL import Image, ImageDraw, ImageFont
import os


def create_modern_member_card(membre_data, output_path):
    """
    Créer une carte de membre moderne ALUBILLES avec design géométrique

    Args:
        membre_data: dict avec les infos du membre
        output_path: chemin où sauvegarder la carte
    """

    # Dimensions verticales (format portrait - ID card standard)
    card_width = 630  # 3.5 pouces (88.9mm)
    card_height = 1000  # 5.5 pouces (139.7mm)

    # Créer l'image de base
    card = Image.new('RGB', (card_width, card_height), color='#FFFFFF')
    draw = ImageDraw.Draw(card)

    # Couleurs
    primary_blue = '#1E5BA8'  # Bleu foncé
    light_gray = '#E0E0E0'
    text_color = '#000000'
    white = '#FFFFFF'

    # Charger les polices
    try:
        font_company = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception:
        font_company = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_info = ImageFont.load_default()

    # ===== EN-TÊTE AVEC FORMES GÉOMÉTRIQUES =====

    # Triangle bleu haut gauche
    points_left = [(0, 0), (280, 0), (250, 200)]
    draw.polygon(points_left, fill=primary_blue)

    # Triangle bleu haut droit
    points_right = [(card_width, 0), (card_width - 280, 0), (card_width - 250, 200)]
    draw.polygon(points_right, fill=primary_blue)

    # Titre de l'association
    draw.text((card_width // 2, 40), "ALUBILLES", fill=text_color, font=font_company, anchor='mm')

    # ===== ZONE PHOTO HEXAGON =====
    photo_x = card_width // 2
    photo_y = 280
    hexagon_size = 100

    # Dessiner hexagon (placeholder pour photo)
    import math
    hex_points = []
    for i in range(6):
        angle = math.radians(i * 60)
        x = photo_x + hexagon_size * math.cos(angle)
        y = photo_y + hexagon_size * math.sin(angle)
        hex_points.append((x, y))

    draw.polygon(hex_points, fill=light_gray, outline=primary_blue)

    # Charger et placer la photo si elle existe
    if membre_data.get('photo_path') and os.path.exists(membre_data['photo_path']):
        try:
            photo = Image.open(membre_data['photo_path'])
            photo_size = 180
            photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)
            card.paste(photo, (photo_x - photo_size // 2, photo_y - photo_size // 2))
        except Exception:
            draw.text((photo_x, photo_y), "PHOTO", fill='#999999', font=font_title, anchor='mm')
    else:
        draw.text((photo_x, photo_y), "PHOTO", fill='#999999', font=font_title, anchor='mm')

    # ===== INFORMATIONS DU MEMBRE =====
    info_y_start = 450

    # Nom et prénom
    nom_complet = f"{membre_data.get('prenom', '')} {membre_data.get('nom', '')}".upper()
    draw.text((card_width // 2, info_y_start), nom_complet, fill=primary_blue, font=font_name, anchor='mm')

    # Titre/Position
    draw.text((card_width // 2, info_y_start + 60), "MEMBRE", fill=text_color, font=font_title, anchor='mm')

    # Ligne de séparation
    draw.line([(150, info_y_start + 90), (card_width - 150, info_y_start + 90)], fill=primary_blue, width=2)

    # Données personnelles
    info_start = info_y_start + 140
    line_height = 60

    # ID Number
    draw.text((80, info_start), "ID No", fill=text_color, font=font_label, anchor='lm')
    draw.text((320, info_start), f": {membre_data.get('numero_membre', 'N/A')}", fill=text_color, font=font_info,
              anchor='lm')

    # Date de naissance
    draw.text((80, info_start + line_height), "DOB", fill=text_color, font=font_label, anchor='lm')
    draw.text((320, info_start + line_height), f": {membre_data.get('date_naissance', 'N/A')}", fill=text_color,
              font=font_info, anchor='lm')

    # Email
    draw.text((80, info_start + line_height * 2), "Email", fill=text_color, font=font_label, anchor='lm')
    email_text = membre_data.get('email', 'N/A')
    if len(email_text) > 30:
        email_text = email_text[:27] + "..."
    draw.text((320, info_start + line_height * 2), f": {email_text}", fill=text_color, font=font_info, anchor='lm')

    # Téléphone
    draw.text((80, info_start + line_height * 3), "Phone", fill=text_color, font=font_label, anchor='lm')
    draw.text((320, info_start + line_height * 3), f": {membre_data.get('telephone', 'N/A')}", fill=text_color,
              font=font_info, anchor='lm')

    # ===== PIED DE PAGE AVEC FORME COURBE =====
    # Forme courbe en bas
    footer_y = 900

    # Courbe supérieure (ondulée)
    points_curve = []
    for x in range(0, card_width + 1, 20):
        y = footer_y - 30 + 30 * abs((x - card_width // 2) / (card_width // 2)) ** 0.5
        points_curve.append((x, y))

    # Compléter le polygone
    points_curve.append((card_width, footer_y))
    points_curve.append((card_width, card_height))
    points_curve.append((0, card_height))
    points_curve.append((0, footer_y))

    draw.polygon(points_curve, fill=primary_blue)

    # Texte du pied de page
    if membre_data.get('date_inscription'):
        date_text = membre_data['date_inscription'].split(' ')[0] if ' ' in membre_data['date_inscription'] else \
        membre_data['date_inscription']
        draw.text((card_width // 2, card_height - 50), f"Membre depuis: {date_text}",
                  fill=white, font=font_info, anchor='mm')

    # Sauvegarder la carte
    card.save(output_path, 'PNG', quality=95)
    print(f"Carte moderne créée: {output_path}")

    return output_path


if __name__ == '__main__':
    # Test de génération
    test_data = {
        'numero_membre': 'ALU-2025-0001',
        'nom': 'SYLLA',
        'prenom': 'ALIOUNE',
        'date_naissance': '2002-09-12',
        'email': 'alioune.sylla@email.com',
        'telephone': '+221 77 330 7117',
        'date_inscription': '2025-11-18',
        'photo_path': None
    }

    output = 'test_card_modern.png'
    create_modern_member_card(test_data, output)