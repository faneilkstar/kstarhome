"""
Service d'IA pour la gestion intelligente de la bibliothèque
Tri automatique des livres par catégorie avec Gemini
Créé par : Ing. KOISSI-ZO Tonyi Constantin
Date : 11 Février 2026
"""

import os
try:
    import google.generativeai as genai
    GEMINI_DISPONIBLE = True
except ImportError:
    GEMINI_DISPONIBLE = False


class BibliothequeIA:
    """Gère le tri intelligent des livres avec l'IA Gemini"""

    # Catégories prédéfinies
    CATEGORIES = [
        'Mathématiques',
        'Physique',
        'Chimie',
        'Électronique',
        'Informatique',
        'Génie Civil',
        'Mécanique',
        'Électrotechnique',
        'Automatique',
        'Thermodynamique',
        'Économie',
        'Gestion',
        'Langues',
        'Sciences Humaines',
        'Roman',
        'Science-Fiction',
        'Histoire',
        'Philosophie',
        'Droit',
        'Médecine',
        'Biologie',
        'Environnement',
        'Agriculture',
        'Arts',
        'Sport',
        'Autre'
    ]

    def __init__(self):
        """Initialiser l'IA avec la clé API Gemini"""
        self.ia_activee = False

        if GEMINI_DISPONIBLE:
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key and api_key.strip():
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.ia_activee = True
                except Exception as e:
                    print(f"⚠️  Erreur configuration Gemini : {e}")

    def determiner_categorie(self, titre, auteur, description=None):
        """
        Détermine automatiquement la catégorie d'un livre

        Args:
            titre: Titre du livre
            auteur: Auteur du livre
            description: Description optionnelle

        Returns:
            str: Catégorie déterminée
        """
        if self.ia_activee:
            return self._determiner_avec_ia(titre, auteur, description)
        else:
            return self._determiner_sans_ia(titre, auteur)

    def _determiner_avec_ia(self, titre, auteur, description):
        """Utilise Gemini pour déterminer la catégorie"""

        categories_str = ", ".join(self.CATEGORIES)

        prompt = f"""Tu es un bibliothécaire expert. Analyse ce livre et détermine sa catégorie.

LIVRE À ANALYSER :
- Titre : {titre}
- Auteur : {auteur}
- Description : {description or 'Non fournie'}

CATÉGORIES DISPONIBLES :
{categories_str}

RÈGLES :
1. Choisis LA catégorie la plus appropriée parmi la liste
2. Si aucune ne correspond vraiment, réponds "Autre"
3. Réponds UNIQUEMENT avec le nom exact de la catégorie (un seul mot ou groupe de mots)

RÉPONSE (juste la catégorie) :"""

        try:
            response = self.model.generate_content(prompt)
            categorie_proposee = response.text.strip()

            # Vérifier si la catégorie est valide
            for cat in self.CATEGORIES:
                if cat.lower() in categorie_proposee.lower() or categorie_proposee.lower() in cat.lower():
                    return cat

            # Si pas trouvé, retourner "Autre"
            return "Autre"

        except Exception as e:
            print(f"⚠️  Erreur Gemini : {e}")
            return self._determiner_sans_ia(titre, auteur)

    def _determiner_sans_ia(self, titre, auteur):
        """Détermine la catégorie sans IA (règles basiques)"""

        titre_lower = titre.lower()

        # Mots-clés par catégorie
        keywords = {
            'Mathématiques': ['math', 'algèbre', 'géométrie', 'calcul', 'analyse', 'probabilité', 'statistique'],
            'Physique': ['physique', 'mécanique', 'optique', 'électromagnétisme', 'quantique', 'relativité'],
            'Chimie': ['chimie', 'chimique', 'molécule', 'atome', 'réaction', 'organique'],
            'Électronique': ['électronique', 'circuit', 'transistor', 'amplificateur', 'arduino', 'microcontrôleur'],
            'Informatique': ['informatique', 'programmation', 'python', 'java', 'algorithme', 'base de données', 'web', 'machine learning', 'ia'],
            'Génie Civil': ['génie civil', 'béton', 'structure', 'bâtiment', 'construction', 'pont'],
            'Mécanique': ['mécanique', 'moteur', 'automobile', 'aéronautique', 'robotique'],
            'Électrotechnique': ['électrotechnique', 'puissance', 'transformateur', 'moteur électrique', 'convertisseur'],
            'Automatique': ['automatique', 'régulation', 'asservissement', 'contrôle', 'pid'],
            'Thermodynamique': ['thermodynamique', 'chaleur', 'énergie', 'entropie', 'transfert thermique'],
            'Économie': ['économie', 'économique', 'marché', 'finance', 'monnaie'],
            'Gestion': ['gestion', 'management', 'entreprise', 'ressources humaines', 'marketing'],
            'Histoire': ['histoire', 'historique', 'guerre', 'civilisation', 'antiquité'],
            'Roman': ['roman', 'fiction', 'aventure', 'amour', 'thriller'],
            'Biologie': ['biologie', 'cellule', 'adn', 'génétique', 'organisme', 'vivant']
        }

        for categorie, mots in keywords.items():
            for mot in mots:
                if mot in titre_lower:
                    return categorie

        return "Autre"

    def generer_description(self, titre, auteur, categorie):
        """Génère une description automatique pour un livre"""

        if not self.ia_activee:
            return f"Ouvrage de {auteur} dans le domaine de {categorie}."

        prompt = f"""Génère une courte description (2-3 phrases) pour ce livre :
        
Titre : {titre}
Auteur : {auteur}
Catégorie : {categorie}

La description doit être informative et donner envie de lire le livre.
Réponds UNIQUEMENT avec la description (pas de titre, pas de préambule)."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()[:500]  # Limiter à 500 caractères
        except:
            return f"Ouvrage de {auteur} dans le domaine de {categorie}."

    def rechercher_livres(self, livres, query):
        """
        Recherche intelligente dans les livres

        Args:
            livres: Liste des livres
            query: Terme de recherche

        Returns:
            list: Livres correspondants triés par pertinence
        """
        query_lower = query.lower()
        resultats = []

        for livre in livres:
            score = 0

            # Score basé sur le titre
            if query_lower in livre.titre.lower():
                score += 10

            # Score basé sur l'auteur
            if query_lower in livre.auteur.lower():
                score += 5

            # Score basé sur la catégorie
            if livre.categorie and query_lower in livre.categorie.lower():
                score += 3

            # Score basé sur la description
            if livre.description and query_lower in livre.description.lower():
                score += 2

            if score > 0:
                resultats.append((livre, score))

        # Trier par score décroissant
        resultats.sort(key=lambda x: x[1], reverse=True)

        return [livre for livre, score in resultats]

    def suggerer_livres(self, livre_actuel, tous_les_livres):
        """Suggère des livres similaires basés sur la catégorie"""

        if not livre_actuel.categorie:
            return []

        similaires = [
            l for l in tous_les_livres
            if l.id != livre_actuel.id and l.categorie == livre_actuel.categorie
        ]

        return similaires[:5]  # Limiter à 5 suggestions


# Fonction utilitaire pour les routes
def get_categories():
    """Retourne la liste des catégories disponibles"""
    return BibliothequeIA.CATEGORIES

