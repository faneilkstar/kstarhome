"""
API Authentication avec JWT
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)

from app.models import User
from app import db

ns = Namespace('auth', description='Authentification')

# Modèles Swagger
login_model = ns.model('Login', {
    'username': fields.String(required=True, description='Nom d\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe')
})

token_model = ns.model('Token', {
    'access_token': fields.String(description='JWT Access Token'),
    'refresh_token': fields.String(description='JWT Refresh Token'),
    'user': fields.Nested(ns.model('User', {
        'id': fields.Integer,
        'username': fields.String,
        'role': fields.String,
        'email': fields.String
    }))
})


@ns.route('/login')
class Login(Resource):
    @ns.expect(login_model)
    @ns.marshal_with(token_model, code=200)
    @ns.response(401, 'Identifiants invalides')
    def post(self):
        """Connexion et génération de tokens JWT"""
        data = request.get_json()

        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            ns.abort(401, 'Identifiants invalides')

        # Générer les tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role.value,
                'email': user.email
            }
        }


@ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @ns.marshal_with(token_model, code=200)
    def post(self):
        """Rafraîchir le token d'accès"""
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)

        user = User.query.get(current_user_id)

        return {
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role.value,
                'email': user.email
            }
        }


@ns.route('/me')
class Me(Resource):
    @jwt_required()
    @ns.doc(security='Bearer')
    def get(self):
        """Récupérer les infos de l'utilisateur connecté"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        return {
            'id': user.id,
            'username': user.username,
            'role': user.role.value,
            'email': user.email
        }