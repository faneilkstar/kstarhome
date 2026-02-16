class SignatureDocument(db.Model):
    """Signatures numériques des documents"""
    __tablename__ = 'signatures_documents'

    id = db.Column(db.Integer, primary_key=True)

    # Document signé
    document_type = db.Column(db.String(50), nullable=False)  # attestation, releve, etc.
    document_id = db.Column(db.Integer, nullable=False)

    # Code de vérification
    code_verification = db.Column(db.String(50), unique=True, nullable=False)

    # Signature numérique
    signature_numerique = db.Column(db.Text)  # Signature RSA en hex

    # QR Code
    qr_code_path = db.Column(db.String(500))

    # Métadonnées
    date_signature = db.Column(db.DateTime, default=datetime.utcnow)
    valide = db.Column(db.Boolean, default=True)

    # Index pour recherche rapide
    __table_args__ = (
        db.Index('idx_code_verification', 'code_verification'),
        db.Index('idx_document', 'document_type', 'document_id'),
    )

    def __repr__(self):
        return f'<SignatureDocument {self.code_verification}>'