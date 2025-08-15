import typing
import requests
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

class MethodNotSupported(Exception):
    """Errore sollevato quando viene usato un metodo non implementato."""
    pass

class InsufficientInfo(Exception):
    """Errore sollevato quando le informazioni per formare la request sono insufficienti."""
    pass

class Http:
    """Classe che permette di effettuare chiamate HTTP."""
    def __init__(self, protocol: typing.Literal['http', 'https'] = "https", host: str = "", port: int = 0, basePath: str = "", timeout: int = 30):
        """
        Inizializza l'oggetto Http che può essere generico oppure specifico specificando i parametri per definire l'API (per semplificare il riuso)

        Args:
            protocol (http|https, optional): http o https, il protocollo da usare, default https, ignorato se non si usa api_request
            host (str, optional): definisce host ad esempio google.com
            port (int, optional): definisce la porta a cui inviare la richiesta
            basePath (str, optional): definisce una eventuale parte fissa del servizio da richiamare
            timeout (int, optional): Timeout in secondi per le richieste HTTP. Default è 30.
        """
        self.timeout = timeout
        self.protocol = protocol
        self.host = host
        self.port = port
        self.basePath = basePath
        if self.basePath is None:
            self.basePath = ""

        if self.basePath.endswith("/"):
            self.basePath = self.basePath[:-1]

        self.method_mapper = {
            "get": requests.get,
            "post": requests.post
        }

    def _build_url(self, protocol: str, host: str, port: int, path: str) -> str:
        """ Funzione privata che costruisce l'url finale
        
        Args:
            protocol (str): Protocollo da usare
            host (str): Nome dell'host da chiamare come google.com
            port (int): Numero della porta da usare, se 0 viene impostta 80 o 443 in base al protocollo
            path (str): Path del servizio da richiamare, deve iniziare per / e se non presente verrà inserito automaticamente"""
        # Se il path è vuoto, default a "/"
        if not path.startswith("/"):
            path = "/" + path
        # Se port è 0, usa i default in base al protocollo
        if port == 0:
            port = 80 if protocol == "http" else 443
        return f"{protocol}://{host}:{port}{path}"

    def _perform_request(self, method: str, url: str, payload: dict, headers: dict = None) -> requests.Response:
        """ Funzione privata che effettua la chiamata HTTP 
        
        
        Args:
            method (str): Il metodo HTTP ("get" o "post"). Default è "get".
            url (str): URL da richiamare già compilato con porta e path
            payload (dict): I dati da inviare con la richiesta. Default è {}.
            headers (dict, optional): Eventuali header da includere nella richiesta.
            

        Raises:
            MethodNotSupported: Se il metodo HTTP non è supportato.
            InsufficientInfo: Se almeno uno di questi elementi non è stato passato: protocol, host, port
            Exception: Rilancia eventuali eccezioni sollevate durante la richiesta."""
        method_lower = method.lower()
        if payload is None:
            payload = {}
        if method_lower not in self.method_mapper:
            logger.error("Metodo non supportato", extra={"internal": True})
            raise MethodNotSupported(f"Il metodo {method} non è supportato. Scegli tra {list(self.method_mapper.keys())}.")
        try:
            logger.info(f"Chiamata HTTP\nPayload{payload}\nHeaders: {headers}\nTimeout: {self.timeout}\nURL: {url}", extra={"internal": True})
            if method_lower == "get":
                response = self.method_mapper[method_lower](url, params=payload, headers=headers, timeout=self.timeout)
            elif method_lower == "post":
                response = self.method_mapper[method_lower](url, json=payload, headers=headers, timeout=self.timeout)
            logger.info(f"Risposta HTTP\nPayload{response}", extra={"internal": True})
            return response
        except Exception as e:
            logger.error(f"Errore durante la chiamata HTTP: {e}", extra={"internal": True})
            raise

    def api_request(self, method: typing.Literal['GET', 'POST'], path: str, payload: dict, headers: dict = None) -> requests.Response:
        """
        Esegue una richiesta HTTP specifica di una API o se si fanno diverse chiamate ad uno stesso servizio.
        
        Usare questa funzione solo se sono stati dichiarati in precedenza protocol, host, port.


        Args:
            method (GET|POST): Obbligatorio, indicare il metodo della chiamata HTTP
            path (str): Obbligatorio, indicare il path del servizio da richiamare, deve iniziare per / se assente verrà inserito automaticamente in base al basePath fornito
            payload (dict): Obbligatorio, indicare il body della chiamata nel formato dizionario Python (JSON) e se non previsto passare dizionario vuoto, passaggio automatico da payload a query parameters
            headers (dict, optional): Facoltativo, indicare eventuali headers che si intende passare nella chiamata


        Raises:
            MethodNotSupported: Se il metodo HTTP non è supportato.
            InsufficientInfo: Se almeno uno di questi elementi non è stato passato: protocol, host, port
            Exception: Rilancia eventuali eccezioni sollevate durante la richiesta.
        """
        logger.debug("Applicazione regole chiamata ad API", extra={"internal": True})
        if not self.protocol or not self.host or self.port == 0:
            raise InsufficientInfo("Verificare che protocol, host e port siano impostati correttamente.")

        if path.startswith("/"):
            path = f"{self.basePath}{path}"
        else:
            path = f"{self.basePath}/{path}"
        url = self._build_url(self.protocol, self.host, self.port, path)
        logger.debug(f"URL: {url}", extra={"internal": True})
        return self._perform_request(method, url, payload, headers)

    def do_request(self, method: typing.Literal['GET', 'POST'], protocol: typing.Literal['http', 'https'], host: str, port: int, path: str, payload: dict = None, headers: dict = None) -> requests.Response:
        """
        Permette di effettuare una chiamata HTTP generica, usando i parametri passati ignorando eventuali parametri creati con l'istanza

        Args:
            method (str, optional): Il metodo HTTP ("get" o "post"). Default è "get".
            protocol (str, optional): Il protocollo ("http" o "https"). Default è "http".
            host (str): L'indirizzo del server.
            port (int, optional): La porta del server; se 0, viene omessa.
            path (str): Il path del servizio da richiamare
            payload (dict, optional): I dati da inviare con la richiesta. Default è {}.
            headers (dict, optional): Eventuali header da includere nella richiesta.

        Returns:
            requests.Response: La risposta ottenuta dalla chiamata HTTP.
        
        Raises:
            MethodNotSupported: Se il metodo HTTP non è supportato.
            Exception: Rilancia eventuali eccezioni sollevate durante la richiesta.
        """
        log_info = {"host": host, "port": port, "method": method, "protocol": protocol, "timeout": self.timeout, "payload": payload, "headers": headers}
        logger.debug(f"Effettuo chiamata HTTP con parametri specifici: {log_info}", extra={"internal": True})
        url = self._build_url(protocol, host, port, path)
        return self._perform_request(method, url, payload, headers)

    def __del__(self) -> None:
        pass  # Aggiungi qui eventuali operazioni di cleanup se necessario.