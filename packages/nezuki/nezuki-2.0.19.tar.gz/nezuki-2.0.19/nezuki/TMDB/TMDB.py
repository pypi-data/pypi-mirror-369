from nezuki.Logger import get_nezuki_logger
import inspect
from nezuki.Http import Http
from nezuki.TMDB import API_KEY, REQUESTS_TIMEOUT, API_VERSION, API_PATHS

logger = get_nezuki_logger()

class TMDB:
    def __init__(self):
        """ Initialize the object """
        self.baseUri = 'api.themoviedb.org'
        self.apiKey = API_KEY
        self.apiCall = Http("https", self.baseUri, 443, f"/{API_VERSION}")
        self.timeout = REQUESTS_TIMEOUT
        self.paths = API_PATHS
        self.headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Connection': 'close'}
        
    def _build_basepath(self, className: str, functionName: str, para) -> str:
        """
            Internal function that use Caller Class and Caller Method to retrieve the correct `API_PATHS` and populate, if present, uri parameters.
            
            Args:
                section: sezione delle API (es. 'tv', 'movie', 'search', ...)
                endpoint: nome logico dell'endpoint (es. 'details', 'tv', ...)
                params: dizionario con i parametri (series_id, season_number, etc.)
        """
        basepath_template = self.paths[className.lower()][functionName]
        print(para)
        try:
            basepath = basepath_template.format(**para)
        except KeyError as e:
            raise ValueError(f"Parametro mancante per costruire il basepath: {e}")
        return basepath
        
    def _make_request(self, method, body):
        """ 
            Internal function to perform HTTP Request using Nezuki Module HTTP.

            `basePath` is build using the Caller name with Caller function, this two infos are used to retrieve the `API_PATHS` a JSON structure with same strucutre ClassName.MethodName
        """
        body['api_key'] = self.apiKey
        basePath = self._build_basepath(self.__class__.__name__.lower(), inspect.stack()[2].function, body)
        response = self.apiCall.api_request(method, basePath, body, self.headers).json()
        return response