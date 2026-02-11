from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Enum

# ============================================================
# 1. TABLE D'ASSOCIATION (Enseignant <-> UE)
# ============================================================
enseignant_ue = db.Table(
    'enseignant_ue',
    db.Column('enseignant_id', db.Integer, db.ForeignKey('enseignants.id', ondelete='CASCADE'), primary_key=True),
    db.Column('ue_id', db.Integer, db.ForeignKey('ues.id', ondelete='CASCADE'), primary_key=True),
    db.Column('date_attribution', db.DateTime, default=datetime.utcnow)
)


# ============================================================
# 2. UTILISATEUR (User)
# ============================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='ETUDIANT')
    statut = db.Column(db.String(20), default='actif')
    avatar = db.Column(db.String(200), nullable=True)  # Nom du fichier avatar
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relations One-to-One
    etudiant_profile = db.relationship('Etudiant', back_populates='user', uselist=False, cascade='all, delete-orphan')
    enseignant_profile = db.relationship('Enseignant', back_populates='user', uselist=False,
                                         cascade='all, delete-orphan')

    # Relations One-to-Many
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    actions = db.relationship('HistoriqueAction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('Le mot de passe n\'est pas lisible !')

    @password.setter
    def password(self, password_en_clair):
        self.password_hash = generate_password_hash(password_en_clair)

    def set_password(self, password_en_clair):
        """Méthode alternative pour définir le mot de passe"""
        self.password_hash = generate_password_hash(password_en_clair)

    def verify_password(self, password_en_clair):
        return check_password_hash(self.password_hash, password_en_clair)

    @property
    def is_directeur(self): return self.role == 'DIRECTEUR'

    @property
    def is_enseignant(self): return self.role == 'ENSEIGNANT'

    @property
    def is_etudiant(self): return self.role == 'ETUDIANT'

    def __repr__(self):
        return f'<User {self.username}>'


# ============================================================
# 3. FILIÈRE
# ============================================================
class Filiere(db.Model):
    __tablename__ = 'filieres'
    id = db.Column(db.Integer, primary_key=True)
    nom_filiere = db.Column(db.String(100), nullable=False, unique=True, index=True)
    code_filiere = db.Column(db.String(20), unique=True, index=True)
    cycle = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations (Corrigées)
    classes = db.relationship('Classe', back_populates='filiere', lazy='dynamic', cascade='all, delete-orphan')
    etudiants = db.relationship('Etudiant', back_populates='filiere_objet', lazy='dynamic')

    def get_nombre_classes(self):
        return self.classes.filter_by(active=True).count()

    def get_nombre_etudiants(self):
        total = 0
        for classe in self.classes.filter_by(active=True):
            total += classe.get_nombre_etudiants()
        return total


