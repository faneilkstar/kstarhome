"""
Service de génération de cartes d'étudiant
Design blanc et doré avec photo, QR code et NFC
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app import db


class CarteEtudiantService:
    """Service pour générer des cartes d'étudiant modernes"""

    def __init__(self):
        self.width = 856  # 85.6mm à 100 DPI
        self.height = 540  # 54mm à 100 DPI

        # Couleurs blanc et doré
        self.color_gold = (218, 165, 32)  # #DAA520
        self.color_gold_light = (255, 215, 0)  # #FFD700
        self.color_white = (255, 255, 255)
        self.color_black = (0, 0, 0)
        self.color_gray = (128, 128, 128)

    def generer_carte_complete(self, etudiant):
        """
        Génère une carte d'étudiant complète avec photo et QR code

        Args:
            etudiant: Objet Etudiant

        Returns:
            str: Chemin vers la carte générée
        """
        # Créer l'image de base
        carte = Image.new('RGB', (self.width, self.height), self.color_white)
        draw = ImageDraw.Draw(carte)

        # 1. Bandeau doré en haut
        self._dessiner_bandeau_superieur(draw, etudiant)

        # 2. Photo de l'étudiant (gauche)
        self._ajouter_photo(carte, etudiant)

        # 3. Informations de l'étudiant (centre)
        self._ajouter_informations(draw, etudiant)

        # 4. QR Code (droite)
        self._ajouter_qr_code(carte, etudiant)

        # 5. Badge NFC virtuel
        self._ajouter_badge_nfc(draw)

        # 6. Pied de page
        self._dessiner_pied_page(draw)

        # Sauvegarder
        output_dir = os.path.join('app', 'static', 'cartes')
        os.makedirs(output_dir, exist_ok=True)

        filename = f"carte_{etudiant.matricule}_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(output_dir, filename)

        carte.save(filepath, 'PNG', quality=95, dpi=(300, 300))

        return filepath

    def generer_carte_enseignant(self, enseignant):
        """
        Génère une carte d'enseignant avec photo et QR code

        Args:
            enseignant: Objet Enseignant

        Returns:
            str: Chemin vers la carte générée
        """
        # Créer l'image de base
        carte = Image.new('RGB', (self.width, self.height), self.color_white)
        draw = ImageDraw.Draw(carte)

        # 1. Bandeau doré en haut (spécial enseignant)
        self._dessiner_bandeau_enseignant(draw)

        # 2. Photo de l'enseignant (gauche)
        self._ajouter_photo_enseignant(carte, enseignant)

        # 3. Informations de l'enseignant (centre)
        self._ajouter_informations_enseignant(draw, enseignant)

        # 4. QR Code (droite)
        self._ajouter_qr_code_enseignant(carte, enseignant)

        # 5. Badge professionnel
        self._ajouter_badge_professionnel(draw, enseignant)

        # 6. Pied de page
        self._dessiner_pied_page(draw)

        # Sauvegarder
        output_dir = os.path.join('app', 'static', 'cartes')
        os.makedirs(output_dir, exist_ok=True)

        matricule = f"ENS{enseignant.id:05d}"
        filename = f"carte_enseignant_{matricule}_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(output_dir, filename)

        carte.save(filepath, 'PNG', quality=95, dpi=(300, 300))

        return filepath

    def _dessiner_bandeau_enseignant(self, draw):
        """Bandeau spécial pour les enseignants"""
        # Fond doré plus intense pour les enseignants
        for i in range(100):
            y = int(i * 1.2)
            color_r = int(184 + (218 - 184) * (i / 100))
            color_g = int(134 + (165 - 134) * (i / 100))
            color = (color_r, color_g, 11)
            draw.rectangle([(0, y), (self.width, y + 2)], fill=color)

        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        draw.text((20, 20), "POLYTECH INFINITY", fill=self.color_white, font=font_title)
        draw.text((20, 55), "Carte Enseignant 2025-2026", fill=self.color_white, font=font_sub)

    def _ajouter_photo_enseignant(self, carte, enseignant):
        """Ajouter la photo de l'enseignant"""
        photo_size = 150
        photo_x = 30
        photo_y = 130

        try:
            # Essayer de charger la photo de profil
            if hasattr(enseignant, 'user') and enseignant.user and hasattr(enseignant.user, 'avatar_url'):
                photo_path = os.path.join('app', 'static', enseignant.user.avatar_url)
                photo = Image.open(photo_path)
            else:
                # Créer un placeholder avec initiales
                photo = self._creer_avatar_initiales_enseignant(enseignant, photo_size)
        except:
            # Fallback
            photo = self._creer_avatar_initiales_enseignant(enseignant, photo_size)

        # Redimensionner
        photo = photo.resize((photo_size, photo_size), Image.LANCZOS)
        photo = self._arrondir_image(photo, 20)

        # Coller
        carte.paste(photo, (photo_x, photo_y), photo)

        # Bordure dorée
        draw = ImageDraw.Draw(carte)
        draw.rectangle(
            [(photo_x - 2, photo_y - 2), (photo_x + photo_size + 2, photo_y + photo_size + 2)],
            outline=self.color_gold,
            width=3
        )

    def _creer_avatar_initiales_enseignant(self, enseignant, size):
        """Créer un avatar avec les initiales pour enseignant"""
        # Fond doré plus foncé pour enseignants
        avatar = Image.new('RGB', (size, size), self.color_gold)
        draw = ImageDraw.Draw(avatar)

        initiales = f"{enseignant.prenom[0]}{enseignant.nom[0]}".upper() if enseignant.prenom and enseignant.nom else "EN"

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), initiales, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) // 2
        y = (size - text_height) // 2

        draw.text((x, y), initiales, fill=self.color_white, font=font)

        return avatar

    def _ajouter_informations_enseignant(self, draw, enseignant):
        """Ajouter les informations de l'enseignant"""
        x = 210
        y_start = 140

        try:
            font_nom = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font_nom = ImageFont.load_default()
            font_info = ImageFont.load_default()
            font_label = ImageFont.load_default()

        # Nom complet avec titre
        titre = "M." if enseignant.sexe == 'M' else "Mme"
        nom_complet = f"{titre} {enseignant.prenom} {enseignant.nom}".upper()
        draw.text((x, y_start), nom_complet, fill=self.color_black, font=font_nom)

        # Matricule
        y_start += 40
        matricule = f"ENS{enseignant.id:05d}"
        draw.text((x, y_start), "Matricule:", fill=self.color_gray, font=font_label)
        draw.text((x, y_start + 18), matricule, fill=self.color_gold, font=font_info)

        # Grade
        if enseignant.grade:
            y_start += 50
            draw.text((x, y_start), "Grade:", fill=self.color_gray, font=font_label)
            draw.text((x, y_start + 18), enseignant.grade[:25], fill=self.color_black, font=font_info)

        # Spécialité
        if enseignant.specialite:
            y_start += 50
            draw.text((x, y_start), "Spécialité:", fill=self.color_gray, font=font_label)
            draw.text((x, y_start + 18), enseignant.specialite[:25], fill=self.color_black, font=font_info)

    def _ajouter_qr_code_enseignant(self, carte, enseignant):
        """Ajouter un QR code pour l'enseignant"""
        matricule = f"ENS{enseignant.id:05d}"
        qr_data = f"POLYTECH-{matricule}-{enseignant.nom}-{enseignant.prenom}-ENSEIGNANT"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=4,
            border=1,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color=self.color_gold, back_color=self.color_white)
        qr_image = qr_image.resize((120, 120))

        qr_x = self.width - 150
        qr_y = 140

        carte.paste(qr_image, (qr_x, qr_y))

        draw = ImageDraw.Draw(carte)
        try:
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font_small = ImageFont.load_default()

        draw.text((qr_x + 30, qr_y + 125), "Scanner", fill=self.color_gray, font=font_small)

    def _ajouter_badge_professionnel(self, draw, enseignant):
        """Ajouter un badge professionnel"""
        badge_x = self.width - 60
        badge_y = 380

        # Cercle doré avec texte grade
        draw.ellipse(
            [(badge_x, badge_y), (badge_x + 40, badge_y + 40)],
            fill=self.color_gold,
            outline=self.color_gold_light,
            width=2
        )

        try:
            font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
        except:
            font_tiny = ImageFont.load_default()

        # Afficher l'initiale du grade
        grade_initial = enseignant.grade[0] if enseignant.grade else "P"
        draw.text((badge_x + 15, badge_y + 13), grade_initial, fill=self.color_white, font=font_tiny)

    def _dessiner_bandeau_superieur(self, draw, etudiant):
        """Bandeau doré en haut avec le nom de l'université"""
        # Fond doré dégradé (simulé avec plusieurs rectangles)
        for i in range(100):
            y = int(i * 1.2)
            color_r = int(218 + (255 - 218) * (i / 100))
            color_g = int(165 + (215 - 165) * (i / 100))
            color = (color_r, color_g, 0)
            draw.rectangle([(0, y), (self.width, y + 2)], fill=color)

        # Texte
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        # Nom de l'université
        draw.text((20, 20), "POLYTECH INFINITY", fill=self.color_white, font=font_title)
        draw.text((20, 55), "Carte Étudiant 2025-2026", fill=self.color_white, font=font_sub)

    def _ajouter_photo(self, carte, etudiant):
        """Ajouter la photo de l'étudiant (ou placeholder)"""
        photo_size = 150
        photo_x = 30
        photo_y = 130

        try:
            # Essayer de charger la photo de profil
            if hasattr(etudiant, 'photo_url') and etudiant.photo_url:
                photo_path = os.path.join('app', 'static', etudiant.photo_url)
                photo = Image.open(photo_path)
            elif hasattr(etudiant, 'user') and etudiant.user and hasattr(etudiant.user, 'avatar_url'):
                photo_path = os.path.join('app', 'static', etudiant.user.avatar_url)
                photo = Image.open(photo_path)
            else:
                # Créer un placeholder avec initiales
                photo = self._creer_avatar_initiales(etudiant, photo_size)
        except:
            # Fallback: placeholder
            photo = self._creer_avatar_initiales(etudiant, photo_size)

        # Redimensionner et recadrer
        photo = photo.resize((photo_size, photo_size), Image.LANCZOS)

        # Arrondir les coins
        photo = self._arrondir_image(photo, 20)

        # Coller sur la carte
        carte.paste(photo, (photo_x, photo_y), photo)

        # Bordure dorée
        draw = ImageDraw.Draw(carte)
        draw.rectangle(
            [(photo_x - 2, photo_y - 2), (photo_x + photo_size + 2, photo_y + photo_size + 2)],
            outline=self.color_gold,
            width=3
        )

    def _creer_avatar_initiales(self, etudiant, size):
        """Créer un avatar avec les initiales"""
        avatar = Image.new('RGB', (size, size), self.color_gold_light)
        draw = ImageDraw.Draw(avatar)

        # Initiales
        initiales = f"{etudiant.prenom[0]}{etudiant.nom[0]}".upper() if etudiant.prenom and etudiant.nom else "ET"

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()

        # Centrer le texte
        bbox = draw.textbbox((0, 0), initiales, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) // 2
        y = (size - text_height) // 2

        draw.text((x, y), initiales, fill=self.color_white, font=font)

        return avatar

    def _arrondir_image(self, image, radius):
        """Arrondir les coins d'une image"""
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius, fill=255)

        output = Image.new('RGBA', image.size, (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)

        return output

    def _ajouter_informations(self, draw, etudiant):
        """Ajouter les informations de l'étudiant"""
        x = 210
        y_start = 140

        try:
            font_nom = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font_nom = ImageFont.load_default()
            font_info = ImageFont.load_default()
            font_label = ImageFont.load_default()

        # Nom complet
        nom_complet = f"{etudiant.prenom} {etudiant.nom}".upper()
        draw.text((x, y_start), nom_complet, fill=self.color_black, font=font_nom)

        # Matricule
        y_start += 40
        draw.text((x, y_start), "Matricule:", fill=self.color_gray, font=font_label)
        draw.text((x, y_start + 18), etudiant.matricule, fill=self.color_gold, font=font_info)

        # Classe/Filière
        if etudiant.classe:
            y_start += 50
            draw.text((x, y_start), "Classe:", fill=self.color_gray, font=font_label)
            classe_nom = f"{etudiant.classe.nom_classe}"
            if etudiant.classe.filiere:
                classe_nom += f" - {etudiant.classe.filiere.nom_filiere}"
            draw.text((x, y_start + 18), classe_nom[:30], fill=self.color_black, font=font_info)

        # Année universitaire
        y_start += 50
        draw.text((x, y_start), "Année:", fill=self.color_gray, font=font_label)
        draw.text((x, y_start + 18), "2025-2026", fill=self.color_black, font=font_info)

    def _ajouter_qr_code(self, carte, etudiant):
        """Ajouter un QR code avec les infos de l'étudiant"""
        # Données du QR code
        qr_data = f"POLYTECH-{etudiant.matricule}-{etudiant.nom}-{etudiant.prenom}"

        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=4,
            border=1,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color=self.color_gold, back_color=self.color_white)
        qr_image = qr_image.resize((120, 120))

        # Position
        qr_x = self.width - 150
        qr_y = 140

        # Coller
        carte.paste(qr_image, (qr_x, qr_y))

        # Label
        draw = ImageDraw.Draw(carte)
        try:
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font_small = ImageFont.load_default()

        draw.text((qr_x + 30, qr_y + 125), "Scanner", fill=self.color_gray, font=font_small)

    def _ajouter_badge_nfc(self, draw):
        """Ajouter un badge NFC virtuel"""
        # Icône NFC (simulée)
        nfc_x = self.width - 60
        nfc_y = 380

        # Cercle doré
        draw.ellipse(
            [(nfc_x, nfc_y), (nfc_x + 40, nfc_y + 40)],
            fill=self.color_gold_light,
            outline=self.color_gold,
            width=2
        )

        # Texte NFC
        try:
            font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        except:
            font_tiny = ImageFont.load_default()

        draw.text((nfc_x + 8, nfc_y + 13), "NFC", fill=self.color_white, font=font_tiny)

    def _dessiner_pied_page(self, draw):
        """Dessiner le pied de page avec signature du directeur"""
        y = self.height - 60

        # Ligne dorée
        draw.line([(20, y), (self.width - 20, y)], fill=self.color_gold, width=2)

        # Texte
        try:
            font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            font_signature = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 11)
        except:
            font_tiny = ImageFont.load_default()
            font_signature = ImageFont.load_default()

        y += 10
        draw.text((20, y), "www.polytech-infinity.com", fill=self.color_gray, font=font_tiny)
        draw.text((self.width - 200, y), f"Émise le: {datetime.now().strftime('%d/%m/%Y')}", fill=self.color_gray, font=font_tiny)

        # Signature du directeur
        y += 18
        from app.models import User
        directeur = User.query.filter_by(role='DIRECTEUR').first()
        directeur_nom = f"Le Directeur: {directeur.username}" if directeur else "Le Directeur"
        draw.text((self.width - 200, y), directeur_nom, fill=self.color_gold, font=font_signature)


# Note: SignatureDocument est maintenant défini dans app/models.py
