"""
Export avancé des rapports de TP avec graphiques matplotlib
"""

import os
from datetime import datetime
import json
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from app.models import SessionTP, MesureSimulation, InteractionIA


class ExporteurTPAvance:
    """Générateur de rapports PDF professionnels avec graphiques"""

    def __init__(self):
        self.output_dir = 'documents/rapports_tp'
        self.graphs_dir = 'static/graphs_tp'
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.graphs_dir, exist_ok=True)

        # Style matplotlib
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")

    def generer_rapport_complet(self, session_tp):
        """
        Génère un rapport PDF complet avec graphiques intégrés

        Returns:
            str: Chemin du fichier PDF
        """
        filename = f"Rapport_TP_{session_tp.tp.id}_Session_{session_tp.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                topMargin=2 * cm, bottomMargin=2 * cm,
                                leftMargin=2.5 * cm, rightMargin=2.5 * cm)

        story = []
        styles = getSampleStyleSheet()

        # Style personnalisé
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # ============ PAGE DE GARDE ============
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph("RAPPORT DE TRAVAUX PRATIQUES", title_style))
        story.append(Spacer(1, 0.5 * cm))

        # Logo de l'école (si disponible)
        logo_path = 'static/images/logo_ecole.png'
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=4 * cm, height=4 * cm))
            story.append(Spacer(1, 1 * cm))

        # Informations générales
        info_table = Table([
            ['TP :', session_tp.tp.titre],
            ['Type :', session_tp.tp.type_simulation.upper()],
            ['UE :', f"{session_tp.tp.ue.code_ue} - {session_tp.tp.ue.intitule}" if session_tp.tp.ue else 'N/A'],
            ['Étudiant :', session_tp.etudiant.get_nom_complet()],
            ['Classe :', session_tp.etudiant.classe.nom_classe if session_tp.etudiant.classe else '-'],
            ['Date :', session_tp.date_debut.strftime('%d/%m/%Y à %H:%M')],
            ['Durée :', f"{session_tp.duree_minutes or 0} minutes"],
            ['Assistant IA :', session_tp.tp.ia_nom],
        ], colWidths=[4 * cm, 11 * cm])

        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(info_table)
        story.append(PageBreak())

        # ============ GRAPHIQUES D'ANALYSE ============
        story.append(Paragraph("ANALYSE GRAPHIQUE DES RÉSULTATS", styles['Heading1']))
        story.append(Spacer(1, 0.5 * cm))

        # Générer les graphiques
        graphs = self._generer_graphiques_analyse(session_tp)

        for graph_path, description in graphs:
            if os.path.exists(graph_path):
                story.append(Paragraph(description, styles['Heading2']))
                story.append(Spacer(1, 0.3 * cm))
                story.append(Image(graph_path, width=15 * cm, height=9 * cm))
                story.append(Spacer(1, 0.5 * cm))

        story.append(PageBreak())

        # ============ ÉVALUATION IA ============
        story.append(Paragraph("ÉVALUATION AUTOMATIQUE", styles['Heading1']))
        story.append(Spacer(1, 0.5 * cm))

        if session_tp.note_ia:
            eval_table = Table([
                ['Note automatique', f"{session_tp.note_ia}/20"],
                ['Assistant IA', session_tp.tp.ia_nom],
                ['Mesures effectuées', str(session_tp.nb_mesures or 0)],
            ], colWidths=[7 * cm, 8 * cm])

            eval_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4caf50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))

            story.append(eval_table)
            story.append(Spacer(1, 0.5 * cm))

            if session_tp.commentaire_ia:
                story.append(Paragraph("<b>Commentaire de l'IA :</b>", styles['Normal']))
                story.append(Paragraph(session_tp.commentaire_ia.replace('\n', '<br/>'), styles['Normal']))

        story.append(PageBreak())

        # ============ INTERACTIONS IA ============
        story.append(Paragraph("HISTORIQUE DES INTERACTIONS IA", styles['Heading1']))
        story.append(Spacer(1, 0.5 * cm))

        interactions = InteractionIA.query.filter_by(session_id=session_tp.id).order_by(InteractionIA.timestamp).all()

        if interactions:
            for idx, interaction in enumerate(interactions[:10], 1):  # Limite à 10
                story.append(Paragraph(f"<b>Question {idx} :</b> {interaction.question_etudiant}", styles['Normal']))
                story.append(Spacer(1, 0.2 * cm))
                story.append(Paragraph(f"<b>{interaction.ia_nom} :</b> {interaction.reponse_ia}", styles['Normal']))
                story.append(Spacer(1, 0.5 * cm))
        else:
            story.append(Paragraph("Aucune interaction avec l'IA durant cette session.", styles['Normal']))

        # Construction finale
        doc.build(story)

        return filepath

    def _generer_graphiques_analyse(self, session_tp):
        """
        Génère des graphiques d'analyse matplotlib

        Returns:
            list: [(chemin_fichier, description), ...]
        """
        graphs = []
        mesures = MesureSimulation.query.filter_by(session_id=session_tp.id).order_by(MesureSimulation.timestamp).all()

        if len(mesures) < 2:
            return graphs

        # ========== GRAPHIQUE 1 : ÉVOLUTION TEMPORELLE ==========
        try:
            fig, ax = plt.subplots(figsize=(12, 6))

            timestamps = [m.timestamp for m in mesures]
            # Extraire une valeur des résultats (flexible selon le type)
            valeurs = []
            for m in mesures:
                if m.resultats:
                    res = json.loads(m.resultats)
                    # Prendre la première valeur numérique trouvée
                    for key, val in res.items():
                        try:
                            valeurs.append(float(val))
                            break
                        except:
                            continue

            if len(valeurs) == len(timestamps):
                ax.plot(range(len(timestamps)), valeurs, marker='o', linewidth=2, markersize=6, color='#1976d2')
                ax.set_xlabel('Numéro de mesure', fontsize=12)
                ax.set_ylabel('Valeur mesurée', fontsize=12)
                ax.set_title('Évolution des mesures au cours du TP', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)

                graph1_path = os.path.join(self.graphs_dir, f'evolution_{session_tp.id}.png')
                plt.tight_layout()
                plt.savefig(graph1_path, dpi=150, bbox_inches='tight')
                plt.close()

                graphs.append((graph1_path, "Évolution temporelle des mesures"))
        except Exception as e:
            print(f"Erreur graphique évolution : {e}")

        # ========== GRAPHIQUE 2 : DISTRIBUTION DES VALEURS ==========
        try:
            if len(valeurs) > 5:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(valeurs, bins=min(15, len(valeurs) // 2), edgecolor='black', color='#4caf50', alpha=0.7)
                ax.set_xlabel('Valeur', fontsize=12)
                ax.set_ylabel('Fréquence', fontsize=12)
                ax.set_title('Distribution des valeurs mesurées', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')

                graph2_path = os.path.join(self.graphs_dir, f'distribution_{session_tp.id}.png')
                plt.tight_layout()
                plt.savefig(graph2_path, dpi=150, bbox_inches='tight')
                plt.close()

                graphs.append((graph2_path, "Distribution statistique des mesures"))
        except Exception as e:
            print(f"Erreur graphique distribution : {e}")

        # ========== GRAPHIQUE 3 : ACTIVITÉ PAR PÉRIODE ==========
        try:
            fig, ax = plt.subplots(figsize=(10, 5))

            # Regrouper par tranche de 5 minutes
            debut = session_tp.date_debut
            periodes = {}

            for m in mesures:
                if m.timestamp and debut:
                    minutes_ecoulees = (m.timestamp - debut).total_seconds() / 60
                    periode = int(minutes_ecoulees // 5) * 5
                    periodes[periode] = periodes.get(periode, 0) + 1

            if periodes:
                x = sorted(periodes.keys())
                y = [periodes[k] for k in x]

                ax.bar(x, y, width=4, edgecolor='black', color='#ff9800', alpha=0.8)
                ax.set_xlabel('Temps (minutes)', fontsize=12)
                ax.set_ylabel('Nombre de mesures', fontsize=12)
                ax.set_title('Activité de mesure au cours du temps', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')

                graph3_path = os.path.join(self.graphs_dir, f'activite_{session_tp.id}.png')
                plt.tight_layout()
                plt.savefig(graph3_path, dpi=150, bbox_inches='tight')
                plt.close()

                graphs.append((graph3_path, "Répartition de l'activité dans le temps"))
        except Exception as e:
            print(f"Erreur graphique activité : {e}")

        return graphs