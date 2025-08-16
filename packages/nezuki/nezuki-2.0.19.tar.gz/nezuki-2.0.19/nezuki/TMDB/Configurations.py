from .TMDB import TMDB

class Configurations(TMDB):
    """
        Class to perform a search on TMDB Database and retrieve some general informations
    """
    def countries(self, **kwargs)->dict:
        """
            Get the list of countries (ISO 3166-1 tags) used throughout TMDB

            Args:
                language (string, optional): Defaults to en-US, language of results
        """
        return self._handle_configursations_call("GET", **kwargs)
    
    def details(self, **kwargs)->dict:
        """
            Query the API configuration details
        """
        return self._handle_configursations_call("GET", **kwargs)

    def jobs(self, **kwargs)->dict:
        """
            Get the list of the jobs and departments we use on TMDB
        """
        return self._handle_configursations_call("GET", **kwargs)

    def languages(self, **kwargs)->dict:
        """
            Get the list of languages (ISO 639-1 tags) used throughout TMDB        
        """
        return self._handle_configursations_call("GET", **kwargs)

    def timezones(self, **kwargs)->dict:
        """
            Get the list of timezones used throughout TMDB        
        """
        return self._handle_configursations_call("GET", **kwargs)

    def primary_translations(self, **kwargs)->dict:
        """
            Get a list of the officially supported translations on TMDB
        """
        return self._handle_configursations_call("GET", **kwargs)

    
    def _handle_configursations_call(self,method: str, **kwargs):
        """
            Internal function to make request to API TMDB
        """
        return self._make_request(method, kwargs)