# ============================================================
# 4. CLASSE
# ============================================================
class Classe(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    nom_classe = db.Column(db.String(100), nullable=False, index=True)
    code_classe = db.Column(db.String(20), unique=True)
    cycle = db.Column(db.String(50))
    annee = db.Column(db.Integer)
    filiere_id = db.Column(db.Integer, db.ForeignKey('filieres.id', ondelete='CASCADE'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    capacite_max = db.Column(db.Integer)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations (Corrigées)
    filiere = db.relationship('Filiere', back_populates='classes')
    etudiants = db.relationship('Etudiant', back_populates='classe', lazy='dynamic')
    ues = db.relationship('UE', back_populates='classe', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', back_populates='classe', lazy='dynamic')

    def get_nombre_etudiants(self):
        return self.etudiants.filter_by(statut_inscription='accepté').count()

    def get_nombre_ues(self):
        return self.ues.count()

    def est_pleine(self):
        if not self.capacite_max: return False
        return self.get_nombre_etudiants() >= self.capacite_max


# ============================================================
# 5. ÉTUDIANT
# ============================================================
class Etudiant(db.Model):
    __tablename__ = 'etudiants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Identité
    numero_inscription = db.Column(db.String(50), unique=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    date_naissance = db.Column(db.Date)
    lieu_naissance = db.Column(db.String(100))
    sexe = db.Column(db.String(10))
    nationalite = db.Column(db.String(50), default='Togolaise')
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    situation_matrimoniale = db.Column(db.String(50))  # Ajouté
    contact_urgence = db.Column(db.String(20))
    nom_pere = db.Column(db.String(100))
    nom_mere = db.Column(db.String(100))

    # Scolaire
    moyenne_bac = db.Column(db.Float)
    serie_bac = db.Column(db.String(10))
    moyenne_licence = db.Column(db.Float)
    diplome_licence = db.Column(db.String(100))

    statut_inscription = db.Column(db.String(20), default='en_attente')
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    annee_academique = db.Column(db.String(20))
    evaluation_ia = db.Column(db.Text)  # Résultat de l'évaluation automatique par l'IA

    # Clés étrangères
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'))
    filiere_id = db.Column(db.Integer, db.ForeignKey('filieres.id', ondelete='SET NULL'))

    # Relations (Corrigées)
    user = db.relationship('User', back_populates='etudiant_profile')
    classe = db.relationship('Classe', back_populates='etudiants')
    filiere_objet = db.relationship('Filiere', back_populates='etudiants')

    notes = db.relationship('Note', backref='etudiant', lazy='dynamic', cascade='all, delete-orphan')
    inscriptions_ue = db.relationship('InscriptionUE', back_populates='etudiant', lazy='dynamic',
                                      cascade='all, delete-orphan')
    diplome_obj = db.relationship('Diplome', back_populates='etudiant', uselist=False)
    absences = db.relationship('Absence', backref='etudiant', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def nom_complet(self):
        n = self.nom.upper() if self.nom else ""
        p = self.prenom.title() if self.prenom else ""
        return f"{n} {p}".strip()

    def get_matricule(self):
        if self.numero_inscription: return self.numero_inscription
        return f"TEMP-{self.id:04d}"

    def get_moyenne_generale(self):
        valides = [n.note for n in self.notes.all() if n.note is not None]
        if not valides: return 0.0
        return round(sum(valides) / len(valides), 2)


# ============================================================
# 6. ENSEIGNANT
# ============================================================
class Enseignant(db.Model):
    __tablename__ = 'enseignants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)

    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    date_naissance = db.Column(db.Date)
    sexe = db.Column(db.String(10))
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    grade = db.Column(db.String(50))
    specialite = db.Column(db.String(100))
    date_embauche = db.Column(db.Date)
    actif = db.Column(db.Boolean, default=True)
    mot_de_passe_initial = db.Column(db.String(255))  # Mot de passe en clair pour le PDF

    # Relations
    user = db.relationship('User', back_populates='enseignant_profile')
    ues = db.relationship('UE', secondary=enseignant_ue, back_populates='enseignants')
    documents = db.relationship('Document', back_populates='enseignant', lazy='dynamic')
    emplois_temps = db.relationship('EmploiTemps', backref='enseignant', lazy='dynamic')

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def get_nombre_ues(self):
        return len(self.ues)


# ============================================================
# 7. UNITÉ D'ENSEIGNEMENT (UE)
# ============================================================
class UE(db.Model):
    __tablename__ = 'ues'
    id = db.Column(db.Integer, primary_key=True)
    code_ue = db.Column(db.String(20), unique=True, nullable=False)
    intitule = db.Column(db.String(200), nullable=False)
    nom_ue = db.Column(db.String(100))  # Alias
    description = db.Column(db.Text)
    heures = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer)
    coefficient = db.Column(db.Integer, default=1)
    semestre = db.Column(db.Integer)
    type_ue = db.Column(db.String(20), default='Obligatoire')

    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)

    # Relations
    classe = db.relationship('Classe', back_populates='ues')
    enseignants = db.relationship('Enseignant', secondary=enseignant_ue, back_populates='ues')
    inscriptions = db.relationship('InscriptionUE', back_populates='ue', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='ue_parent', lazy='dynamic', cascade='all, delete-orphan')
    absences = db.relationship('Absence', backref='ue_concernee', lazy='dynamic', cascade='all, delete-orphan')
    emploi_temps = db.relationship('EmploiTemps', backref='ue_associee', lazy='dynamic', cascade='all, delete-orphan')

    def get_nombre_etudiants(self):
        return self.inscriptions.filter_by(statut='validé').count()

    def get_moyenne_ue(self):
        notes_list = [n.note for n in self.notes.all() if n.note is not None]
        if not notes_list: return None
        return round(sum(notes_list) / len(notes_list), 2)

    def get_taux_reussite(self):
        """Retourne le taux de réussite (% de notes >= 10)"""
        notes_list = [n.note for n in self.notes.all() if n.note is not None]
        if not notes_list: return 0
        notes_reussies = [n for n in notes_list if n >= 10]
        return round((len(notes_reussies) / len(notes_list)) * 100, 1)

    def has_composantes(self):
        """Vérifie si l'UE a des composantes de notes configurées"""
        return self.composantes.filter_by(active=True).count() > 0

    def get_composantes_actives(self):
        """Retourne les composantes actives triées par ordre"""
        return self.composantes.filter_by(active=True).order_by(ComposanteNote.ordre).all()

    def get_total_ponderation(self):
        """Calcule la somme des pondérations (devrait être 100)"""
        return sum([c.ponderation for c in self.get_composantes_actives()])

    def calculer_note_finale_etudiant(self, etudiant_id):
        """
        Calcule la note finale d'un étudiant pour cette UE en fonction des composantes pondérées
        """
        composantes = self.get_composantes_actives()
        if not composantes:
            # Système classique : une seule note
            note_obj = Note.query.filter_by(
                etudiant_id=etudiant_id,
                ue_id=self.id,
                composante_id=None
            ).first()
            return note_obj.note if note_obj and note_obj.note is not None else None

        # Système avec pondération
        note_finale = 0
        ponderation_totale = 0

        for composante in composantes:
            note_obj = Note.query.filter_by(
                etudiant_id=etudiant_id,
                ue_id=self.id,
                composante_id=composante.id
            ).first()

            if note_obj and note_obj.note is not None:
                note_finale += note_obj.note * (composante.ponderation / 100)
                ponderation_totale += composante.ponderation

        # Si toutes les composantes ne sont pas notées, on retourne None
        if ponderation_totale < 100:
            return None

        return round(note_finale, 2)


# ============================================================
# 8. INSCRIPTION UE
# ============================================================
class InscriptionUE(db.Model):
    __tablename__ = 'inscriptions_ue'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    ue_id = db.Column(db.Integer, db.ForeignKey('ues.id', ondelete='CASCADE'), nullable=False)
    annee_academique = db.Column(db.String(20))
    statut = db.Column(db.String(20), default='validé')
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)

    etudiant = db.relationship('Etudiant', back_populates='inscriptions_ue')
    ue = db.relationship('UE', back_populates='inscriptions')


# ============================================================
# 9. DOCUMENT (Corrigé date_upload -> date_creation)
# ============================================================
class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    nom_fichier = db.Column(db.String(200), nullable=False)
    type_doc = db.Column(db.String(50), default='cours')
    description = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'))

    classe = db.relationship('Classe', back_populates='documents')
    enseignant = db.relationship('Enseignant', back_populates='documents')


# ============================================================
# 10. AUTRES TABLES (Remises intégralement)
# ============================================================

# ============================================================
# SYSTÈME DE PONDÉRATION DES NOTES
# ============================================================
class ComposanteNote(db.Model):
    """Configuration des composantes d'évaluation pour chaque UE"""
    __tablename__ = 'composantes_notes'
    id = db.Column(db.Integer, primary_key=True)
    ue_id = db.Column(db.Integer, db.ForeignKey('ues.id', ondelete='CASCADE'), nullable=False)
    nom = db.Column(db.String(50), nullable=False)  # Ex: "Examen", "Devoir", "TP", "Projet"
    ponderation = db.Column(db.Float, nullable=False)  # Ex: 50.0 pour 50%
    ordre = db.Column(db.Integer, default=1)  # Pour trier les composantes
    active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    ue = db.relationship('UE', backref=db.backref('composantes', lazy='dynamic', cascade='all, delete-orphan'))
    notes = db.relationship('Note', back_populates='composante', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ComposanteNote {self.nom} - {self.ponderation}%>'


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    ue_id = db.Column(db.Integer, db.ForeignKey('ues.id', ondelete='CASCADE'), nullable=False)
    composante_id = db.Column(db.Integer, db.ForeignKey('composantes_notes.id', ondelete='SET NULL'), nullable=True)
    note = db.Column(db.Float)
    session = db.Column(db.String(20), default='normale')
    annee_academique = db.Column(db.String(20))
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow)
    saisi_par_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relations
    composante = db.relationship('ComposanteNote', back_populates='notes')

    def est_valide(self):
        return self.note is not None and self.note >= 10

    def __repr__(self):
        comp = self.composante.nom if self.composante else "Générale"
        return f'<Note {comp}: {self.note}/20>'


class Absence(db.Model):
    __tablename__ = 'absences'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    ue_id = db.Column(db.Integer, db.ForeignKey('ues.id', ondelete='CASCADE'), nullable=False)
    date_absence = db.Column(db.Date, nullable=False)
    justifiee = db.Column(db.Boolean, default=False)
    motif = db.Column(db.Text)
    document_justificatif = db.Column(db.String(500))


class EmploiTemps(db.Model):
    __tablename__ = 'emploi_temps'
    id = db.Column(db.Integer, primary_key=True)
    ue_id = db.Column(db.Integer, db.ForeignKey('ues.id', ondelete='CASCADE'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id', ondelete='SET NULL'))
    jour = db.Column(db.String(20), nullable=False)
    heure_debut = db.Column(db.String(10), nullable=False)
    heure_fin = db.Column(db.String(10), nullable=False)
    salle = db.Column(db.String(50))
    type_cours = db.Column(db.String(20))  # CM, TD, TP


class Annonce(db.Model):
    __tablename__ = 'annonces'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    visible_etudiants = db.Column(db.Boolean, default=True)
    visible_enseignants = db.Column(db.Boolean, default=True)
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)
    auteur_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    titre = db.Column(db.String(200))
    message = db.Column(db.Text)
    type = db.Column(db.String(20), default='info')
    lue = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)


class Statistique(db.Model):
    __tablename__ = 'statistiques'
    id = db.Column(db.Integer, primary_key=True)
    type_stat = db.Column(db.String(50))
    cle = db.Column(db.String(100))
    valeur = db.Column(db.Float)
    date_calcul = db.Column(db.DateTime, default=datetime.utcnow)


class HistoriqueAction(db.Model):
    __tablename__ = 'historique_actions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    table_cible = db.Column(db.String(50))
    id_cible = db.Column(db.Integer)
    details = db.Column(db.Text)
    date_action = db.Column(db.DateTime, default=datetime.utcnow)


class Diplome(db.Model):
    __tablename__ = 'diplomes'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), unique=True)
    numero_serie = db.Column(db.String(50))
    mention = db.Column(db.String(50), default='Passable')  # Ajouté: mention du diplôme
    date_emission = db.Column(db.DateTime, default=datetime.utcnow)
    etudiant = db.relationship('Etudiant', back_populates='diplome_obj')


# Dans app/models.py

class Examen(db.Model):
    __tablename__ = 'examens'
    id = db.Column(db.Integer, primary_key=True)

    # Quoi et Qui ?
    ue_id = db.Column(db.Integer, db.ForeignKey('ues.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    # Quand et Où ?
    date_examen = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    salle = db.Column(db.String(50), nullable=False)  # Ex: Amphithéâtre A

    # Qui surveille ? (Optionnel)
    surveillant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=True)

    # Relations
    ue = db.relationship('UE', backref='examens')
    classe = db.relationship('Classe', backref='examens')
    surveillant = db.relationship('Enseignant', backref='surveillances')


# Dans app/models.py

class Seance(db.Model):
    __tablename__ = 'seances'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)  # Ex: Mathématiques

    # Dates et Heures (Format ISO pour le calendrier)
    start = db.Column(db.DateTime, nullable=False)  # Début
    end = db.Column(db.DateTime, nullable=False)  # Fin

    salle = db.Column(db.String(50))
    couleur = db.Column(db.String(20), default='#3788d8')  # Bleu par défaut

    # Relations
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=True)

    classe = db.relationship('Classe', backref='emploi_du_temps')
    enseignant = db.relationship('Enseignant', backref='seances')


