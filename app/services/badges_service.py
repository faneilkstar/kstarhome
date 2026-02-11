"""
Système de gamification avec badges
"""

from app import db
from app.models import Badge, BadgeEtudiant, SessionTP, Etudiant
from datetime import datetime
import json


class BadgesService:
    """Gestion des badges et achievements"""

    @staticmethod
    def initialiser_badges():
        """Crée les badges de base (à exécuter une fois)"""
        badges_defaut = [
            {
                'nom': '🎯 Premier Pas',
                'description': 'Première session de TP terminée',
                'icone': 'fa-flag-checkered',
                'couleur': '#4caf50',
                'categorie': 'debutant',
                'points': 10,
                'criteres': json.dumps({'nb_sessions_terminees': 1})
            },
            {
                'nom': '🔬 Explorateur',
                'description': '5 TPs différents réalisés',
                'icone': 'fa-compass',
                'couleur': '#2196f3',
                'categorie': 'exploration',
                'points': 25,
                'criteres': json.dumps({'nb_tps_differents': 5})
            },
            {
                'nom': '⭐ Excellence',
                'description': 'Note de 18/20 ou plus',
                'icone': 'fa-star',
                'couleur': '#ffd700',
                'categorie': 'performance',
                'points': 50,
                'criteres': json.dumps({'note_min': 18})
            },
            {
                'nom': '🔥 Perfectionniste',
                'description': '50 mesures dans une seule session',
                'icone': 'fa-fire',
                'couleur': '#ff5722',
                'categorie': 'perseverance',
                'points': 30,
                'criteres': json.dumps({'nb_mesures_session': 50})
            },
            {
                'nom': '💎 Maître du Labo',
                'description': '20 sessions terminées avec note >= 15',
                'icone': 'fa-gem',
                'couleur': '#9c27b0',
                'categorie': 'maitre',
                'points': 100,
                'criteres': json.dumps({'nb_sessions_note_min': {'nb': 20, 'note': 15}})
            },
            {
                'nom': '🤝 Curieux',
                'description': '20 questions posées à l\'IA',
                'icone': 'fa-question-circle',
                'couleur': '#00bcd4',
                'categorie': 'aide',
                'points': 20,
                'criteres': json.dumps({'nb_interactions_ia': 20})
            },
            {
                'nom': '⚡ Rapide',
                'description': 'Session terminée en moins de 15 minutes',
                'icone': 'fa-bolt',
                'couleur': '#ffeb3b',
                'categorie': 'vitesse',
                'points': 15,
                'criteres': json.dumps({'duree_max': 15})
            },
            {
                'nom': '🏆 Champion',
                'description': 'Note parfaite 20/20',
                'icone': 'fa-trophy',
                'couleur': '#ff9800',
                'categorie': 'performance',
                'points': 75,
                'criteres': json.dumps({'note_exacte': 20})
            }
        ]

        for badge_data in badges_defaut:
            # Vérifier si le badge existe déjà
            existe = Badge.query.filter_by(nom=badge_data['nom']).first()
            if not existe:
                badge = Badge(**badge_data)
                db.session.add(badge)

        db.session.commit()
        print(f"✅ {len(badges_defaut)} badges initialisés")

    @staticmethod
    def verifier_et_attribuer_badges(session_tp):
        """
        Vérifie si une session déclenche de nouveaux badges

        Args:
            session_tp: SessionTP qui vient de se terminer

        Returns:
            list: Liste des badges nouvellement débloqués
        """
        etudiant = session_tp.etudiant
        nouveaux_badges = []

        # Récupérer tous les badges
        tous_badges = Badge.query.all()

        # Badges déjà obtenus par cet étudiant
        badges_obtenus_ids = [b.badge_id for b in etudiant.badges_obtenus.all()]

        for badge in tous_badges:
            # Skip si déjà obtenu
            if badge.id in badges_obtenus_ids:
                continue

            # Vérifier les critères
            criteres = json.loads(badge.criteres)

            if BadgesService._verifie_criteres(etudiant, session_tp, criteres):
                # Débloquer le badge !
                badge_etudiant = BadgeEtudiant(
                    etudiant_id=etudiant.id,
                    badge_id=badge.id,
                    session_id=session_tp.id
                )
                db.session.add(badge_etudiant)
                nouveaux_badges.append(badge)

        if nouveaux_badges:
            db.session.commit()

        return nouveaux_badges

    @staticmethod
    def _verifie_criteres(etudiant, session_tp, criteres):
        """Vérifie si les critères d'un badge sont remplis"""

        # Première session terminée
        if 'nb_sessions_terminees' in criteres:
            nb_requis = criteres['nb_sessions_terminees']
            nb_actuel = SessionTP.query.filter_by(
                etudiant_id=etudiant.id,
                statut='terminé'
            ).count()
            if nb_actuel >= nb_requis:
                return True

        # Note minimale
        if 'note_min' in criteres:
            note_min = criteres['note_min']
            if session_tp.note_finale and session_tp.note_finale >= note_min:
                return True
            elif session_tp.note_ia and session_tp.note_ia >= note_min:
                return True

        # Note exacte
        if 'note_exacte' in criteres:
            note_exacte = criteres['note_exacte']
            if session_tp.note_finale == note_exacte or session_tp.note_ia == note_exacte:
                return True

        # Nombre de mesures dans la session
        if 'nb_mesures_session' in criteres:
            nb_requis = criteres['nb_mesures_session']
            if (session_tp.nb_mesures or 0) >= nb_requis:
                return True

        # TPs différents
        if 'nb_tps_differents' in criteres:
            nb_requis = criteres['nb_tps_differents']
            tps_differents = db.session.query(SessionTP.tp_id).filter_by(
                etudiant_id=etudiant.id
            ).distinct().count()
            if tps_differents >= nb_requis:
                return True

        # Durée maximale
        if 'duree_max' in criteres:
            duree_max = criteres['duree_max']
            if session_tp.duree_minutes and session_tp.duree_minutes <= duree_max:
                return True

        # Nombre d'interactions IA
        if 'nb_interactions_ia' in criteres:
            from app.models import InteractionIA
            nb_requis = criteres['nb_interactions_ia']
            nb_actuel = InteractionIA.query.join(SessionTP).filter(
                SessionTP.etudiant_id == etudiant.id
            ).count()
            if nb_actuel >= nb_requis:
                return True

        # Sessions avec note minimale
        if 'nb_sessions_note_min' in criteres:
            config = criteres['nb_sessions_note_min']
            nb_requis = config['nb']
            note_min = config['note']

            nb_actuel = SessionTP.query.filter(
                SessionTP.etudiant_id == etudiant.id,
                SessionTP.note_finale >= note_min
            ).count()

            if nb_actuel >= nb_requis:
                return True

        return False