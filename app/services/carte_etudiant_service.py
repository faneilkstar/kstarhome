"""
Service de génération de cartes d'étudiant et enseignant
Design blanc et doré avec photo, QR code, logo, cachet, directeur
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app import db


# Chemin de base du projet (PythonProject3/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')


def _get_font(name, size):
    """Helper pour charger une police DejaVu"""
    fonts = {
        'bold': "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        'regular': "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        'italic': "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    }
    try:
        return ImageFont.truetype(fonts.get(name, fonts['regular']), size)
    except:
        return ImageFont.load_default()


def _get_config_ecole():
    """Récupère la config école depuis la DB"""
    try:
        from app.models import ConfigurationEcole
        return ConfigurationEcole.query.first()
    except:
        return None


def _get_directeur_nom():
    """Récupère le nom du directeur"""
    config = _get_config_ecole()
    if config and config.nom_directeur:
        return config.nom_directeur
    from app.models import User
    directeur = User.query.filter_by(role='DIRECTEUR').first()
    return directeur.username if directeur else "Le Directeur"


def _charger_logo():
    """Charge le logo de l'école"""
    config = _get_config_ecole()
    logo_path = None

    if config and config.logo_path:
        for p in [
            config.logo_path,
            os.path.join(STATIC_DIR, config.logo_path),
            os.path.join(BASE_DIR, config.logo_path),
        ]:
            if os.path.exists(p):
                logo_path = p
                break

    if not logo_path:
        for c in [
            os.path.join(STATIC_DIR, 'branding', 'logo_principal.png'),
            os.path.join(STATIC_DIR, 'branding', 'logo_header.png'),
            os.path.join(STATIC_DIR, 'images', 'logo_ecole.png'),
            os.path.join(STATIC_DIR, 'images', 'logo.png'),
        ]:
            if os.path.exists(c):
                logo_path = c
                break

    if logo_path:
        try:
            return Image.open(logo_path)
        except:
            pass
    return None


def _charger_cachet():
    """Charge le cachet/tampon de l'école"""
    config = _get_config_ecole()
    cachet_path = None

    if config and hasattr(config, 'cachet_path') and config.cachet_path:
        for p in [
            config.cachet_path,
            os.path.join(STATIC_DIR, config.cachet_path),
            os.path.join(BASE_DIR, config.cachet_path),
        ]:
            if os.path.exists(p):
                cachet_path = p
                break

    if not cachet_path:
        for c in [
            os.path.join(STATIC_DIR, 'branding', 'cachet.png'),
            os.path.join(STATIC_DIR, 'branding', 'logo_cachet.png'),
            os.path.join(STATIC_DIR, 'images', 'cachet.png'),
        ]:
            if os.path.exists(c):
                cachet_path = c
                break

    if cachet_path:
        try:
            return Image.open(cachet_path).convert('RGBA')
        except:
            pass
    return None


def _charger_photo_personne(user_obj):
    """Charge la photo de profil d'un user"""
    if not user_obj:
        return None
    avatar = getattr(user_obj, 'avatar', None)
    if avatar:
        for p in [
            os.path.join(STATIC_DIR, 'avatars', avatar),
            os.path.join(STATIC_DIR, avatar),
            os.path.join(STATIC_DIR, 'uploads', 'photos', avatar),
        ]:
            if os.path.exists(p):
                try:
                    return Image.open(p)
                except:
                    pass
    return None


