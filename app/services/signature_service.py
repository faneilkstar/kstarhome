"""
Service de génération de signatures électroniques avec QR codes
"""

import os
import hashlib
import qrcode
from io import BytesIO
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class SignatureService:
    """Gestion des signatures électroniques"""

    def __init__(self):
        self.keys_dir = 'data/keys'
        self.qr_dir = 'static/qr_codes'
        os.makedirs(self.keys_dir, exist_ok=True)
        os.makedirs(self.qr_dir, exist_ok=True)

        # Charger ou générer les clés de l'école
        self.private_key, self.public_key = self._load_or_generate_keys()

    def _load_or_generate_keys(self):
        """Charge ou génère les clés RSA de l'école"""
        private_key_path = os.path.join(self.keys_dir, 'ecole_private.pem')
        public_key_path = os.path.join(self.keys_dir, 'ecole_public.pem')

        if os.path.exists(private_key_path) and os.path.exists(public_key_path):
            # Charger les clés existantes
            with open(private_key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )

            with open(public_key_path, 'rb') as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        else:
            # Générer de nouvelles clés
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

            public_key = private_key.public_key()

            # Sauvegarder
            with open(private_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            with open(public_key_path, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))

        return private_key, public_key

    def generer_code_verification(self, document_type, document_id, etudiant_id=None):
        """
        Génère un code de vérification unique

        Args:
            document_type: 'attestation', 'releve', 'certificat', etc.
            document_id: ID du document
            etudiant_id: ID de l'étudiant (si applicable)

        Returns:
            str: Code de vérification
        """
        # Créer une chaîne unique
        data = f"{document_type}_{document_id}_{etudiant_id}_{datetime.utcnow().isoformat()}"

        # Hash SHA-256
        hash_obj = hashlib.sha256(data.encode())
        code = hash_obj.hexdigest()[:16].upper()

        # Formater avec tirets
        return f"{code[:4]}-{code[4:8]}-{code[8:12]}-{code[12:]}"

    def signer_document(self, donnees_document):
        """
        Signe numériquement les données d'un document

        Args:
            donnees_document: Données à signer (dict)

        Returns:
            bytes: Signature numérique
        """
        # Convertir en JSON bytes
        import json
        message = json.dumps(donnees_document, sort_keys=True).encode()

        # Signer avec la clé privée
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature

    def verifier_signature(self, donnees_document, signature):
        """
        Vérifie la signature d'un document

        Args:
            donnees_document: Données du document
            signature: Signature à vérifier

        Returns:
            bool: True si valide
        """
        import json
        message = json.dumps(donnees_document, sort_keys=True).encode()

        try:
            self.public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def generer_qr_code(self, code_verification, url_verification=None):
        """
        Génère un QR code pour la vérification

        Args:
            code_verification: Code de vérification
            url_verification: URL de vérification (optionnel)

        Returns:
            str: Chemin du fichier QR code
        """
        if not url_verification:
            url_verification = f"https://harmony-school.tg/verifier/{code_verification}"

        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(url_verification)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Sauvegarder
        filename = f"qr_{code_verification.replace('-', '')}.png"
        filepath = os.path.join(self.qr_dir, filename)
        img.save(filepath)

        return filepath

    def generer_qr_code_base64(self, code_verification, url_verification=None):
        """Génère un QR code en base64 (pour embed dans PDF)"""
        if not url_verification:
            url_verification = f"https://harmony-school.tg/verifier/{code_verification}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(url_verification)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir en base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return img_str

    def enregistrer_signature_document(self, document_type, document_id, code_verification, signature):
        """Enregistre les métadonnées de signature dans la base"""
        from app.models import SignatureDocument
        from app import db

        signature_doc = SignatureDocument(
            document_type=document_type,
            document_id=document_id,
            code_verification=code_verification,
            signature_numerique=signature.hex(),  # Convertir bytes en hex
            date_signature=datetime.utcnow()
        )

        db.session.add(signature_doc)
        db.session.commit()

        return signature_doc