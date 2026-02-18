"""
Service de gestion des UE selon le système LMD
Architecture V2 avec Semestres et UE Composites
"""
from app import db
from app.models import UE, Departement, Filiere, Note


class UEService:
    """Service pour gérer les Unités d'Enseignement selon le système LMD"""

    # Mapping semestre -> code numérique (pour génération de code)
    SEMESTRE_TO_NUM = {
        'S1': '1', 'S2': '2', 'S3': '3',
        'S4': '4', 'S5': '5', 'S6': '6',
        'S7': '7', 'S8': '8', 'S9': '9', 'S10': '10'
    }

    @staticmethod
    def generer_code_ue(categorie, semestre, nom_ue, departement_code=None, filiere_code=None):
        """
        Génère un code intelligent pour une UE selon le système LMD

        Exemples:
        - INF101 : Informatique, S1, cours 01
        - GL301 : Génie Logiciel, S3, cours 01
        - LANG201 : Langues (transversal), S2, cours 01
        - LIB101 : Libre, S1, cours 01

        Args:
            categorie: 'fondamentale', 'specialite', 'transversale', 'libre'
            semestre: 'S1', 'S2', ..., 'S6'
            nom_ue: Nom de l'UE (pour extraction intelligente)
            departement_code: Code du département (ex: 'INFO', 'MATH')
            filiere_code: Code de la filière (ex: 'GL', 'IA', 'RES')

        Returns:
            str: Code généré (ex: 'INF101')
        """
        # 1. Déterminer le préfixe selon la catégorie
        prefixe = ""

        if categorie == 'fondamentale':
            # Utiliser le code du département
            prefixe = departement_code[:4] if departement_code else "UNK"

        elif categorie == 'specialite':
            # Utiliser le code de la filière
            if filiere_code:
                prefixe = filiere_code[:4].upper()
            elif departement_code:
                prefixe = departement_code[:4]
            else:
                prefixe = "SPE"

        elif categorie == 'transversale':
            # Préfixe thématique basé sur le nom
            nom_upper = nom_ue.upper()
            if 'ANGL' in nom_upper or 'LANG' in nom_upper:
                prefixe = "LANG"
            elif 'COM' in nom_upper or 'EXPRESSION' in nom_upper:
                prefixe = "COM"
            elif 'DROIT' in nom_upper:
                prefixe = "DRT"
            elif 'MANAGE' in nom_upper or 'GEST' in nom_upper:
                prefixe = "MGT"
            else:
                prefixe = "TR"

        elif categorie == 'libre':
            prefixe = "LIB"

        # 2. Extraire le numéro du semestre
        numero_semestre = UEService.SEMESTRE_TO_NUM.get(semestre, '1')

        # 3. Trouver le prochain numéro disponible pour ce préfixe+semestre
        pattern = f"{prefixe}{numero_semestre}%"
        existing_ues = UE.query.filter(UE.code_ue.like(pattern)).all()

        # Extraire les numéros existants
        existing_numbers = []
        for ue in existing_ues:
            try:
                # Extraire les 2 derniers chiffres (ex: INF101 -> 01)
                num_str = ue.code_ue[len(prefixe) + len(numero_semestre):]
                if num_str.isdigit():
                    existing_numbers.append(int(num_str))
            except:
                continue

        # Trouver le prochain numéro libre
        next_num = 1
        if existing_numbers:
            next_num = max(existing_numbers) + 1

        # 4. Construire le code final
        numero_cours = f"{next_num:02d}"  # Format sur 2 chiffres (01, 02, ...)
        code_final = f"{prefixe}{numero_semestre}{numero_cours}"

        return code_final

    @staticmethod
    def generer_code_ec(ue_mere, nom_ec, type_element='ec_matiere'):
        """
        Génère le code d'un Élément Constitutif (sous-UE)

        Exemples:
        - UE Mère: NUM101 (Analyse Numérique)
          - EC 1: 1NUM101 (Séries Numériques)
          - EC 2: 2NUM101 (Intégrales)

        Args:
            ue_mere: L'objet UE parent
            nom_ec: Nom de l'EC
            type_element: 'ec_cours', 'ec_td', 'ec_tp', 'ec_matiere'

        Returns:
            str: Code généré (ex: '1NUM101')
        """
        # Compter combien d'EC existent déjà pour cette UE mère
        nb_ec_existants = ue_mere.elements_constitutifs.count()

        # Le numéro d'ordre est le suivant
        numero_ordre = nb_ec_existants + 1

        # Format: {ordre}{code_ue_mere}
        code_ec = f"{numero_ordre}{ue_mere.code_ue}"

        return code_ec

    @staticmethod
    def creer_ue_composite(
        nom_ue_mere,
        semestre,
        credits,
        categorie,
        departement_id,
        elements_constitutifs_data,
        **kwargs
    ):
        """
        Crée une UE composite avec ses éléments constitutifs

        Args:
            nom_ue_mere: Nom de l'UE mère (ex: "Analyse Numérique")
            semestre: 'S1', 'S2', etc.
            credits: Crédits ECTS (portés par l'UE mère)
            categorie: Catégorie de l'UE
            departement_id: ID du département
            elements_constitutifs_data: Liste de dict avec les EC
                [
                    {'nom': 'Séries Numériques', 'coefficient': 2.0, 'type': 'ec_matiere'},
                    {'nom': 'Intégrales', 'coefficient': 1.0, 'type': 'ec_matiere'}
                ]
            **kwargs: Autres paramètres optionnels

        Returns:
            tuple: (ue_mere, liste_ec)
        """
        # 1. Générer le code de l'UE mère
        dept = Departement.query.get(departement_id)
        code_ue_mere = UEService.generer_code_ue(
            categorie=categorie,
            semestre=semestre,
            nom_ue=nom_ue_mere,
            departement_code=dept.code if dept else None,
            filiere_code=kwargs.get('filiere_code')
        )

        # 2. Créer l'UE mère
        ue_mere = UE(
            code_ue=code_ue_mere,
            intitule=nom_ue_mere,
            nom_ue=nom_ue_mere,
            semestre=semestre,
            credits=credits,
            categorie=categorie,
            nature='composite',
            type_element='ue_composite',
            departement_id=departement_id,
            coefficient=0,  # La mère ne porte pas de coefficient
            **{k: v for k, v in kwargs.items() if k not in ['filiere_code']}
        )

        db.session.add(ue_mere)
        db.session.flush()  # Pour obtenir l'ID de l'UE mère

        # 3. Créer les éléments constitutifs
        elements_crees = []

        for ordre, ec_data in enumerate(elements_constitutifs_data, start=1):
            code_ec = UEService.generer_code_ec(
                ue_mere=ue_mere,
                nom_ec=ec_data['nom'],
                type_element=ec_data.get('type', 'ec_matiere')
            )

            ec = UE(
                code_ue=code_ec,
                intitule=ec_data['nom'],
                nom_ue=ec_data['nom'],
                semestre=semestre,
                credits=0,  # Les crédits sont portés par la mère
                coefficient=ec_data.get('coefficient', 1.0),
                categorie=categorie,
                nature='simple',
                type_element=ec_data.get('type', 'ec_matiere'),
                departement_id=departement_id,
                parent_id=ue_mere.id,
                ordre=ordre
            )

            db.session.add(ec)
            elements_crees.append(ec)

        db.session.commit()

        return ue_mere, elements_crees

    @staticmethod
    def calculer_moyenne_ue_composite(ue_mere_id, etudiant_id):
        """
        Calcule la moyenne d'un étudiant pour une UE composite

        Formule: (Note1 * Coef1 + Note2 * Coef2) / (Coef1 + Coef2)

        Args:
            ue_mere_id: ID de l'UE composite
            etudiant_id: ID de l'étudiant

        Returns:
            float or None: Moyenne calculée ou None si notes manquantes
        """
        ue_mere = UE.query.get(ue_mere_id)

        if not ue_mere or ue_mere.type_element != 'ue_composite':
            return None

        # Récupérer tous les EC
        elements_constitutifs = ue_mere.elements_constitutifs.all()

        if not elements_constitutifs:
            return None

        total_points = 0
        total_coefs = 0
        notes_manquantes = False

        for ec in elements_constitutifs:
            # Récupérer la note de l'étudiant pour cet EC
            note_obj = Note.query.filter_by(
                ue_id=ec.id,
                etudiant_id=etudiant_id
            ).first()

            if not note_obj or note_obj.note is None:
                notes_manquantes = True
                continue

            # Calcul pondéré
            total_points += note_obj.note * ec.coefficient
            total_coefs += ec.coefficient

        # Si aucune note n'est disponible
        if total_coefs == 0:
            return None

        # Si des notes manquent, on retourne None (impossible de calculer)
        if notes_manquantes and len(elements_constitutifs) > total_coefs:
            return None

        # Calcul de la moyenne
        moyenne = total_points / total_coefs

        return round(moyenne, 2)

    @staticmethod
    def valider_coherence_ue(ue_data):
        """
        Valide la cohérence des données d'une UE selon les règles métier

        Règles:
        - UE libre DOIT être simple (pas composite)
        - UE libre doit avoir est_ouverte_a_tous = True
        - UE composite doit avoir au moins 1 EC
        - Somme des coefficients des EC doit être > 0

        Args:
            ue_data: Dict avec les données de l'UE

        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []

        # Règle 1: UE libre ne peut pas être composite
        if ue_data.get('categorie') == 'libre' and ue_data.get('nature') == 'composite':
            errors.append("Une UE libre ne peut pas être composite")

        # Règle 2: UE libre doit être ouverte à tous
        if ue_data.get('categorie') == 'libre' and not ue_data.get('est_ouverte_a_tous'):
            errors.append("Une UE libre doit être accessible à tous (est_ouverte_a_tous=True)")

        # Règle 3: UE composite doit avoir des EC
        if ue_data.get('nature') == 'composite':
            elements = ue_data.get('elements_constitutifs', [])
            if not elements or len(elements) < 1:
                errors.append("Une UE composite doit avoir au moins un élément constitutif")

        # Règle 4: Semestre valide
        semestre = ue_data.get('semestre', '')
        if not semestre.startswith('S') or semestre[1:] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            errors.append(f"Semestre invalide: {semestre}. Format attendu: S1, S2, ..., S10")

        return (len(errors) == 0, errors)

