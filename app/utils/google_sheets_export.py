"""
Export automatique vers Google Sheets
"""

import os
import json
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.models import SessionTP, MesureSimulation, InteractionIA


class GoogleSheetsExporter:
    """Export des données de TP vers Google Sheets"""

    def __init__(self):
        # Clés d'API Google (à mettre dans .env)
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']

        try:
            self.creds = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.scopes
            )
            self.service = build('sheets', 'v4', credentials=self.creds)
        except:
            print("⚠️ Google Sheets API non configurée")
            self.service = None

    def creer_spreadsheet(self, titre):
        """
        Crée un nouveau Google Spreadsheet

        Returns:
            str: ID du spreadsheet créé
        """
        if not self.service:
            return None

        try:
            spreadsheet = {
                'properties': {
                    'title': titre
                }
            }

            sheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()

            return sheet.get('spreadsheetId')

        except HttpError as error:
            print(f"Erreur création spreadsheet : {error}")
            return None

    def exporter_session(self, session_tp, spreadsheet_id=None):
        """
        Exporte une session de TP vers Google Sheets

        Args:
            session_tp: SessionTP à exporter
            spreadsheet_id: ID du spreadsheet (None = créer nouveau)

        Returns:
            str: URL du spreadsheet
        """
        if not self.service:
            return None

        # Créer un nouveau spreadsheet si nécessaire
        if not spreadsheet_id:
            titre = f"TP_{session_tp.tp.titre}_{session_tp.etudiant.get_nom_complet()}"
            spreadsheet_id = self.creer_spreadsheet(titre)

            if not spreadsheet_id:
                return None

        try:
            # ========== FEUILLE 1 : INFORMATIONS ==========
            infos_data = [
                ['RAPPORT DE TRAVAUX PRATIQUES'],
                [''],
                ['TP', session_tp.tp.titre],
                ['Type', session_tp.tp.type_simulation],
                ['Étudiant', session_tp.etudiant.get_nom_complet()],
                ['Matricule', session_tp.etudiant.matricule],
                ['Classe', session_tp.etudiant.classe.nom_classe if session_tp.etudiant.classe else '-'],
                ['Date', session_tp.date_debut.strftime('%d/%m/%Y %H:%M')],
                ['Durée', f"{session_tp.duree_minutes or 0} minutes"],
                ['Mesures effectuées', str(session_tp.nb_mesures or 0)],
                [''],
                ['ÉVALUATION'],
                ['Note IA', f"{session_tp.note_ia or '-'}/20"],
                ['Note Finale', f"{session_tp.note_finale or '-'}/20"],
            ]

            self._write_to_sheet(spreadsheet_id, 'Informations!A1', infos_data)

            # ========== FEUILLE 2 : MESURES ==========
            mesures = MesureSimulation.query.filter_by(
                session_id=session_tp.id
            ).order_by(MesureSimulation.timestamp).all()

            mesures_data = [['N°', 'Temps (s)', 'Paramètres', 'Résultats', 'Horodatage']]

            for idx, mesure in enumerate(mesures, 1):
                parametres_str = self._json_to_text(mesure.parametres)
                resultats_str = self._json_to_text(mesure.resultats)

                mesures_data.append([
                    idx,
                    mesure.temps_relatif or 0,
                    parametres_str,
                    resultats_str,
                    mesure.timestamp.strftime('%H:%M:%S')
                ])

            # Créer la feuille Mesures
            self._create_sheet(spreadsheet_id, 'Mesures')
            self._write_to_sheet(spreadsheet_id, 'Mesures!A1', mesures_data)

            # ========== FEUILLE 3 : INTERACTIONS IA ==========
            interactions = InteractionIA.query.filter_by(
                session_id=session_tp.id
            ).order_by(InteractionIA.timestamp).all()

            ia_data = [['N°', 'Question', 'Réponse IA', 'Heure']]

            for idx, interaction in enumerate(interactions, 1):
                ia_data.append([
                    idx,
                    interaction.question_etudiant,
                    interaction.reponse_ia,
                    interaction.timestamp.strftime('%H:%M:%S')
                ])

            self._create_sheet(spreadsheet_id, 'Assistant IA')
            self._write_to_sheet(spreadsheet_id, 'Assistant IA!A1', ia_data)

            # Formatage
            self._formater_spreadsheet(spreadsheet_id)

            # URL du spreadsheet
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

            return url

        except HttpError as error:
            print(f"Erreur export : {error}")
            return None

    def _write_to_sheet(self, spreadsheet_id, range_name, values):
        """Écrit des données dans une feuille"""
        body = {'values': values}

        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

    def _create_sheet(self, spreadsheet_id, title):
        """Crée une nouvelle feuille dans le spreadsheet"""
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': title
                        }
                    }
                }]
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
        except:
            pass  # Feuille existe déjà

    def _formater_spreadsheet(self, spreadsheet_id):
        """Applique un formatage aux feuilles"""
        requests = [
            # En-têtes en gras
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            }
        ]

        body = {'requests': requests}

        try:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
        except:
            pass

    def _json_to_text(self, json_str):
        """Convertit JSON en texte lisible"""
        if not json_str:
            return ''

        try:
            data = json.loads(json_str)
            return ', '.join([f"{k}={v}" for k, v in data.items()])
        except:
            return str(json_str)