# Dans app/models.py

class Livre(db.Model):
    __tablename__ = 'livres'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    auteur = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(50))  # Ex: Roman, Science, Histoire

    # Fichiers
    image_couverture = db.Column(db.String(255), default='default_book.jpg')
    fichier_pdf = db.Column(db.String(255), nullable=False)

    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)


# Dans app/models.py

class Deliberation(db.Model):
    __tablename__ = 'deliberations'
    id = db.Column(db.Integer, primary_key=True)

    moyenne_annuelle = db.Column(db.Float, nullable=False)
    decision = db.Column(db.String(50), nullable=False)  # 'ADMIS', 'AJOURNÉ', 'RATTRAPAGE'
    mention = db.Column(db.String(50))  # 'Passable', 'Bien', etc.
    rang = db.Column(db.Integer)  # 1er, 2ème, 3ème...

    date_calcul = db.Column(db.DateTime, default=datetime.utcnow)

    # Liens
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    etudiant = db.relationship('Etudiant', backref='deliberations')
    classe = db.relationship('Classe', backref='historique_deliberations')


# Dans app/models.py
from datetime import datetime


# ============================================================
# LABORATOIRE VIRTUEL - MODÈLES
# ============================================================

class TP(db.Model):
    """Travaux Pratiques déposés par enseignants"""
    __tablename__ = 'tps'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ue_id = db.Column(db.Integer, db.ForeignKey('ues.id', ondelete='CASCADE'), nullable=False, index=True)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id', ondelete='CASCADE'), nullable=False)

    # Type de simulation
    type_simulation = db.Column(
        Enum('buck', 'boost', 'chute_libre', 'rdm_poutre', 'signal_fourier',
             'stock_flux', 'transport_routage', 'thermodynamique',
             'pile_electrochimique', 'saponification', name='type_sim_enum'),
        nullable=False
    )

    # Nom de l'IA assistant
    ia_nom = db.Column(
        Enum('ETA', 'ALPHA', 'KAYT', name='ia_nom_enum'),
        nullable=False
    )

    # Fichiers
    fichier_sujet = db.Column(db.String(500))  # PDF du sujet
    fichier_consigne = db.Column(db.Text)  # Consignes JSON

    # Notation
    note_sur = db.Column(db.Integer, default=20)
    bareme = db.Column(db.Text)  # JSON du barème

    # Métadonnées
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_limite = db.Column(db.DateTime)  # Deadline

    # Relations
    sessions = db.relationship('SessionTP', backref='tp', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TP {self.titre}>'


class SessionTP(db.Model):
    """Session de TP d'un étudiant"""
    __tablename__ = 'sessions_tp'

    id = db.Column(db.Integer, primary_key=True)
    tp_id = db.Column(db.Integer, db.ForeignKey('tps.id', ondelete='CASCADE'), nullable=False, index=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False, index=True)

    # Timing
    date_debut = db.Column(db.DateTime, default=datetime.utcnow)
    date_fin = db.Column(db.DateTime)
    duree_minutes = db.Column(db.Integer)

    # Statut
    statut = db.Column(
        Enum('en_cours', 'terminé', 'évalué', 'rendu', name='statut_session_enum'),
        default='en_cours',
        index=True
    )

    # Données de simulation (JSON)
    donnees_simulation = db.Column(db.Text)  # Stocke toutes les mesures
    nb_mesures = db.Column(db.Integer, default=0)

    # Fichiers générés
    fichier_excel = db.Column(db.String(500))
    fichier_pdf = db.Column(db.String(500))
    fichier_rapport = db.Column(db.String(500))  # Rapport étudiant uploadé

    # Évaluation IA
    note_ia = db.Column(db.Float)  # Note automatique de l'IA
    commentaire_ia = db.Column(db.Text)
    criteres_evaluation = db.Column(db.Text)  # JSON détaillé

    # Note finale enseignant
    note_finale = db.Column(db.Float)
    commentaire_enseignant = db.Column(db.Text)
    validé = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<SessionTP Etudiant:{self.etudiant_id} TP:{self.tp_id}>'


class MesureSimulation(db.Model):
    """Stockage des mesures individuelles"""
    __tablename__ = 'mesures_simulation'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions_tp.id', ondelete='CASCADE'), nullable=False, index=True)

    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    temps_relatif = db.Column(db.Float)  # En secondes depuis le début

    # Paramètres d'entrée (JSON)
    parametres = db.Column(db.Text)  # Ex: {"Vin": 24, "alpha": 0.5, "L": 0.001}

    # Résultats (JSON)
    resultats = db.Column(db.Text)  # Ex: {"Vout": 12.3, "ripple": 0.05}

    # Métadonnées
    type_mesure = db.Column(db.String(50))  # 'automatique' ou 'manuelle'

    def __repr__(self):
        return f'<Mesure Session:{self.session_id} T:{self.temps_relatif}s>'


class InteractionIA(db.Model):
    """Historique des interactions avec l'IA"""
    __tablename__ = 'interactions_ia'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions_tp.id', ondelete='CASCADE'), nullable=False, index=True)

    # Conversation
    question_etudiant = db.Column(db.Text, nullable=False)
    reponse_ia = db.Column(db.Text, nullable=False)

    # Contexte
    contexte_simulation = db.Column(db.Text)  # JSON snapshot des paramètres

    # Métadonnées
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ia_nom = db.Column(db.String(20))  # ETA, ALPHA, ou KAYT

    # Analyse pédagogique
    pertinence_question = db.Column(db.Integer)  # 1-5
    aide_apportee = db.Column(db.Boolean)  # L'IA a-t-elle vraiment aidé ?

    def __repr__(self):
        return f'<InteractionIA Session:{self.session_id}>'


class Badge(db.Model):
    """Badges déblocables par les étudiants"""
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icone = db.Column(db.String(50))  # Nom de l'icône Font Awesome
    couleur = db.Column(db.String(20), default='#ffd700')

    # Critères de déblocage (JSON)
    criteres = db.Column(db.Text)  # Ex: {"nb_sessions": 10, "note_min": 15}

    # Métadonnées
    categorie = db.Column(db.String(50))  # 'performance', 'persévérance', 'exploration', 'aide'
    points = db.Column(db.Integer, default=10)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Badge {self.nom}>'


class BadgeEtudiant(db.Model):
    """Association entre étudiants et badges débloqués"""
    __tablename__ = 'badges_etudiants'

    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False)

    date_obtention = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.Integer,
                           db.ForeignKey('sessions_tp.id', ondelete='SET NULL'))  # Session qui a déclenché le badge

    # Relations
    etudiant = db.relationship('Etudiant', backref=db.backref('badges_obtenus', lazy='dynamic'))
    badge = db.relationship('Badge')

    def __repr__(self):
        return f'<BadgeEtudiant E:{self.etudiant_id} B:{self.badge_id}>'


class SessionCollaborative(db.Model):
    """Sessions de TP en mode collaboratif"""
    __tablename__ = 'sessions_collaboratives'

    id = db.Column(db.Integer, primary_key=True)
    tp_id = db.Column(db.Integer, db.ForeignKey('tps.id', ondelete='CASCADE'), nullable=False)

    # Créateur de la session
    createur_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)

    # Nom de la session
    nom_session = db.Column(db.String(200))
    code_acces = db.Column(db.String(10), unique=True)  # Code pour rejoindre

    # État
    statut = db.Column(
        Enum('ouverte', 'en_cours', 'terminee', name='statut_collab_enum'),
        default='ouverte'
    )

    # Paramètres collaboratifs
    max_participants = db.Column(db.Integer, default=4)
    partage_mesures = db.Column(db.Boolean, default=True)  # Partager les mesures entre tous

    # Données partagées (JSON)
    donnees_partagees = db.Column(db.Text)  # Paramètres synchronisés

    # Métadonnées
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)

    # Relations
    tp = db.relationship('TP', backref='sessions_collaboratives')
    createur = db.relationship('Etudiant', foreign_keys=[createur_id])

    def __repr__(self):
        return f'<SessionCollaborative {self.nom_session}>'


class ParticipantCollaboratif(db.Model):
    """Participants d'une session collaborative"""
    __tablename__ = 'participants_collaboratifs'

    id = db.Column(db.Integer, primary_key=True)
    session_collab_id = db.Column(db.Integer, db.ForeignKey('sessions_collaboratives.id', ondelete='CASCADE'),
                                  nullable=False)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)

    role = db.Column(
        Enum('createur', 'participant', name='role_collab_enum'),
        default='participant'
    )

    date_rejointe = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)

    # Contribution individuelle
    nb_mesures_personnelles = db.Column(db.Integer, default=0)

    # Relations
    session_collab = db.relationship('SessionCollaborative', backref='participants')
    etudiant = db.relationship('Etudiant')

    def __repr__(self):
        return f'<ParticipantCollab E:{self.etudiant_id} S:{self.session_collab_id}>'


