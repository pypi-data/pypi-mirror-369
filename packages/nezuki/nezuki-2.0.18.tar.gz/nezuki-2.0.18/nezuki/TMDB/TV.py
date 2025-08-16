from .TMDB import TMDB

class TV(TMDB):
    """
        Class to get informations about a specific serie
    """
    def details(self, **kwargs) -> dict:
        """
            Get the details of a TV show

            Args:
                series_id (int32, required): TMDB ID Show
                append_to_response (string, optional): comma separated list of endpoints (or functions) within this namespace (or class), 20 items max
                language (string, optional): Defaults to en-US language of results
        """
        return self._handle_tv_call("GET", **kwargs)
    
    def account_states(self, **kwargs):
        """
            Get the rating, watchlist and favourite status

            Args:
                series_id (int32, required): TMDB ID Show
                session_id (string, optional): See Autentication, basically used to perform action with user signed and autorization and has privileged access
                guest_session_id (string, optional): See Autentication, basically used to perform action with guest signed and autorization and has limited access
        
        """
        return self._handle_tv_call("GET", **kwargs)
    
    def aggregate_credits(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)
    
    def alternative_titles(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)
    
    def changes(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def content_ratings(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)
    
    def credits(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)
    
    def episode_groups(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)
    
    def external_ids(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)
    
    def images(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def keywords(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def latest(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def lists(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def recommendations(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def reviews(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def screened_theatrically(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def similar(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def translations(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def videos(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def watchProviders(self, **kwargs):
        return self._handle_tv_call("GET", **kwargs)

    def addRating(self, **kwargs):
        return self._handle_tv_call("POST", **kwargs)

    def deleteRating(self, **kwargs):
        return self._handle_tv_call("DELETE", **kwargs)

    def _handle_tv_call(self, method: str, **kwargs):
        """
            Internal function to make request to API TMDB
        """
        return self._make_request(method, kwargs)