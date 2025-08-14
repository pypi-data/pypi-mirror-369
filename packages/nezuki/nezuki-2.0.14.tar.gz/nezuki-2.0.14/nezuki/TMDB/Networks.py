from .TMDB import TMDB

class Networks(TMDB):
    """
        Class to perform a search on TMDB Database and retrieve some general informations
    """
    def details(self, **kwargs)->dict:
        """
            Get network information

            Args:
                network_id (int32, required): Network ID
        """
        return self._handle_networks_call("GET", **kwargs)
    
    def alternative_names(self, **kwargs)->dict:
        """
            Get the alternative names of a network

            Args:
                network_id (int32, required): Network ID
        """
        return self._handle_networks_call("GET", **kwargs)
    
    def images(self, **kwargs)->dict:
        """
            Get the TV network logos by id

            Args:
                network_id (int32, required): Network ID
        """
        return self._handle_networks_call("GET", **kwargs)
    
    def _handle_networks_call(self,method: str, **kwargs):
        """
            Internal function to make request to API TMDB
        """
        return self._make_request(method, kwargs)