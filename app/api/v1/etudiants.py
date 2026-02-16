"""
API Gestion des étudiants
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Etudiant, Classe, User
from app import db

ns = Namespace('etudiants', description='Gestion des étudiants')

# Modèles
etudiant_model = ns.model('Etudiant', {
    'id': fields.Integer(readonly=True),
    'matricule': fields.String(required=True),
    'nom': fields.String(required=True),
    'prenom': fields.String(required=True),
    'sexe': fields.String(),
    'date_naissance': fields.Date(),
    'lieu_naissance': fields.String(),
    'email': fields.String(),
    'telephone': fields.String(),
    'classe_id': fields.Integer(),
    'classe_nom': fields.String(attribute=lambda x: x.classe.nom_classe if x.classe else None)
})

etudiant_input = ns.model('EtudiantInput', {
    'matricule': fields.String(required=True),
    'nom': fields.String(required=True),
    'prenom': fields.String(required=True),
    'sexe': fields.String(),
    'date_naissance': fields.String(),
    'lieu_naissance': fields.String(),
    'email': fields.String(),
    'telephone': fields.String(),
    'classe_id': fields.Integer()
})


@ns.route('/')
class EtudiantList(Resource):
    @jwt_required()
    @ns.doc(security='Bearer')
    @ns.marshal_list_with(etudiant_model)
    @ns.param('classe_id', 'Filtrer par classe')
    @ns.param('page', 'Numéro de page', type=int)
    @ns.param('per_page', 'Éléments par page', type=int)
    def get(self):
        """Liste de tous les étudiants (paginée)"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        classe_id = request.args.get('classe_id', type=int)

        query = Etudiant.query

        if classe_id:
            query = query.filter_by(classe_id=classe_id)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return pagination.items

    @jwt_required()
    @ns.doc(security='Bearer')
    @ns.expect(etudiant_input)
    @ns.marshal_with(etudiant_model, code=201)
    def post(self):
        """Créer un nouvel étudiant"""
        data = request.get_json()

        # Vérifier si matricule existe déjà
        if Etudiant.query.filter_by(matricule=data['matricule']).first():
            ns.abort(400, 'Matricule déjà existant')

        etudiant = Etudiant(
            matricule=data['matricule'],
            nom=data['nom'],
            prenom=data['prenom'],
            sexe=data.get('sexe'),
            email=data.get('email'),
            telephone=data.get('telephone'),
            classe_id=data.get('classe_id')
        )

        db.session.add(etudiant)
        db.session.commit()

        return etudiant, 201


@ns.route('/<int:id>')
@ns.param('id', 'Identifiant de l\'étudiant')
class EtudiantDetail(Resource):
    @jwt_required()
    @ns.doc(security='Bearer')
    @ns.marshal_with(etudiant_model)
    def get(self, id):
        """Récupérer un étudiant par son ID"""
        etudiant = Etudiant.query.get_or_404(id)
        return etudiant

    @jwt_required()
    @ns.doc(security='Bearer')
    @ns.expect(etudiant_input)
    @ns.marshal_with(etudiant_model)
    def put(self, id):
        """Mettre à jour un étudiant"""
        etudiant = Etudiant.query.get_or_404(id)
        data = request.get_json()

        for key, value in data.items():
            if hasattr(etudiant, key):
                setattr(etudiant, key, value)

        db.session.commit()
        return etudiant

    @jwt_required()
    @ns.doc(security='Bearer')
    @ns.response(204, 'Étudiant supprimé')
    def delete(self, id):
        """Supprimer un étudiant"""
        etudiant = Etudiant.query.get_or_404(id)
        db.session.delete(etudiant)
        db.session.commit()
        return '', 204


@ns.route('/<int:id>/notes')
class EtudiantNotes(Resource):
    @jwt_required()
    @ns.doc(security='Bearer')
    def get(self, id):
        """Récupérer toutes les notes d'un étudiant"""
        etudiant = Etudiant.query.get_or_404(id)

        notes_data = []
        for note in etudiant.notes:
            notes_data.append({
                'id': note.id,
                'matiere': note.matiere.intitule if note.matiere else None,
                'type_note': note.type_note.value,
                'valeur': note.valeur,
                'coefficient': note.coefficient,
                'date': note.date_note.isoformat() if note.date_note else None
            })

        return {
            'etudiant': etudiant.get_nom_complet(),
            'total_notes': len(notes_data),
            'notes': notes_data
        }