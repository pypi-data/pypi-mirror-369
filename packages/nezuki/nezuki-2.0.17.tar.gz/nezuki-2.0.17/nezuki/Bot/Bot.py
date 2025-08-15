from Common import *
import time, requests, traceback
from commonLogId import *

current_version = "2.0.1"

@versione("2.0.1")
class Bot:
    """ Classe che permette di dar vita al proprio bot personalizzato """
    
    token: str
    """ API Token fornito da BotFather """

    base_url: str
    """ URL dell'API del bot """

    running: bool
    """ Indica se il bot è in esecuzione e nel caso stopparlo """

    update_id: int
    """ Update ID relativo all'input ricevuto da Telegram API, usato anche come correlation-id/LogID """

    logWaiting: bool
    """ Flag utile per evitare spam di log indicando nei log 1 solo messaggio di attesa nuovi input dal bot """

    botName: str
    """ Nome del bot """
    botUsername: str
    """ Username del bot, unico su Telegram """

    botId: str
    """ Chat ID Telegram del bot """

    logId: str
    """ Autogenerato, identifica il log per singolo update """
    
    def __init__(self, token, localMode: bool = False, localFileLogPath: str = "/"):
        """ Inizializza il bot e la parte relativa ai log, compreso il webserver """
        print(localFileLogPath)
        self.logger = get_logger(localMode, localFileLogPath)
        self.token = token
        self.base_url = f"http://localhost:8081/bot{token}"
        self.host = "localhost"
        self.port = 8081
        self.protocol = "http"
        self.path_start = f"/bot{token}"
        self.running = False
        self.update_id = None
        self.logWaiting = True
        self._get_me_()
        # Agganciamo il bot al webserver dei log
        self.register_to_log_server()
    
    def _get_me_(self):
        """ Ottiene informazioni relative al bot in esecuzione """
        methodName = "getMe"
        url = f"{self.base_url}/{methodName}"
        payload = {}
        response = requests.post(url=url, data=payload).json()
        self.botName: str = response['result']['first_name']
        self.botUsername: str = response['result']['username']
        self.botId: str = response['result']['id']
        self.logger.debug(f"Ottenute informazioni bot", extra={"internal": True, "esito_funzionale": 0, "details": f"{response['result']}"})
    
    def start_polling(self, interval=0):
        """ Avvia il listening di nuovi input del bot """
        self.running = True
        while self.running:
            updates = self.get_updates()
            if updates:
                self.process_updates(updates)
            time.sleep(interval)

        self.remove_from_log_server()

    
    def stop_polling(self):
        """ Ferma il listening di nuovi input """
        self.running = False
        self.logger.info("Il bot è stato arrestato", extra={"internal": True, "esito_funzionale": 0})
        self.remove_from_log_server()

    
    def get_updates(self):
        """ Ottiene gli input ricevuti """
        url = f"{self.base_url}/getUpdates"
        if self.update_id:
            url += f"?offset={self.update_id + 1}"
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            updates = result.get("result", [])
            if updates:
                LogContext.generate_log_id()
                self.update_id = updates[0]["update_id"]
                self.logger.info(f"Trovato un nuovo input con offset {self.update_id}", extra={"esito_funzionale": 0, "internal": True})
                self.logWaiting = True
            if len(updates) == 0 and self.logWaiting:
                self.update_id = None
                self.logger.debug(f"Non ci sono ulteriori input da processare, bot in attesa di nuovi input", extra={"esito_funzionale": 0, "internal": True})
                self.logWaiting = False
            return updates
        return []

    
    def process_updates(self, updates):
        """ Esegue la cattura dell'input ricevuto e lo esegue """
        for update in updates:
            self.handle_update(update)

    
    def handle_update(self, update):
        """ Metodo da sovrascrivere dal proprio bot custom per poter eseguire qualsiasi logica """
        raise NotImplementedError("Questo metodo deve essere sovrascritto dalla sottoclasse")
    
    
    def register_to_log_server(self):
        """ Fa la chiamata al web server per visualizzare i log e registrare il bot, fornendo il path assoluto per i log da leggere e visualizzare """
        log_server_url = "http://localhost:7080/register"
        log_dir = self.logger.pathLogs
        data = {
            'bot_username': self.botUsername,
            'log_dir': log_dir
        }
        
        try:
            response = requests.post(log_server_url, data=data)
            response.raise_for_status()  # Solleva un'eccezione per risposte con status code >= 400
            
            if response.status_code == 200:
                self.logger.info(f"Bot registrato nella console log", extra={"internal": True, "esito_funzionale": 0, "details": f"Bot Username: {self.botUsername}\nBot Name: {self.botName}\nBot ID: {self.botId}"})
            elif response.status_code == 208:
                self.logger.info(f"Bot già presente in console log", extra={"internal": True, "esito_funzionale": 0, "details": f"Bot Username: {self.botUsername}\nBot Name: {self.botName}\nBot ID: {self.botId}"})
            else:
                self.logger.warn(f"Errore in fase di registrazione alla console log", extra={"esito_funzionale": f"HTTP {response.status_code}", "internal": True, "details": f"Bot Username: {self.botUsername}\nBot Name: {self.botName}\nBot ID: {self.botId}"})
        
        except requests.exceptions.RequestException as e:
            # Gestione degli errori di connessione e altri errori di richiesta
            tb_str = traceback.format_exc()  # Questo ti fornisce lo stack trace completo
            reason = str(e)
            self.logger.critical(f"Errore di comunicazione con la console log", extra={"esito_funzionale": f"HTTP 500", "internal": True, "details": f"Bot Username: {self.botUsername}\nBot Name: {self.botName}\nBot ID: {self.botId}\nErrore: {reason}"})
    
    
    def remove_from_log_server(self):
        """ Fa la chiamata al web server per rimuovere il bot registrato """
        print("==== STOPPING BOT ====")
        log_server_url = "http://localhost:7080/remove"
        data = {
            'bot_username': self.botUsername
        }
        
        try:
            response = requests.post(log_server_url, data=data)
            response.raise_for_status()  # Solleva un'eccezione per risposte con status code >= 400
            
            if response.status_code == 200:
                self.logger.info(f"Bot sganciato dalla console log con successo", extra={"internal": True, "esito_funzionale": 0, "details": f"Bot Username: {self.botUsername}\nBot Name: {self.botName}\nBot ID: {self.botId}"})
            else:
                self.logger.error(f"Si è verificato un errore sulla console log", extra={"internal": True, "esito_funzionale": f"HTTP {response.status_code}", "details": f"Bot Username: {self.botUsername}\nBot Name: {self.botName}\nBot ID: {self.botId}\nErrore: {response.text}"})
        
        except requests.exceptions.RequestException as e:
            # Gestione degli errori di connessione e altri errori di richiesta
            self.logger.critical(f"Errore imprevisto con la console log", extra={"internal": True, "esito_funzionale": f"HTTP 500", "details": f"Bot Username: {self.botUsername}\nBot Name: {self.botName}\nBot ID: {self.botId}\nErrore: {str(e)}"})