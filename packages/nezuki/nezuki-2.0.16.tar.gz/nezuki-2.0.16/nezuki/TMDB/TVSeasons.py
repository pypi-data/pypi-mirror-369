from .TMDB import TMDB

class TVSeasons(TMDB):
    """
        Classe per interagire con le informazioni relative alle stagioni di una serie TV tramite le API di TMDb.
    """
    def details(self, **kwargs) -> dict:
        return self._handle_tvseasons_call("GET", **kwargs)

    def account_states(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)
    
    def aggregate_credits(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)
    
    def changes(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)
    
    def credits(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)
    
    def external_ids(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)

    def translations(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)

    def videos(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)

    def watchProviders(self, **kwargs):
        return self._handle_tvseasons_call("GET", **kwargs)

    def _handle_tvseasons_call(self,method: str, **kwargs):
        return self._make_request(method, kwargs)