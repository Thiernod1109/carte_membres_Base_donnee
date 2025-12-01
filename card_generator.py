from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

def create_alumni_member_card(membre_data, template_path, output_path):
    """
    Ajouter les informations du membre sur le template de carte existant

    Args:
        membre_data: dict avec les infos du membre
        template_path: chemin vers l'image template
        output_path: chemin où sauvegarder la carte
    """

    # Charger l'image template
    card = Image.open(template_path)
    draw = ImageDraw.Draw(card)

    # Couleur du texte
    text_dark = '#333333'

    # Charger les polices
    try:
        # Police pour les valeurs (nom, email, etc.)
        font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)

        # Police en gras pour les titres
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except Exception:
        try:
            # Alternative Windows
            font_value = ImageFont.truetype("arial.ttf", 22)
            font_bold = ImageFont.truetype("arialbd.ttf", 24)
        except:
            font_value = ImageFont.load_default()
            font_bold = ImageFont.load_default()

        # ===== AJOUTER LA PHOTO DU MEMBRE DANS LE CERCLE =====
    photo_path = membre_data.get('photo_path')
    if photo_path and os.path.exists(photo_path):
        try:
            # Position et taille du cercle
            circle_x = 238  # Centre X du cercle
            circle_y = 250  # Centre Y du cercle
            circle_radius = 180  # Rayon du cercle
            photo_size = circle_radius * 2  # Diamètre

            # Charger et redimensionner la photo
            photo = Image.open(photo_path)
            photo = photo.convert('RGB')

            # Redimensionner pour remplir le cercle (crop au centre)
            photo = ImageOps.fit(photo, (photo_size, photo_size), Image.Resampling.LANCZOS)

            # Créer un masque circulaire
            mask = Image.new('L', (photo_size, photo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, photo_size, photo_size), fill=255)

            # Appliquer le masque à la photo
            photo.putalpha(mask)

            # Position de collage (coin supérieur gauche de la photo)
            paste_x = circle_x - circle_radius
            paste_y = circle_y - circle_radius

            # Coller la photo sur la carte
            card.paste(photo, (paste_x, paste_y), mask)

        except Exception as e:
            print(f"⚠ Erreur lors de l'ajout de la photo: {e}")

    # Positions pour les valeurs (après les ":")
    info_x = 649  # Position X pour les valeurs
    info_y_start = 383  # Position Y de départ
    line_height = 40  # Espacement entre les lignes

    # Ajouter le Nom
    draw.text((info_x, info_y_start),
              f"{membre_data.get('prenom', '')} {membre_data.get('nom', '')}".strip() or 'N/A',
              fill=text_dark,
              font=font_bold,
              anchor='lm')

    # Ajouter le No ID
    draw.text((info_x, info_y_start + line_height),
              membre_data.get('numero_membre', 'N/A'),
              fill=text_dark,
              font=font_bold,
              anchor='lm')

    # Ajouter le Cellulaire
    draw.text((info_x, info_y_start + line_height * 2),
              membre_data.get('telephone', 'N/A'),
              fill=text_dark,
              font=font_bold,
              anchor='lm')

    # Ajouter le Courriel
    email = membre_data.get('email', 'N/A')
    if len(email) > 35:
        email = email[:32] + "..."
    draw.text((info_x, info_y_start + line_height * 3),
              email,
              fill=text_dark,
              font=font_bold,
              anchor='lm')

    # Sauvegarder la carte
    card.save(output_path, 'PNG', quality=95)
    print(f"✓ Carte de membre créée: {output_path}")

    return output_path


# Exemple d'utilisation
if __name__ == '__main__':
    membre = {
        'numero_membre': 'ALU-001',
        'nom': 'Thierno Mamadou Diallo',
        'email': 'waydiallo@yahoo.fr',
        'telephone': '873-307-1175',
        'photo_path': 'static/uploads/test.jpg'

    }

    create_alumni_member_card(
        membre,
        'static/images/Carte_membre_base.png',  # Votre image template
        'cards/member_card.png'
    )