class VideoExplicative(db.Model):
    """Vidéos explicatives pour les TPs"""
    __tablename__ = 'videos_explicatives'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Lien vidéo (YouTube, Vimeo, etc.)
    url_video = db.Column(db.String(500), nullable=False)
    duree_minutes = db.Column(db.Integer)

    # Association
    type_simulation = db.Column(db.String(50))  # 'buck', 'rdm_poutre', etc.
    tp_id = db.Column(db.Integer, db.ForeignKey('tps.id', ondelete='CASCADE'))

    # Métadonnées
    langue = db.Column(db.String(10), default='fr')
    niveau = db.Column(
        Enum('debutant', 'intermediaire', 'avance', name='niveau_video_enum'),
        default='debutant'
    )

    nb_vues = db.Column(db.Integer, default=0)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    tp = db.relationship('TP', backref='videos')

    def __repr__(self):
        return f'<VideoExplicative {self.titre}>'


class VueVideo(db.Model):
    """Suivi des vues de vidéos par étudiant"""
    __tablename__ = 'vues_videos'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos_explicatives.id', ondelete='CASCADE'), nullable=False)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)

    date_vue = db.Column(db.DateTime, default=datetime.utcnow)
    pourcentage_visionne = db.Column(db.Float, default=0)  # 0-100

    # Relations
    video = db.relationship('VideoExplicative')
    etudiant = db.relationship('Etudiant')


class ReactionChimique(db.Model):
    """Base de données des réactions chimiques"""
    __tablename__ = 'reactions_chimiques'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    type_reaction = db.Column(
        Enum('oxydoreduction', 'acide_base', 'saponification',
             'esterification', 'hydrolyse', 'equilibre', name='type_reaction_enum'),
        nullable=False
    )

    # Équation chimique
    equation = db.Column(db.String(500))

    # Réactifs et produits (JSON)
    reactifs = db.Column(db.Text)  # [{"formule": "NaOH", "nom": "Soude", "quantite": 1}]
    produits = db.Column(db.Text)

    # Données thermodynamiques
    delta_h = db.Column(db.Float)  # Enthalpie (kJ/mol)
    delta_g = db.Column(db.Float)  # Énergie libre (kJ/mol)
    constante_equilibre = db.Column(db.Float)  # K

    # Cinétique
    ordre_reaction = db.Column(db.Integer)
    energie_activation = db.Column(db.Float)  # Ea (kJ/mol)

    def __repr__(self):
        return f'<ReactionChimique {self.nom}>'
