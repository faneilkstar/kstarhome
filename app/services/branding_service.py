"""
Service de gestion du branding et de la personnalisation
"""

import os
from PIL import Image, ImageDraw, ImageFont
from app import db
from app.models import ConfigurationEcole


class BrandingService:
    """Gestion du branding de l'école"""

    def __init__(self):
        self.config = ConfigurationEcole.query.first()
        if not self.config:
            # Créer la configuration par défaut
            self.config = ConfigurationEcole()
            db.session.add(self.config)
            db.session.commit()

    def get_config(self):
        """Récupère la configuration actuelle"""
        return self.config

    def update_config(self, data):
        """Met à jour la configuration"""
        for key, value in data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        db.session.commit()
        return self.config

    def upload_logo(self, file, type='principal'):
        """
        Upload et traite le logo

        Args:
            file: Fichier uploadé
            type: 'principal', 'header', 'filigrane'
        """
        upload_dir = 'static/branding'
        os.makedirs(upload_dir, exist_ok=True)

        # Nom du fichier
        filename = f"logo_{type}.png"
        filepath = os.path.join(upload_dir, filename)

        # Sauvegarder et optimiser
        img = Image.open(file)

        # Redimensionner selon le type
        if type == 'principal':
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
        elif type == 'header':
            img.thumbnail((200, 100), Image.Resampling.LANCZOS)
        elif type == 'filigrane':
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            # Rendre transparent pour filigrane
            img = img.convert('RGBA')
            img.putalpha(int(255 * 0.2))  # 20% opacité

        img.save(filepath, 'PNG', optimize=True)

        # Mettre à jour la config
        if type == 'principal':
            self.config.logo_path = filepath
        elif type == 'header':
            self.config.logo_header_path = filepath
        elif type == 'filigrane':
            self.config.filigrane_path = filepath

        db.session.commit()

        return filepath

    def generer_filigrane_texte(self, text=None):
        """Génère un filigrane texte si pas d'image"""
        if not text:
            text = self.config.nom_court or self.config.nom_ecole

        # Créer image
        img = Image.new('RGBA', (800, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()

        # Texte centré
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (800 - text_width) / 2
        y = (200 - text_height) / 2

        # Dessiner avec opacité
        draw.text((x, y), text, fill=(128, 128, 128, 50), font=font)

        # Rotation diagonale
        img = img.rotate(45, expand=True)

        filepath = 'static/branding/filigrane_texte.png'
        img.save(filepath, 'PNG')

        return filepath

    def get_css_variables(self):
        """Génère les variables CSS pour le thème"""
        return f"""
:root {{
    --primary-color: {self.config.couleur_primaire};
    --secondary-color: {self.config.couleur_secondaire};
    --accent-color: {self.config.couleur_accent};
    --logo-url: url('/{self.config.logo_path}');
}}
"""

    def get_footer_html(self):
        """Génère le HTML du footer avec coordonnées"""
        return f"""
<footer class="bg-dark text-white py-4 mt-5">
    <div class="container">
        <div class="row">
            <div class="col-md-4">
                <h5>{self.config.nom_ecole}</h5>
                <p class="small">{self.config.slogan or ''}</p>
            </div>
            <div class="col-md-4">
                <h6>Coordonnées</h6>
                <p class="small mb-0">
                    <i class="fas fa-map-marker-alt"></i> {self.config.adresse or ''}<br>
                    <i class="fas fa-phone"></i> {self.config.telephone or ''}<br>
                    <i class="fas fa-envelope"></i> {self.config.email or ''}
                </p>
            </div>
            <div class="col-md-4">
                <h6>Légal</h6>
                <p class="small mb-0">
                    Agrément N° {self.config.numero_agrement or 'XXX'}<br>
                    Registre N° {self.config.numero_registre or 'XXX'}<br>
                    © {self.config.annee_creation or 2024} - Tous droits réservés
                </p>
            </div>
        </div>
    </div>
</footer>
"""