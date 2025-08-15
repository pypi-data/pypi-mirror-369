from .TMDB import TMDB

class Search(TMDB):
    """
        Class to perform a search on TMDB Database and retrieve some general informations
    """
    def collection(self, **kwargs)->dict:
        """
            Search for collections by their original, translated and alternative names.

            Args:
                query (string, required): Text to search
                include_adult (bool, optional): Defaults to False Choose whether to inlcude adult (pornography) content in the results.
                language (string, optional): Defaults to en-US, language of results
                page (int32, optional): Defaults to 1, show page number
                region (string, optional), Specify a ISO 3166-1 code to filter release dates. Must be uppercase.
        """
        return self._handle_search_call("GET", **kwargs)
    
    def company(self, **kwargs)->dict:
        """
            Search for companies by their original and alternative names
            
            Args:
                query (string, required): Text to search
                page (int32, optional): Defaults to 1, show page number

        """
        return self._handle_search_call("GET", **kwargs)

    def keyword(self, **kwargs)->dict:
        """
            Search for keywords by their name

            Args:
                query (string, required): Text to search
                page (int32, optional): Defaults to 1, show page number
        """
        return self._handle_search_call("GET", **kwargs)

    def movie(self, **kwargs)->dict:
        """
            Search for movies by their original, translated and alternative titles

            Args:
                query (string, required): Text to search
                include_adult (bool, optional): Defaults to False Choose whether to inlcude adult (pornography) content in the results.
                language (string, optional): Defaults to en-US, language of results
                primary_release_year (string, optional): A filter to limit the results to a specific primary release year.
                page (int32, optional): Defaults to 1, show page number
                region (string, optional), Specify a ISO 3166-1 code to filter release dates. Must be uppercase.
                year (string, optional): A filter to limit the results to a specific year (looking at all release dates).
        
        """
        return self._handle_search_call("GET", **kwargs)

    def multi(self, **kwargs)->dict:
        """
            Use multi search when you want to search for movies, TV shows and people in a single request

            Args:
                query (string, required): Text to search
                include_adult (bool, optional): Defaults to False Choose whether to inlcude adult (pornography) content in the results.
                language (string, optional): Defaults to en-US, language of results
                page (int32, optional): Defaults to 1, show page number
        
        """
        return self._handle_search_call("GET", **kwargs)

    def person(self, **kwargs)->dict:
        """
            Search for people by their name and also known as names

            Args:
                query (string, required): Text to search
                include_adult (bool, optional): Defaults to False Choose whether to inlcude adult (pornography) content in the results.
                language (string, optional): Defaults to en-US, language of results
                page (int32, optional): Defaults to 1, show page number

        """
        return self._handle_search_call("GET", **kwargs)

    def tv(self, **kwargs) -> dict:
        """
            Search for TV shows by their original, translated and also known as names

            Args:
                query (string, required): Text to search
                first_air_date_year (int32, optional): Search only the first air date. Valid values are: 1000..9999
                include_adult (bool, optional): Defaults to False Choose whether to inlcude adult (pornography) content in the results.
                language (string, optional): Defaults to en-US, language of results
                page (int32, optional): Defaults to 1, show page number
                year (string, optional): A filter to limit the results to a specific year (looking at all release dates).
        """
        return self._handle_search_call("GET", **kwargs)
    
    def _handle_search_call(self,method: str, **kwargs):
        """
            Internal function to make request to API TMDB
        """
        return self._make_request(method, kwargs)