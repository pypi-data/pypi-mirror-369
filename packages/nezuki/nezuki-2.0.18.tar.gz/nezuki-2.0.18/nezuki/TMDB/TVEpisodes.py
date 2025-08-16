from .TMDB import TMDB

class TVEpisodes(TMDB):
    """
        Classe per interagire con le informazioni relative agli episodi di una stagione tramite le API di TMDb.
    """
    def details(self, **kwargs) -> dict:
        return self._handle_tvepisodes_call("GET", **kwargs)

    def account_states(self, **kwargs):
        return self._handle_tvepisodes_call("GET", **kwargs)
    
    def aggregate_credits(self, **kwargs):
        return self._handle_tvepisodes_call("GET", **kwargs)
    
    def changes(self, **kwargs):
        return self._handle_tvepisodes_call("GET", **kwargs)
    
    def credits(self, **kwargs):
        return self._handle_tvepisodes_call("GET", **kwargs)
    
    def external_ids(self, **kwargs):
        return self._handle_tvepisodes_call("GET", **kwargs)

    def translations(self, **kwargs):
        return self._handle_tvepisodes_call("GET", **kwargs)

    def videos(self, **kwargs):
        return self._handle_tvepisodes_call("GET", **kwargs)

    def addRating(self, **kwargs):
        return self._handle_tvepisodes_call("POST", **kwargs)

    def deleteRating(self, **kwargs):
        return self._handle_tvepisodes_call("DELETE", **kwargs)

    def _handle_tvepisodes_call(self,method: str, **kwargs):
        return self._make_request(method, kwargs)