class CarteEtudiantService:
    """Service pour générer des cartes d'étudiant/enseignant modernes"""

    NOM_DIRECTEUR = "Prof. KOISSI-ZO T. Constantin"

    def __init__(self):
        self.width = 1012
        self.height = 638

        self.GOLD = (218, 165, 32)
        self.GOLD_LIGHT = (255, 215, 0)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.DARK = (40, 40, 40)

        self.font_title = _get_font('bold', 26)
        self.font_sub = _get_font('regular', 13)
        self.font_nom = _get_font('bold', 22)
        self.font_info = _get_font('regular', 15)
        self.font_label = _get_font('regular', 11)
        self.font_small = _get_font('regular', 10)
        self.font_tiny = _get_font('italic', 9)
        self.font_directeur = _get_font('italic', 10)

        self.output_dir = os.path.join(STATIC_DIR, 'cartes')
        os.makedirs(self.output_dir, exist_ok=True)

    # ================================================================
    # CARTE ÉTUDIANT
    # ================================================================
    def generer_carte_complete(self, etudiant):
        carte = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw = ImageDraw.Draw(carte)

        self._bandeau_haut(carte, draw, "CARTE ÉTUDIANT 2025-2026")
        self._photo(carte, etudiant.user if etudiant.user else None, etudiant)
        self._infos_etudiant(draw, etudiant)
        self._qr_code(carte, self._qr_data_etudiant(etudiant))
        self._cachet_et_directeur(carte, draw)
        self._pied_de_page(draw)

        filename = f"carte_{etudiant.get_matricule()}_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.output_dir, filename)
        carte.save(filepath, 'PNG', quality=95, dpi=(300, 300))
        return filepath

    # ================================================================
    # CARTE ENSEIGNANT
    # ================================================================
    def generer_carte_enseignant(self, enseignant):
        carte = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw = ImageDraw.Draw(carte)

        self._bandeau_haut(carte, draw, "CARTE ENSEIGNANT 2025-2026")
        self._photo(carte, enseignant.user if enseignant.user else None, enseignant)
        self._infos_enseignant(draw, enseignant)
        self._qr_code(carte, self._qr_data_enseignant(enseignant))
        self._cachet_et_directeur(carte, draw)
        self._pied_de_page(draw)

        matricule = f"ENS{enseignant.id:05d}"
        filename = f"carte_enseignant_{matricule}_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.output_dir, filename)
        carte.save(filepath, 'PNG', quality=95, dpi=(300, 300))
        return filepath

    # ================================================================
    # BANDEAU HAUT
    # ================================================================
    def _bandeau_haut(self, carte, draw, sous_titre):
        h_bandeau = 110
        for i in range(h_bandeau):
            ratio = i / h_bandeau
            r = int(180 + (218 - 180) * ratio)
            g = int(130 + (165 - 130) * ratio)
            b = int(5 + (32 - 5) * ratio)
            draw.rectangle([(0, i), (self.width, i + 1)], fill=(r, g, b))

        logo = _charger_logo()
        logo_offset = 20
        if logo:
            logo_h = 70
            ratio = logo_h / logo.size[1]
            logo_w = int(logo.size[0] * ratio)
            logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)
            y_logo = (h_bandeau - logo_h) // 2
            try:
                carte.paste(logo_resized, (15, y_logo), logo_resized.convert('RGBA'))
            except:
                carte.paste(logo_resized, (15, y_logo))
            logo_offset = 15 + logo_w + 12

        config = _get_config_ecole()
        nom_ecole = config.nom_ecole if config and config.nom_ecole else "POLYTECH INFINITY"
        draw.text((logo_offset, 18), nom_ecole.upper(), fill=self.WHITE, font=self.font_title)
        draw.text((logo_offset, 52), sous_titre, fill=self.WHITE, font=self.font_sub)
        draw.text((self.width - 170, 18), "2025 - 2026", fill=self.WHITE, font=self.font_sub)
        draw.rectangle([(0, h_bandeau - 3), (self.width, h_bandeau)], fill=self.GOLD_LIGHT)

    # ================================================================
    # PHOTO
    # ================================================================
    def _photo(self, carte, user_obj, personne):
        photo_size = 160
        photo_x = 30
        photo_y = 130

        photo = _charger_photo_personne(user_obj)
        if not photo:
            prenom = getattr(personne, 'prenom', '') or ''
            nom = getattr(personne, 'nom', '') or ''
            initiales = f"{prenom[:1]}{nom[:1]}".upper() or "??"
            photo = self._avatar_initiales(initiales, photo_size)

        photo = photo.resize((photo_size, photo_size), Image.LANCZOS)
        photo = self._arrondir(photo, 18)
        carte.paste(photo, (photo_x, photo_y), photo)

        draw = ImageDraw.Draw(carte)
        draw.rounded_rectangle(
            [(photo_x - 3, photo_y - 3),
             (photo_x + photo_size + 3, photo_y + photo_size + 3)],
            radius=20, outline=self.GOLD, width=3
        )

    # ================================================================
    # INFOS ÉTUDIANT
    # ================================================================
    def _infos_etudiant(self, draw, etudiant):
        x = 220
        y = 130

        nom_complet = f"{(etudiant.nom or '').upper()} {(etudiant.prenom or '').title()}"
        draw.text((x, y), nom_complet, fill=self.BLACK, font=self.font_nom)
        y += 32

        draw.text((x, y), "Matricule :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), etudiant.get_matricule(), fill=self.GOLD, font=self.font_info)
        y += 26

        date_naiss = ""
        if etudiant.date_naissance:
            try:
                date_naiss = etudiant.date_naissance.strftime('%d/%m/%Y')
            except:
                date_naiss = str(etudiant.date_naissance)
        draw.text((x, y), "Né(e) le :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), date_naiss or "N/A", fill=self.DARK, font=self.font_info)
        y += 26

        sexe_txt = etudiant.sexe or "N/A"
        if sexe_txt == 'M':
            sexe_txt = 'Masculin'
        elif sexe_txt == 'F':
            sexe_txt = 'Féminin'
        draw.text((x, y), "Sexe :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), sexe_txt, fill=self.DARK, font=self.font_info)
        y += 26

        classe_txt = ""
        if etudiant.classe:
            classe_txt = etudiant.classe.nom_classe or ""
            if etudiant.classe.filiere:
                classe_txt += f" ({etudiant.classe.filiere.nom_filiere})"
        draw.text((x, y), "Classe :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), (classe_txt or "N/A")[:40], fill=self.DARK, font=self.font_info)
        y += 26

        dept_txt = ""
        if etudiant.classe and etudiant.classe.filiere:
            filiere = etudiant.classe.filiere
            if hasattr(filiere, 'departement') and filiere.departement:
                dept_txt = filiere.departement.nom
        draw.text((x, y), "Départ. :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), (dept_txt or "N/A")[:35], fill=self.DARK, font=self.font_info)
        y += 26

        nat = etudiant.nationalite or "N/A"
        draw.text((x, y), "Nationalité :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 95, y), nat[:25], fill=self.DARK, font=self.font_info)

    # ================================================================
    # INFOS ENSEIGNANT
    # ================================================================
    def _infos_enseignant(self, draw, enseignant):
        x = 220
        y = 130

        titre = "M." if enseignant.sexe == 'M' else "Mme" if enseignant.sexe == 'F' else ""
        nom_complet = f"{titre} {(enseignant.nom or '').upper()} {(enseignant.prenom or '').title()}"
        draw.text((x, y), nom_complet.strip(), fill=self.BLACK, font=self.font_nom)
        y += 32

        matricule = f"ENS{enseignant.id:05d}"
        draw.text((x, y), "Matricule :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), matricule, fill=self.GOLD, font=self.font_info)
        y += 26

        date_naiss = ""
        if enseignant.date_naissance:
            try:
                date_naiss = enseignant.date_naissance.strftime('%d/%m/%Y')
            except:
                date_naiss = str(enseignant.date_naissance)
        draw.text((x, y), "Né(e) le :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), date_naiss or "N/A", fill=self.DARK, font=self.font_info)
        y += 26

        sexe_txt = enseignant.sexe or "N/A"
        if sexe_txt == 'M':
            sexe_txt = 'Masculin'
        elif sexe_txt == 'F':
            sexe_txt = 'Féminin'
        draw.text((x, y), "Sexe :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), sexe_txt, fill=self.DARK, font=self.font_info)
        y += 26

        grade = enseignant.grade or "N/A"
        draw.text((x, y), "Grade :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), grade[:30], fill=self.DARK, font=self.font_info)
        y += 26

        spec = enseignant.specialite or "N/A"
        draw.text((x, y), "Spécialité :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 90, y), spec[:30], fill=self.DARK, font=self.font_info)
        y += 26

        dept_txt = ""
        # Méthode robuste : requête directe au lieu du backref (évite InstrumentedList)
        try:
            from app.models import Departement
            dept_chef = Departement.query.filter_by(chef_id=enseignant.id, active=True).first()
            if dept_chef:
                dept_txt = f"Chef - {dept_chef.nom}"
        except Exception:
            pass
        if not dept_txt and enseignant.ues:
            for ue in enseignant.ues:
                if ue.departement:
                    dept_txt = ue.departement.nom
                    break
        draw.text((x, y), "Départ. :", fill=self.GRAY, font=self.font_label)
        draw.text((x + 80, y), (dept_txt or "N/A")[:35], fill=self.DARK, font=self.font_info)

    # ================================================================
    # QR CODE
    # ================================================================
    def _qr_code(self, carte, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=4, border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=self.GOLD, back_color=self.WHITE)
        qr_img = qr_img.resize((130, 130))
        qr_x = self.width - 165
        qr_y = 130
        carte.paste(qr_img, (qr_x, qr_y))
        draw = ImageDraw.Draw(carte)
        draw.text((qr_x + 35, qr_y + 135), "Scanner QR", fill=self.GRAY, font=self.font_small)

    def _qr_data_etudiant(self, etudiant):
        classe = etudiant.classe.nom_classe if etudiant.classe else "N/A"
        return f"POLYTECH|ETU|{etudiant.get_matricule()}|{etudiant.nom}|{etudiant.prenom}|{classe}"

    def _qr_data_enseignant(self, enseignant):
        return f"POLYTECH|ENS|ENS{enseignant.id:05d}|{enseignant.nom}|{enseignant.prenom}|{enseignant.grade or 'N/A'}"

    # ================================================================
    # CACHET + DIRECTEUR
    # ================================================================
    def _cachet_et_directeur(self, carte, draw):
        x_zone = self.width - 320
        y_zone = self.height - 200

        cachet = _charger_cachet()
        if cachet:
            cachet_size = 280  # Taille très agrandie (était 200, puis 130)
            cachet_resized = cachet.resize((cachet_size, cachet_size), Image.LANCZOS)
            try:
                carte.paste(cachet_resized, (x_zone - 50, y_zone - 60), cachet_resized)
            except:
                carte.paste(cachet_resized, (x_zone - 50, y_zone - 60))
        else:
            draw.ellipse([(x_zone, y_zone), (x_zone + 200, y_zone + 200)], outline=self.GOLD, width=4)
            draw.text((x_zone + 50, y_zone + 80), "CACHET", fill=self.GOLD, font=self.font_info)

        directeur = _get_directeur_nom()
        if not directeur or directeur == "Le Directeur":
            directeur = self.NOM_DIRECTEUR

        draw.text((x_zone + 120, y_zone + 5), "Le Directeur", fill=self.GRAY, font=self.font_label)
        draw.text((x_zone + 120, y_zone + 20), directeur, fill=self.DARK, font=self.font_directeur)
        draw.line([(x_zone + 120, y_zone + 42), (x_zone + 270, y_zone + 42)], fill=self.GOLD, width=1)

    # ================================================================
    # PIED DE PAGE
    # ================================================================
    def _pied_de_page(self, draw):
        y = self.height - 45
        draw.line([(15, y), (self.width - 15, y)], fill=self.GOLD, width=2)
        y += 8

        config = _get_config_ecole()
        site = config.site_web if config and config.site_web else "www.polytech-infinity.com"
        tel = config.telephone if config and config.telephone else ""

        draw.text((20, y), site, fill=self.GRAY, font=self.font_tiny)
        if tel:
            draw.text((250, y), f"Tél: {tel}", fill=self.GRAY, font=self.font_tiny)
        draw.text((self.width - 200, y), f"Émise le: {datetime.now().strftime('%d/%m/%Y')}", fill=self.GRAY, font=self.font_tiny)

    # ================================================================
    # UTILITAIRES
    # ================================================================
    def _avatar_initiales(self, initiales, size):
        avatar = Image.new('RGB', (size, size), self.GOLD)
        draw = ImageDraw.Draw(avatar)
        font = _get_font('bold', size // 3)
        bbox = draw.textbbox((0, 0), initiales, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((size - tw) // 2, (size - th) // 2), initiales, fill=self.WHITE, font=font)
        return avatar

    def _arrondir(self, image, radius):
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius, fill=255)
        output = Image.new('RGBA', image.size, (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)
        return output

