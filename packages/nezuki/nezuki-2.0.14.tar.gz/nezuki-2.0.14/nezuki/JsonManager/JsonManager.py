import json
import os
import re
from jsonpath_ng import parse
from nezuki.Logger import get_nezuki_logger

# Inizializza il logger di Nezuki con il flag internal=True
logger = get_nezuki_logger()

class JsonManager:
    """
    Questa classe permette di gestire file JSON, supportando lettura, scrittura e modifica dei dati.
    """

    def __init__(self, json_data: dict | str | list = {}):
        """
        Istanzia l'oggetto JsonManager con un JSON iniziale.

        Args:
            json_data (dict|str|list, optional): JSON di partenza, può essere un dizionario, una stringa JSON o una lista.
        """
        self.data = {}
        self.load_data(json_data)

    def load_data(self, data: dict | str | list) -> None:
        """
        Carica e decodifica il JSON.

        Args:
            data (dict|str|list): JSON da caricare.

        Returns:
            None: Il dato viene salvato nell'attributo `self.data`.
        """
        if isinstance(data, str) and os.path.exists(data):
            logger.debug(f"Caricamento JSON da file: {data}", extra={"internal": True})
            data = self.read_json(data)

        try:
            if isinstance(data, dict):
                self.data = data
            elif isinstance(data, str):
                self.data = json.loads(data)
            elif isinstance(data, list):
                self.data = json.loads(json.dumps(data))  # Normalizza in JSON
            else:
                raise ValueError("Tipo di dato non supportato per il JSON")
        except Exception as e:
            logger.error(f"Errore nel caricamento del JSON: {e}", extra={"internal": True})
            self.data = {}

    def read_json(self, path: str) -> dict:
        """
        Legge un file JSON da un percorso e restituisce il suo contenuto come dizionario.

        Args:
            path (str): Percorso assoluto del file JSON.

        Returns:
            dict: Contenuto del file JSON.
        """
        if not os.path.exists(path):
            logger.error(f"File JSON non trovato: {path}", extra={"internal": True})
            return {}

        try:
            with open(path, "r", encoding="utf-8") as file_json:
                content = json.load(file_json)
                logger.debug(f"JSON caricato correttamente da '{path}'", extra={"internal": True})
                return content
        except json.JSONDecodeError as e:
            logger.error(f"Errore di parsing JSON nel file '{path}': {e}", extra={"internal": True})
        except Exception as e:
            logger.error(f"Errore nella lettura del file JSON '{path}': {e}", extra={"internal": True})

        return {}

    def retrieveKey(self, key: str) -> str | list:
        """
        Recupera il valore corrispondente a un pattern JSONPath.

        Args:
            key (str): Il percorso della chiave da estrarre, es. "$.tastiera.inline_keyboard[*][*].text"

        Returns:
            str | list: Il valore associato alla chiave cercata o una lista di valori se ci sono più corrispondenze.
        """

        try:
            jsonpath_expression = parse(key)
            results = [match.value for match in jsonpath_expression.find(self.data)]

            if not results:
                logger.warning(f"Nessun valore trovato per la chiave '{key}'", extra={"internal": True})
                return []

            if len(results) == 1:
                logger.debug(f"Valore trovato: {results[0]} per la chiave '{key}'", extra={"internal": True})
                return results[0]

            logger.debug(f"Valori trovati ({len(results)}) per la chiave '{key}': {results}", extra={"internal": True})
            return results
        except Exception as e:
            logger.error(f"Errore durante il recupero della chiave '{key}': {e}", extra={"internal": True})
            return []

    def updateKey(self, pattern: str, value: any) -> bool:
        """
        Aggiorna il valore di una chiave JSON utilizzando JSONPath.

        Args:
            pattern (str): Espressione JSONPath della chiave da aggiornare.
            value (any): Nuovo valore da assegnare.

        Returns:
            bool: `True` se l'aggiornamento è riuscito, `False` in caso contrario.
        """
        try:
            jsonpath_expr = parse(pattern)
            matches = jsonpath_expr.find(self.data)

            if not matches:
                logger.warning(f"Nessuna chiave trovata con il pattern '{pattern}'", extra={"internal": True})
                return False

            jsonpath_expr.update(self.data, value)
            logger.debug(f"Aggiornato '{pattern}' con il valore '{value}'", extra={"internal": True})
            return True
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento della chiave '{pattern}': {e}", extra={"internal": True})
            return False

# --- ESEMPIO DI UTILIZZO ---
if __name__ == "__main__":
    json_data = {
        "utente": {
            "nome": "Sergio",
            "età": 28
        },
        "hobby": ["programmazione", "anime", "gaming"]
    }

    manager = JsonManager(json_data)

    # Recupero dati
    print(manager.retrieveKey("$.utente.nome"))  # Output: "Sergio"

    # Aggiornamento chiave
    manager.updateKey("$.utente.nome", "Andrea")

    print(manager.retrieveKey("$.utente.nome"))  # Output: "Andrea"

# json_data = {
#     "message_id": 22050,
#     "chat_id": 115420076,
#     "bot_id": 5270541563,
#     "lingua": 8,
#     "tastiera": {
#       "inline_keyboard": [
#         [
#           {
#             "text": "Erbaiuto",
#             "callback_data": "Pokdx Ability 1 65"
#           },
#           {
#             "text": "Clorofilla",
#             "callback_data": "Pokdx Ability 1 34"
#           }
#         ],
#         [
#           {
#             "text": "🔙 Bulbasaur",
#             "callback_data": "Pokdx Info Cerca 1"
#           }
#         ]
#       ]
#     }
#   }

# x = JsonManager({'ok': True, 'results': [], 'rows_affected': 0, 'error': None})
# print(x.retrieveKey("results[0][0]"))
# x.updateKey('$.tastiera.inline_keyboard[*][*].text',"miaomiao")
# print(x.data)

