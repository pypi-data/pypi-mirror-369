import threading
import typing
from TelegramParser import TelegramParser
from Bot import Bot
from Common import *
from commonLogId import *
from Http import Http

current_version = "1.0.0"

class MissinRequiredField(Exception):
    """Eccezione sollevata quando manca un campo required """
    
    def __init__(self, message:str=""):
        """ Genera aggiunge il messaggio di errore """
        self.message = message
        super().__init__(self.message)

@versione("1.0.0")
class TelegramApi(Bot):
    def __init__(self, token, isLocalMode: bool = False, pathLocalLogs: str = ""):
        super().__init__(token, isLocalMode, pathLocalLogs)
        self.logger = get_logger()
        self.http = Http()

    # def getMe(self):
    #     method = "getMe"
    #     payload={}
    #     response = self.http.doRequest(self.urlComponents['host'] + method, self.urlComponents['path'], self.urlComponents['method'].lower(), payload, self.urlComponents['port'], self.urlComponents['protocol'])
    #     return response

    
    def _api_call(self, methodName: str, payload: dict={}, asynch: bool = True):
        url = f"{self.base_url}/{methodName}"
        endpoint = f"{self.path_start}/{methodName}"
        if asynch:
            self.logger.info(f"Chiamata asincrona per il metodo {methodName}.", extra={"details": f"URL: {url}\nPayload: {payload}", "internal": True})
            threading.Thread(target=self.http.doRequest, args=(self.host, endpoint, "post", payload, self.port, self.protocol)).start()
        else:
            self.logger.info(f"Chiamata api sincrona per il metodo {methodName}.", extra={"details": f"URL: {url}\nPayload: {payload}", "internal": True})
            # response = requests.post(url=url, data=payload
            response = self.http.doRequest(self.host, endpoint, "post", payload, self.port, self.protocol).json()
            if not response['ok']:
                self.logger.error(f"Errore nell'esecuzione sincrona del metodo {methodName}", extra={"esito_funzionale": 1, "details": f"{response}", "internal": False})
            else:
                self.logger.info(f"Risposta sincrona API metodo {methodName}", extra={"esito_funzionale": 0, "details": f"{response}", "internal": False})

    
    def sendMessage(self, asynch: bool= True, **kwargs):
        methodName = "sendMessage"
        payload = {**kwargs}
        if "chat_id" not in kwargs:
            self.logger.error("Obbligatorietà non rispettata.", extra={"esito_funzionale": 1, "details": "'chat_id' è obbligatorio"})
            raise MissinRequiredField("chat_id è obbligatorio")
        
        if "text" not in kwargs:
            self.logger.error("Obbligatorietà non rispettata.", extra={"esito_funzionale": 1, "details": "'text' è obbligatorio"})
            raise MissinRequiredField("text è obbligatorio")
        

        self.logger.info(f"Invio automatico dell'action typing", extra={"internal": True})
        threading.Thread(target=self.sendChatAction, args=(kwargs['chat_id'], "typing")).start()
        if asynch:
            self.logger.info(f"Esecuzione asincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            threading.Thread(target=self._api_call, args=(methodName, payload, asynch)).start()
        else:
            self.logger.info(f"Esecuzione sincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            self._api_call(methodName, payload, asynch)
            
    
    def logOut(self, asynch: bool= True):
        methodName = "logOut"
        payload = {}
        if asynch:
            self.logger.info(f"Esecuzione asincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            threading.Thread(target=self._api_call, args=(methodName, payload, asynch)).start()
        else:
            self.logger.info(f"Esecuzione sincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            self._api_call(methodName, payload, asynch)

    
    def logOut(self, asynch: bool= True):
        methodName = "logOut"
        payload = {}
        if asynch:
            self.logger.info(f"Esecuzione asincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            threading.Thread(target=self._api_call, args=(methodName, payload, asynch)).start()
        else:
            self.logger.info(f"Esecuzione sincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            self._api_call(methodName, payload, asynch)

    
    def close(self, asynch: bool= True):
        methodName = "close"
        payload = {}
        if asynch:
            self.logger.info(f"Esecuzione asincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            threading.Thread(target=self._api_call, args=(methodName, payload, asynch)).start()
        else:
            self.logger.info(f"Esecuzione sincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
            self._api_call(methodName, payload, asynch)
   
    
    def sendChatAction(self, chat_id: int, action: typing.Literal['typing', 'upload_photo', 'record_video', 'upload_video', 'record_voice', 'upload_voice', 'upload_document', 'choose_sticker', 'find_location', 'record_video_note', 'upload_video_note'] = "typing", asynch: bool= True):
        methodName = "sendChatAction"
        payload = {"chat_id": chat_id, "action": action}
        self.logger.info(f"Esecuzione asincrona del metodo {methodName}", extra={"details": f"Payload: {payload}"})
        self._api_call(methodName, payload, asynch)
   
    
    def handle_update(self, update):
        parser = TelegramParser(update)
        self.logger.info(f"Ricveuto un input di tipo: {parser.inputType}", extra={"internal": True})
        self.handleMessage(parser)
    
    
    def handleMessage(self, message):
        self.logger.error(f"Questo metodo deve essere implementato dalla classe figlia.")
        raise NotImplementedError("Questo metodo deve essere sovrascritto dalla classe del Bot.")



# test = TelegramApi("123")
# test.getMe()