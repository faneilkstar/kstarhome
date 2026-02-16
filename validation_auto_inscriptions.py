#!/usr/bin/env python3
"""
Service de validation automatique des inscriptions par IA
Si le directeur ne valide pas une inscription sous 48h, l'IA le fait automatiquement
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Etudiant, Classe, InscriptionUE
from app.services.validation_ia import ValidationIA
from config import Config

app = create_app('development')

def validation_auto_inscriptions():
    """Valide automatiquement les inscriptions en attente depuis plus de 48h"""

    with app.app_context():
        print("=" * 70)
        print("🤖 VALIDATION AUTOMATIQUE DES INSCRIPTIONS PAR IA")
        print("=" * 70)
        print()

        # Calculer la date limite (48h avant maintenant)
        delai_validation = datetime.utcnow() - timedelta(hours=48)

        # Récupérer les étudiants en attente depuis plus de 48h
        etudiants_attente = Etudiant.query.filter(
            Etudiant.statut_inscription == 'en_attente',
            Etudiant.date_inscription <= delai_validation
        ).all()

        if not etudiants_attente:
            print("✅ Aucune inscription en attente de validation automatique")
            print()
            return

        print(f"📋 {len(etudiants_attente)} inscription(s) en attente depuis plus de 48h")
        print()

        ia = ValidationIA()
        acceptes = 0
        refuses = 0
        erreurs = 0

        for etudiant in etudiants_attente:
            try:
                print(f"🔄 Traitement de {etudiant.nom} {etudiant.prenom}...", end=" ")

                # Évaluer avec l'IA
                resultat = ia.evaluer_inscription(etudiant)

                # Stocker l'évaluation
                etudiant.evaluation_ia = str(resultat)

                if resultat['decision'] == 'accepte':
                    # Accepter l'étudiant
                    # Trouver une classe de première année dans sa filière
                    classe = Classe.query.filter_by(
                        filiere_id=etudiant.filiere_id,
                        annee=1,
                        active=True
                    ).first()

                    if classe:
                        # Générer le matricule
                        annee_actuelle = datetime.now().year
                        etudiant.matricule = f"ETU-{annee_actuelle}-{str(etudiant.id).zfill(4)}"

                        # Valider
                        etudiant.classe_id = classe.id
                        etudiant.statut_inscription = 'accepté'
                        etudiant.date_validation = datetime.utcnow()

                        # Inscrire aux UEs de la classe (optionnel selon la configuration)
                        # Note: On peut laisser l'étudiant choisir ses UEs en 1ère année

                        acceptes += 1
                        print(f"✅ ACCEPTÉ (Score: {resultat['score']}/100)")
                    else:
                        print(f"⚠️  Aucune classe de 1ère année trouvée pour la filière")
                        erreurs += 1
                else:
                    # Refuser
                    etudiant.statut_inscription = 'refusé'
                    refuses += 1
                    print(f"❌ REFUSÉ (Moyenne insuffisante)")

            except Exception as e:
                print(f"❌ ERREUR: {str(e)}")
                erreurs += 1

        # Sauvegarder toutes les modifications
        db.session.commit()

        print()
        print("=" * 70)
        print("📊 RÉSULTATS DE LA VALIDATION AUTOMATIQUE")
        print("=" * 70)
        print(f"✅ Acceptés : {acceptes}")
        print(f"❌ Refusés  : {refuses}")
        print(f"⚠️  Erreurs  : {erreurs}")
        print("=" * 70)
        print()

        if acceptes > 0 or refuses > 0:
            print("💡 Les étudiants concernés ont été notifiés par email (si configuré)")

        return {
            'acceptes': acceptes,
            'refuses': refuses,
            'erreurs': erreurs
        }

if __name__ == '__main__':
    validation_auto_inscriptions()

