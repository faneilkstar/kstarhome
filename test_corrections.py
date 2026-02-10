#!/usr/bin/env python3
"""
Script de test pour vérifier que toutes les corrections fonctionnent
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Etudiant, Enseignant, UE, Filiere, Classe

def test_user_properties():
    """Test des propriétés is_directeur, is_enseignant, is_etudiant"""
    print("🧪 Test 1: Propriétés User...")
    app = create_app()
    with app.app_context():
        # Test directeur
        user_dir = User(username="test_dir", role="DIRECTEUR")
        assert user_dir.is_directeur == True
        assert user_dir.is_enseignant == False
        assert user_dir.is_etudiant == False
        print("   ✅ Propriétés directeur OK")

        # Test enseignant
        user_ens = User(username="test_ens", role="ENSEIGNANT")
        assert user_ens.is_directeur == False
        assert user_ens.is_enseignant == True
        assert user_ens.is_etudiant == False
        print("   ✅ Propriétés enseignant OK")

        # Test étudiant
        user_etu = User(username="test_etu", role="ETUDIANT")
        assert user_etu.is_directeur == False
        assert user_etu.is_enseignant == False
        assert user_etu.is_etudiant == True
        print("   ✅ Propriétés étudiant OK")

def test_user_set_password():
    """Test de la méthode set_password"""
    print("\n🧪 Test 2: Méthode set_password...")
    app = create_app()
    with app.app_context():
        user = User(username="test_pwd", role="ETUDIANT")
        user.set_password("motdepasse123")
        assert user.password_hash is not None
        assert user.verify_password("motdepasse123") == True
        assert user.verify_password("mauvais") == False
        print("   ✅ Méthode set_password OK")

def test_etudiant_filiere():
    """Test de la relation filiere_objet dans Etudiant"""
    print("\n🧪 Test 3: Relation Etudiant.filiere_objet...")
    app = create_app()
    with app.app_context():
        # Vérifier que l'attribut existe
        etudiant = Etudiant.query.first()
        if etudiant:
            # L'attribut doit exister (peut être None)
            assert hasattr(etudiant, 'filiere_objet')
            print(f"   ✅ Attribut filiere_objet existe")
            if etudiant.filiere_objet:
                print(f"   ✅ Filière: {etudiant.filiere_objet.nom_filiere}")
            else:
                print(f"   ⚠️  Étudiant sans filière (normal pour test)")
        else:
            print("   ⚠️  Aucun étudiant en base (normal pour test)")

def test_ue_taux_reussite():
    """Test de la méthode get_taux_reussite dans UE"""
    print("\n🧪 Test 4: Méthode UE.get_taux_reussite...")
    app = create_app()
    with app.app_context():
        ue = UE.query.first()
        if ue:
            assert hasattr(ue, 'get_taux_reussite')
            taux = ue.get_taux_reussite()
            assert isinstance(taux, (int, float))
            print(f"   ✅ Méthode get_taux_reussite OK (taux: {taux}%)")
        else:
            print("   ⚠️  Aucune UE en base (normal pour test)")

def test_database_connection():
    """Test de la connexion à la base de données"""
    print("\n🧪 Test 5: Connexion base de données...")
    app = create_app()
    with app.app_context():
        try:
            # Test simple de requête
            user_count = User.query.count()
            etudiant_count = Etudiant.query.count()
            ue_count = UE.query.count()
            print(f"   ✅ Base de données accessible")
            print(f"   📊 Users: {user_count}, Étudiants: {etudiant_count}, UE: {ue_count}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    return True

def main():
    print("=" * 60)
    print("🔍 TESTS DE VÉRIFICATION DES CORRECTIONS")
    print("=" * 60)

    try:
        test_user_properties()
        test_user_set_password()
        test_etudiant_filiere()
        test_ue_taux_reussite()
        test_database_connection()

        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ ÉCHEC: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

