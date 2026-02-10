"""
Module de statistiques avancées
Analyse descriptive et inférentielle des données académiques
"""

import numpy as np
import matplotlib

matplotlib.use('Agg')  # Backend sans GUI
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime
import os
from app.models import Etudiant, Note, Classe, UE, Filiere
from app import db

# Configuration style matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class StatistiquesAvancees:
    """Classe pour analyses statistiques avancées"""

    def __init__(self):
        self.output_dir = 'static/graphs'
        os.makedirs(self.output_dir, exist_ok=True)

    # ========== STATISTIQUES DESCRIPTIVES ==========

    def stats_descriptives(self, notes_list):
        """
        Calcule statistiques descriptives complètes

        Returns:
            dict: {
                'moyenne': float,
                'mediane': float,
                'mode': float,
                'ecart_type': float,
                'variance': float,
                'min': float,
                'max': float,
                'q1': float (1er quartile),
                'q3': float (3ème quartile),
                'etendue': float,
                'coefficient_variation': float
            }
        """
        if not notes_list:
            return None

        notes = np.array(notes_list)

        return {
            'moyenne': round(float(np.mean(notes)), 2),
            'mediane': round(float(np.median(notes)), 2),
            'mode': round(float(stats.mode(notes, keepdims=True)[0][0]), 2) if len(notes) > 1 else notes[0],
            'ecart_type': round(float(np.std(notes, ddof=1)), 2),
            'variance': round(float(np.var(notes, ddof=1)), 2),
            'min': round(float(np.min(notes)), 2),
            'max': round(float(np.max(notes)), 2),
            'q1': round(float(np.percentile(notes, 25)), 2),
            'q3': round(float(np.percentile(notes, 75)), 2),
            'etendue': round(float(np.ptp(notes)), 2),
            'coefficient_variation': round(float(np.std(notes, ddof=1) / np.mean(notes) * 100), 2) if np.mean(
                notes) != 0 else 0,
            'asymetrie': round(float(stats.skew(notes)), 2),
            'aplatissement': round(float(stats.kurtosis(notes)), 2)
        }

    def stats_classe(self, classe_id):
        """Statistiques complètes d'une classe"""
        classe = Classe.query.get(classe_id)
        if not classe:
            return None

        etudiants = classe.etudiants.filter_by(statut_inscription='accepté').all()
        moyennes = [e.get_moyenne_generale() for e in etudiants if e.get_moyenne_generale()]

        if not moyennes:
            return None

        stats_desc = self.stats_descriptives(moyennes)

        # Distribution par tranches
        distribution = {
            'excellent': sum(1 for m in moyennes if m >= 16),
            'bien': sum(1 for m in moyennes if 14 <= m < 16),
            'assez_bien': sum(1 for m in moyennes if 12 <= m < 14),
            'passable': sum(1 for m in moyennes if 10 <= m < 12),
            'ajourne': sum(1 for m in moyennes if m < 10)
        }

        return {
            'classe': classe.nom_classe,
            'effectif': len(etudiants),
            'stats_descriptives': stats_desc,
            'distribution': distribution,
            'taux_reussite': round(sum(1 for m in moyennes if m >= 10) / len(moyennes) * 100, 2)
        }

    # ========== STATISTIQUES INFÉRENTIELLES ==========

    def test_normalite(self, notes_list):
        """
        Test de normalité (Shapiro-Wilk)

        Returns:
            dict: {
                'statistic': float,
                'p_value': float,
                'est_normal': bool (True si p > 0.05)
            }
        """
        if len(notes_list) < 3:
            return None

        notes = np.array(notes_list)
        statistic, p_value = stats.shapiro(notes)

        return {
            'statistic': round(float(statistic), 4),
            'p_value': round(float(p_value), 4),
            'est_normal': p_value > 0.05
        }

    def comparaison_classes(self, classe_id1, classe_id2):
        """
        Compare deux classes avec test statistique

        Returns:
            dict: {
                't_statistic': float,
                'p_value': float,
                'significatif': bool,
                'interpretation': str
            }
        """
        classe1 = Classe.query.get(classe_id1)
        classe2 = Classe.query.get(classe_id2)

        moyennes1 = [e.get_moyenne_generale() for e in classe1.etudiants.filter_by(statut_inscription='accepté')
                     if e.get_moyenne_generale()]
        moyennes2 = [e.get_moyenne_generale() for e in classe2.etudiants.filter_by(statut_inscription='accepté')
                     if e.get_moyenne_generale()]

        if len(moyennes1) < 2 or len(moyennes2) < 2:
            return None

        # Test t de Student
        t_stat, p_value = stats.ttest_ind(moyennes1, moyennes2)

        return {
            'classe1': classe1.nom_classe,
            'classe2': classe2.nom_classe,
            't_statistic': round(float(t_stat), 4),
            'p_value': round(float(p_value), 4),
            'significatif': p_value < 0.05,
            'interpretation': 'Différence significative' if p_value < 0.05 else 'Pas de différence significative'
        }

    def correlation_ues(self, ue_id1, ue_id2):
        """
        Calcule la corrélation entre deux UE

        Returns:
            dict: {
                'pearson_r': float,
                'p_value': float,
                'interpretation': str
            }
        """
        # Récupérer les notes communes aux deux UE
        notes1_dict = {n.etudiant_id: n.note for n in Note.query.filter_by(ue_id=ue_id1) if n.note}
        notes2_dict = {n.etudiant_id: n.note for n in Note.query.filter_by(ue_id=ue_id2) if n.note}

        # Étudiants ayant notes dans les deux UE
        etudiants_communs = set(notes1_dict.keys()) & set(notes2_dict.keys())

        if len(etudiants_communs) < 3:
            return None

        notes1 = [notes1_dict[e] for e in etudiants_communs]
        notes2 = [notes2_dict[e] for e in etudiants_communs]

        r, p_value = stats.pearsonr(notes1, notes2)

        # Interprétation
        if abs(r) < 0.3:
            force = 'Faible'
        elif abs(r) < 0.7:
            force = 'Modérée'
        else:
            force = 'Forte'

        sens = 'positive' if r > 0 else 'négative'

        return {
            'pearson_r': round(float(r), 3),
            'p_value': round(float(p_value), 4),
            'significatif': p_value < 0.05,
            'interpretation': f'{force} corrélation {sens}'
        }

    # ========== VISUALISATIONS ==========

    def generer_histogramme(self, notes_list, titre, filename):
        """Génère un histogramme avec courbe normale"""
        plt.figure(figsize=(10, 6))

        notes = np.array(notes_list)

        # Histogramme
        n, bins, patches = plt.hist(notes, bins=10, density=True,
                                    alpha=0.7, color='steelblue', edgecolor='black')

        # Courbe normale théorique
        mu, sigma = notes.mean(), notes.std()
        x = np.linspace(notes.min(), notes.max(), 100)
        plt.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2,
                 label=f'Normale (μ={mu:.2f}, σ={sigma:.2f})')

        plt.xlabel('Notes', fontsize=12)
        plt.ylabel('Densité', fontsize=12)
        plt.title(titre, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generer_boxplot_comparaison(self, classes_data, filename):
        """
        Box plot comparant plusieurs classes

        Args:
            classes_data: dict {nom_classe: [moyennes]}
        """
        plt.figure(figsize=(12, 6))

        data = list(classes_data.values())
        labels = list(classes_data.keys())

        bp = plt.boxplot(data, labels=labels, patch_artist=True)

        # Coloration
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors * (len(data) // len(colors) + 1)):
            patch.set_facecolor(color)

        plt.ylabel('Moyennes', fontsize=12)
        plt.title('Comparaison des Classes - Box Plot', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generer_heatmap_absences(self, classe_id, filename):
        """Heatmap des absences par étudiant et UE"""
        classe = Classe.query.get(classe_id)
        etudiants = classe.etudiants.filter_by(statut_inscription='accepté').all()
        ues = classe.ues.all()

        if not etudiants or not ues:
            return None

        # Matrice absences
        data = []
        for etudiant in etudiants[:20]:  # Limite à 20 pour lisibilité
            row = []
            for ue in ues:
                nb_absences = etudiant.absences.filter_by(ue_id=ue.id).count()
                row.append(nb_absences)
            data.append(row)

        plt.figure(figsize=(12, 8))
        sns.heatmap(data,
                    xticklabels=[ue.code_ue for ue in ues],
                    yticklabels=[e.get_nom_complet()[:20] for e in etudiants[:20]],
                    annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Nombre d\'absences'})

        plt.title(f'Heatmap des Absences - {classe.nom_classe}', fontsize=14, fontweight='bold')
        plt.xlabel('UE', fontsize=12)
        plt.ylabel('Étudiants', fontsize=12)
        plt.tight_layout()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generer_courbe_evolution(self, etudiant_id, filename):
        """Courbe d'évolution des notes d'un étudiant"""
        etudiant = Etudiant.query.get(etudiant_id)
        notes = etudiant.notes.order_by(Note.date_saisie).all()

        if len(notes) < 2:
            return None

        plt.figure(figsize=(12, 6))

        x = range(len(notes))
        y = [n.note for n in notes]
        labels = [n.ue.code_ue for n in notes]

        plt.plot(x, y, marker='o', linewidth=2, markersize=8, color='steelblue')
        plt.axhline(y=10, color='red', linestyle='--', label='Seuil validation (10/20)')

        plt.xlabel('UE', fontsize=12)
        plt.ylabel('Note /20', fontsize=12)
        plt.title(f'Évolution des Notes - {etudiant.get_nom_complet()}', fontsize=14, fontweight='bold')
        plt.xticks(x, labels, rotation=45)
        plt.ylim(0, 20)
        plt.grid(True, alpha=0.3)
        plt.legend()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generer_scatter_correlation(self, ue_id1, ue_id2, filename):
        """Nuage de points montrant corrélation entre 2 UE"""
        ue1 = UE.query.get(ue_id1)
        ue2 = UE.query.get(ue_id2)

        # Notes communes
        notes1_dict = {n.etudiant_id: n.note for n in Note.query.filter_by(ue_id=ue_id1) if n.note}
        notes2_dict = {n.etudiant_id: n.note for n in Note.query.filter_by(ue_id=ue_id2) if n.note}

        etudiants_communs = set(notes1_dict.keys()) & set(notes2_dict.keys())

        if len(etudiants_communs) < 3:
            return None

        x = [notes1_dict[e] for e in etudiants_communs]
        y = [notes2_dict[e] for e in etudiants_communs]

        plt.figure(figsize=(10, 8))
        plt.scatter(x, y, alpha=0.6, s=100, color='steelblue', edgecolors='black')

        # Droite de régression
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", linewidth=2, label=f'Régression: y={z[0]:.2f}x+{z[1]:.2f}')

        # Corrélation
        r, _ = stats.pearsonr(x, y)

        plt.xlabel(f'{ue1.code_ue} - {ue1.intitule}', fontsize=12)
        plt.ylabel(f'{ue2.code_ue} - {ue2.intitule}', fontsize=12)
        plt.title(f'Corrélation entre UE (r={r:.3f})', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()

        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath