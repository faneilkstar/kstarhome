"""
Agent IA pour génération automatique de rapports
Utilise les statistiques pour créer des analyses narratives
Version Optimisée : Moteur Sémantique et Profilage Avancé
"""

from datetime import datetime
import random
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from app.utils.statistiques_avancees import StatistiquesAvancees
from app.models import Classe, Filiere, Etudiant, Note
import os

class AgentIARapports:
    """Agent IA qui génère des rapports narratifs automatiques avec intelligence contextuelle"""

    def __init__(self):
        self.stats_engine = StatistiquesAvancees()
        self.output_dir = 'documents/rapports_ia'
        os.makedirs(self.output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        # Base de connaissances sémantique pour varier le vocabulaire (IA Generative simulée)
        self.vocabulaire = {
            'intro': [
                "L'analyse des données académiques révèle une dynamique intéressante pour la",
                "L'examen approfondi des résultats de la",
                "Sur le plan pédagogique, la",
                "Le profil statistique de la"
            ],
            'excellent': [
                "démontre une maîtrise exceptionnelle",
                "affiche une performance de premier plan",
                "se distingue par l'excellence de ses résultats",
                "surperforme les attentes académiques"
            ],
            'moyen': [
                "présente des résultats en consolidation",
                "montre une performance honorable mais perfectible",
                "se situe dans la moyenne académique attendue",
                "affiche un bilan contrasté mais prometteur"
            ],
            'faible': [
                "rencontre des difficultés structurelles",
                "nécessite une attention pédagogique immédiate",
                "affiche des indicateurs de performance préoccupants",
                "montre des signes de décrochage sur les fondamentaux"
            ]
        }

    def _setup_custom_styles(self):
        """Styles personnalisés pour PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        ))

    def _get_synonyme(self, cle):
        """Récupère une variation sémantique aléatoire"""
        return random.choice(self.vocabulaire.get(cle, [""]))

    def analyser_performance_classe(self, classe_id):
        """
        Analyse IA de la performance d'une classe avec détection de profils types
        """
        stats = self.stats_engine.stats_classe(classe_id)
        if not stats:
            return "Données insuffisantes pour l'analyse algorithmique."

        sd = stats['stats_descriptives']
        dist = stats['distribution']

        # Calculs dérivés pour l'IA
        taux_excellent = dist['excellent'] / stats['effectif'] * 100
        taux_ajourne = dist['ajourne'] / stats['effectif'] * 100
        ratio_elite_difficulte = taux_excellent / (taux_ajourne + 0.1) # +0.1 pour éviter div/0

        # Construction narrative IA Dynamique
        analyse = []

        # 1. Introduction Contextuelle
        intro_phrase = self._get_synonyme('intro')
        analyse.append(f"<b>Classe {stats['classe']}</b> ({stats['effectif']} étudiants). {intro_phrase} classe.")
        analyse.append("")

        # 2. Profilage Algorithmique (Le "Cerveau" de l'IA)
        # Détermination du profil de la classe basé sur Moyenne ET Écart-type
        profil = ""
        diagnostic = ""

        if sd['moyenne'] >= 13:
            if sd['ecart_type'] < 2.5:
                profil = "Excellence Homogène"
                diagnostic = "Un groupe moteur très performant avec peu de disparités."
                tendance_vocab = self._get_synonyme('excellent')
            else:
                profil = "Excellence Polarisée"
                diagnostic = "Une moyenne élevée tirée par une tête de classe brillante, masquant quelques élèves en retrait."
                tendance_vocab = "est tirée vers le haut par une élite académique"
        elif sd['moyenne'] >= 10:
            if sd['ecart_type'] < 2.5:
                profil = "Ventre Mou Homogène"
                diagnostic = "La classe a acquis les bases mais manque d'ambition ou de pics de performance."
                tendance_vocab = self._get_synonyme('moyen')
            else:
                profil = "Classe Hétérogène"
                diagnostic = "Cohabitation complexe entre élèves performants et élèves en difficulté majeure."
                tendance_vocab = "présente une fracture de niveau marquée"
        else:
            profil = "Difficulté Généralisée"
            diagnostic = "La majorité du groupe n'a pas validé les acquis fondamentaux."
            tendance_vocab = self._get_synonyme('faible')

        analyse.append(
            f"La performance globale {tendance_vocab} (Moyenne : <b>{sd['moyenne']}/20</b>).<br/>"
            f"L'algorithme identifie le profil suivant : <b>{profil}</b>.<br/>"
            f"<i>Analyse : {diagnostic}</i>"
        )
        analyse.append("")

        # 3. Analyse de la Dispersion (Hétérogénéité)
        analyse.append(f"<b>Structure du groupe :</b>")
        if sd['ecart_type'] < 2:
            dispersion_txt = "cohésion forte"
            consequence = "permettant une progression pédagogique rapide."
        elif sd['ecart_type'] < 3.5:
            dispersion_txt = "diversité standard"
            consequence = "nécessitant une attention ponctuelle aux extrêmes."
        else:
            dispersion_txt = "fragmentation importante"
            consequence = "qui risque de ralentir la dynamique de groupe sans différenciation."

        analyse.append(f"L'indice de dispersion ({sd['ecart_type']}) révèle une <b>{dispersion_txt}</b>, {consequence}")

        # 4. Insights basés sur la distribution (Data Mining)
        analyse.append(f"<br/><b>Indicateurs de Réussite :</b>")

        if ratio_elite_difficulte > 2:
            insight = "Le groupe est solidement ancré dans la réussite, les difficultés sont marginales."
            couleur = "green"
        elif ratio_elite_difficulte < 0.5:
            insight = "Le volume d'étudiants en échec dépasse largement celui des excellents."
            couleur = "red"
        else:
            insight = "Équilibre précaire entre réussite et échec."
            couleur = "orange"

        analyse.append(f"• Taux de validation : <b>{stats['taux_reussite']}%</b>")
        analyse.append(f"• Excellence (>16/20) : {round(taux_excellent, 1)}%")
        analyse.append(f"• Zone critique (<10/20) : {round(taux_ajourne, 1)}%")
        analyse.append(f"<font color='{couleur}'>-> {insight}</font>")
        analyse.append("")

        # 5. Recommandations IA Prescriptives (Actionables)
        analyse.append("<b>Stratégie Pédagogique Recommandée :</b>")
        actions = []

        if profil == "Excellence Homogène":
            actions.append("• Accélérer le rythme du programme pour maintenir la stimulation.")
            actions.append("• Proposer des projets complexes ou des concours inter-écoles.")
        elif profil == "Excellence Polarisée":
            actions.append("• Utiliser les élèves leaders comme tuteurs pour les élèves en retrait.")
            actions.append("• Vérifier si les écarts proviennent de UE spécifiques.")
        elif profil == "Classe Hétérogène":
            actions.append("• Impératif : Mettre en place des groupes de niveau.")
            actions.append("• Adapter les évaluations (notation différenciée ou progressive).")
        elif profil == "Difficulté Généralisée":
            actions.append("• URGENCE : Audit des pré-requis (le niveau n-1 est-il acquis ?).")
            actions.append("• Organiser des séances de remédiation sur les fondamentaux.")

        # Ajout d'une recommandation basée sur le taux de réussite brut
        if stats['taux_reussite'] < 50:
             actions.append("• <b>Alerte administrative :</b> Un conseil de classe exceptionnel est suggéré.")

        for action in actions:
            analyse.append(action)

        return "<br/>".join(analyse)

    def generer_rapport_annuel_ecole(self, annee_academique=None):
        """
        Génère le rapport annuel complet de l'école avec analyse IA
        """
        if not annee_academique:
            from config import Config
            annee_academique = Config.ANNEE_ACADEMIQUE_ACTUELLE

        filename = f'rapport_annuel_{annee_academique}_{datetime.now().strftime("%Y%m%d")}.pdf'
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                topMargin=2 * cm, bottomMargin=2 * cm,
                                leftMargin=2.5 * cm, rightMargin=2.5 * cm)

        story = []

        # PAGE DE GARDE (Design pro)
        story.append(Spacer(1, 3 * cm))
        story.append(Paragraph(
            f"AUDIT ACADÉMIQUE &<br/>RAPPORT DE PERFORMANCE",
            self.styles['CustomTitle']
        ))
        story.append(Paragraph(f"Année : {annee_academique}", self.styles['CustomHeading2']))
        story.append(Spacer(1, 2 * cm))

        # Logo IA (simulé par texte ici, mais image possible)
        story.append(Paragraph("<i>Analyse générée par le moteur Infinity AI</i>", self.styles['BodyText']))
        story.append(Paragraph(f"Date du rapport : {datetime.now().strftime('%d/%m/%Y à %H:%M')}", self.styles['BodyText']))
        story.append(PageBreak())

        # SYNTHÈSE GLOBALE
        story.append(Paragraph("1. SYNTHÈSE ET KPI GLOBAUX", self.styles['CustomHeading2']))

        total_etudiants = Etudiant.query.filter_by(statut_inscription='accepté').count()
        total_classes = Classe.query.filter_by(active=True).count()

        # Calcul d'un "Score de Santé" global de l'école (fictif basé sur les données)
        # Ici on simule une agrégation simple
        synthese = f"""
        L'analyse porte sur un effectif de <b>{total_etudiants} apprenants</b> répartis dans <b>{total_classes} structures pédagogiques</b>.
        Le système a traité l'ensemble des notes pour dégager les tendances majeures de l'année {annee_academique}.
        """
        story.append(Paragraph(synthese, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.5 * cm))

        # ANALYSE PAR CLASSE
        story.append(Paragraph("2. ANALYSE GRANULAIRE PAR CLASSE", self.styles['CustomHeading2']))

        classes = Classe.query.filter_by(active=True).all()
        for classe in classes:  # Analyse de toutes les classes
            analyse_classe = self.analyser_performance_classe(classe.id)
            story.append(Paragraph(analyse_classe, self.styles['BodyJustify']))
            story.append(Spacer(1, 0.5 * cm))

            # Ligne de séparation
            story.append(Paragraph("_" * 60, self.styles['BodyJustify']))
            story.append(Spacer(1, 0.5 * cm))

        # === CONCLUSIONS ET RECOMMANDATIONS STRATÉGIQUES ===
        story.append(PageBreak())
        story.append(Paragraph(
            "3. CONCLUSIONS & RECOMMANDATIONS STRATÉGIQUES",
            self.styles['SectionHeading']
        ))
        story.append(Spacer(1, 0.5 * cm))

        # Synthèse analytique
        conclusion_principale = f"""
        <b>Analyse transversale :</b><br/>
        Sur la base des {len(classes)} profils de classe identifiés et des {total_notes} évaluations analysées, 
        le moteur Infinity AI a détecté des dynamiques différenciées nécessitant une approche ciblée.
        """
        story.append(Paragraph(conclusion_principale, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.8 * cm))

        # Recommandations prioritaires dans un encadré
        story.append(Paragraph(
            "🎯 RECOMMANDATIONS PRIORITAIRES",
            self.styles['Highlight']
        ))
        story.append(Spacer(1, 0.3 * cm))

        recommandations = [
            ("Allocation des ressources",
             "Orienter prioritairement les ressources pédagogiques vers les classes en 'Difficulté Généralisée' "
             "pour éviter un taux d'échec structurel."),

            ("Surveillance des écarts-types",
             "Les classes présentant des écarts-types élevés (>3.5) signalent un risque de décrochage masqué. "
             "Un suivi individualisé est impératif."),

            ("Valorisation de l'excellence",
             "Les classes en 'Excellence Homogène' doivent bénéficier de programmes accélérés pour maintenir "
             "la dynamique de performance."),

            ("Audit pédagogique",
             "Pour les classes sous la moyenne générale, un audit des pré-requis du niveau précédent "
             "est recommandé avant la prochaine année."),
        ]

        for titre, texte in recommandations:
            story.append(Paragraph(
                f'<b><font color="{PolytechColors.BLUE_PRIMARY.hexval()}">• {titre} :</font></b> {texte}',
                self.styles['Recommendation']
            ))
            story.append(Spacer(1, 0.3 * cm))

        story.append(Spacer(1, 1 * cm))

        # Signature IA
        signature = f"""
        <para align="right" fontSize="10" textColor="gray">
        <i>Rapport généré automatiquement par Infinity AI v2.0</i><br/>
        <i>Polytech Academy - Direction des Études</i><br/>
        <i>{datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>
        </para>
        """
        story.append(Paragraph(signature, self.styles['BodyText']))

        # Pied de page final
        story.append(Spacer(1, 2 * cm))
        footer_final = f"""
        <para align="center" fontSize="8" textColor="{PolytechColors.GRAY.hexval()}">
        Document confidentiel - Usage strictement interne<br/>
        © 2026 Polytech Academy - Tous droits réservés
        </para>
        """
        story.append(Paragraph(footer_final, self.styles['BodyText']))

        # CONSTRUCTION PDF AVEC GESTION D'ERREURS
        try:
            # Fonction pour ajouter en-tête et pied de page sur chaque page
            def add_page_decorations(canvas_obj, doc_obj):
                canvas_obj.saveState()
                width, height = A4

                # En-tête simplifié sur chaque page (sauf première)
                if doc_obj.page > 1:
                    canvas_obj.setFont('Helvetica-Bold', 10)
                    canvas_obj.setFillColor(PolytechColors.BLUE_DARK)
                    canvas_obj.drawString(2.5*cm, height - 1.5*cm, "RAPPORT ANNUEL ACADÉMIQUE")
                    canvas_obj.setFont('Helvetica', 9)
                    canvas_obj.setFillColor(PolytechColors.GRAY)
                    canvas_obj.drawRightString(width - 2.5*cm, height - 1.5*cm, f"Année {annee_academique}")

                    # Ligne de séparation
                    canvas_obj.setStrokeColor(PolytechColors.GOLD)
                    canvas_obj.setLineWidth(1)
                    canvas_obj.line(2.5*cm, height - 2*cm, width - 2.5*cm, height - 2*cm)

                # Pied de page sur chaque page
                canvas_obj.setFont('Helvetica', 8)
                canvas_obj.setFillColor(PolytechColors.GRAY)
                canvas_obj.drawCentredString(width/2, 1.5*cm, f"Page {doc_obj.page}")
                canvas_obj.drawString(2.5*cm, 1*cm, "Polytech Academy")
                canvas_obj.drawRightString(width - 2.5*cm, 1*cm, "Confidentiel")

                canvas_obj.restoreState()

            doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
            print(f"✅ Rapport généré avec succès : {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generer_rapport_filiere(self, filiere_id, annee_academique=None):
        """Génère un rapport détaillé pour une filière spécifique"""
        # Logique similaire à implémenter si besoin
        pass


def generer_rapport_pdf_ue(ue, rapport, enseignant):
    """
    Génère un rapport PDF détaillé pour une UE avec analyse IA

    Args:
        ue: Instance de l'UE
        rapport: Dictionnaire avec les statistiques et l'analyse IA
        enseignant: Instance de l'enseignant

    Returns:
        BytesIO: Buffer contenant le PDF
    """
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()

    # Style titre
    style_titre = ParagraphStyle(
        'Titre',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    style_sous_titre = ParagraphStyle(
        'SousTitre',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2b6cb0'),
        spaceAfter=12
    )

    style_normal = ParagraphStyle(
        'Normal2',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    # En-tête
    story.append(Paragraph("📊 RAPPORT D'ANALYSE PÉDAGOGIQUE", style_titre))
    story.append(Paragraph(f"UE : {ue.code_ue} - {ue.intitule}", style_sous_titre))
    story.append(Paragraph(f"Enseignant : {enseignant.nom} {enseignant.prenom}", style_normal))
    story.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", style_normal))
    story.append(Spacer(1, 20))

    # Statistiques descriptives
    story.append(Paragraph("📈 STATISTIQUES DESCRIPTIVES", style_sous_titre))

    desc = rapport['descriptives']
    data_desc = [
        ['Indicateur', 'Valeur'],
        ['Nombre d\'étudiants', str(desc['nb_notes'])],
        ['Moyenne', f"{desc['moyenne']}/20"],
        ['Médiane', f"{desc['mediane']}/20"],
        ['Écart-type', str(desc['ecart_type'])],
        ['Note minimale', f"{desc['min']}/20"],
        ['Note maximale', f"{desc['max']}/20"],
        ['Taux de réussite', f"{desc['taux_reussite']}%"],
        ['Réussis', str(desc['nb_reussis'])],
        ['Ajournés', str(desc['nb_ajournes'])]
    ]

    table_desc = Table(data_desc, colWidths=[8*cm, 6*cm])
    table_desc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f5ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0'))
    ]))
    story.append(table_desc)
    story.append(Spacer(1, 20))

    # Analyse IA
    story.append(Paragraph("🤖 ANALYSE IA (Gemini)", style_sous_titre))

    analyse = rapport.get('analyse_ia', {})

    if analyse.get('synthese'):
        story.append(Paragraph(f"<b>Synthèse :</b> {analyse['synthese']}", style_normal))
        story.append(Spacer(1, 10))

    if analyse.get('points_forts'):
        story.append(Paragraph("<b>✅ Points forts :</b>", style_normal))
        for point in analyse['points_forts']:
            story.append(Paragraph(f"• {point}", style_normal))
        story.append(Spacer(1, 10))

    if analyse.get('axes_amelioration'):
        story.append(Paragraph("<b>⚠️ Axes d'amélioration :</b>", style_normal))
        for axe in analyse['axes_amelioration']:
            story.append(Paragraph(f"• {axe}", style_normal))
        story.append(Spacer(1, 10))

    if analyse.get('recommandations'):
        story.append(Paragraph("<b>💡 Recommandations :</b>", style_normal))
        for reco in analyse['recommandations']:
            story.append(Paragraph(f"• {reco}", style_normal))
        story.append(Spacer(1, 10))

    if analyse.get('pourquoi'):
        story.append(Paragraph(f"<b>📊 Explication des résultats :</b> {analyse['pourquoi']}", style_normal))

    story.append(Spacer(1, 20))

    # Statistiques inférentielles
    story.append(Paragraph("📐 STATISTIQUES INFÉRENTIELLES", style_sous_titre))

    inf = rapport.get('inferentielles', {})

    story.append(Paragraph(f"<b>Corrélation absences-notes :</b> {inf.get('correlation_absences_notes', 'N/A')}", style_normal))
    story.append(Paragraph(f"<b>Interprétation :</b> {inf.get('interpretation_correlation', 'N/A')}", style_normal))
    story.append(Paragraph(f"<b>Test de normalité :</b> {inf.get('normalite_interpretation', 'N/A')}", style_normal))

    story.append(Spacer(1, 30))

    # Pied de page
    story.append(Paragraph("─" * 50, style_normal))
    story.append(Paragraph(
        f"Rapport généré automatiquement par KstarHome - {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.gray, alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        "Créé par Ing. KOISSI-ZO Tonyi Constantin - Électronique de Puissance",
        ParagraphStyle('Footer2', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)

    return buffer
