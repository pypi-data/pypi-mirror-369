__version__ = "1.0.0"

API_VERSION: str = '3'
REQUESTS_TIMEOUT = 30
API_KEY = 'a8e14442c89c22c2788f7d1d96198a5d'
API_PATHS = {
    'configurations': {
        'details': '/configuration',
        'countries': '/configuration/countries',
        'jobs': '/configuration/jobs',
        'languages': '/configuration/languages',
        'primary_translations': '/configuration/primary_translations',
        'timezones': '/configuration/timezones',
    },
    'genres': {
        'tv': '/genre/tv/list',
        'movie': '/genre/movie/list',
    },
    'networks': {
        'details': '/network/{network_id}',
        'alternative_names': '/network/{network_id}/alternative_names',
        'images': '/network/{network_id}/images',
    },
    'search': {
        'collection': '/search/collection',
        'company': '/search/company',
        'keyword': '/search/keyword',
        'movie': '/search/movie',
        'multi': '/search/multi',
        'person': '/search/person',
        'tv': '/search/tv'
    },
    'tv': {
        'details': '/tv/{series_id}',
        'account_states': '/tv/{series_id}/account_states',
        'aggregate_credits': '/tv/{series_id}/aggregate_credits',
        'alternative_titles': '/tv/{series_id}/alternative_titles',
        'changes': '/tv/{series_id}/changes',
        'content_ratings': '/tv/{series_id}/content_ratings',
        'credits': '/tv/{series_id}/credits',
        'episode_groups': '/tv/{series_id}/episode_groups',
        'external_ids': '/tv/{series_id}/external_ids',
        'images': '/tv/{series_id}/images',
        'keywords': '/tv/{series_id}/keywords',
        'latest': '/tv/{series_id}/latest',
        'lists': '/tv/{series_id}/lists',
        'recommendations': '/tv/{series_id}/recommendations',
        'reviews': '/tv/{series_id}/reviews',
        'screened_theatrically': '/tv/{series_id}/screened_theatrically',
        'similar': '/tv/{series_id}/similar',
        'translations': '/tv/{series_id}/translations',
        'videos': '/tv/{series_id}/videos',
        'watchProviders': '/tv/{series_id}/watch/providers',
        'addRating': '/tv/{series_id}/rating',
        'deleteRating': '/tv/{series_id}/rating',
    },
    'tvseasons': {
        'details': '/tv/{series_id}/season/{season_number}',
        'account_states': '/tv/{series_id}/season/{season_number}/account_states',
        'aggregate_credits': '/tv/{series_id}/season/{season_number}/aggregate_credits',
        'changes': '/tv/{series_id}/season/{season_number}/changes',
        'credits': '/tv/{series_id}/season/{season_number}/credits',
        'external_ids': '/tv/{series_id}/season/{season_number}/external_ids',
        'images': '/tv/{series_id}/season/{season_number}/images',
        'translations': '/tv/{series_id}/season/{season_number}/translations',
        'videos': '/tv/{series_id}/season/{season_number}/videos',
        'watchProviders': '/tv/{series_id}/season/{season_number}/watch/providers',
    },
    'tvepisodes': {
        'details': '/tv/{series_id}/season/{season_number}/episode/{episode_number}',
        'account_states': '/tv/{series_id}/season/{season_number}/episode/{episode_number}/account_states',
        'changes': '/tv/{series_id}/season/{season_number}/episode/{episode_number}/changes',
        'credits': '/tv/{series_id}/season/{season_number}/episode/{episode_number}/credits',
        'external_ids': '/tv/{series_id}/season/{season_number}/episode/{episode_number}/external_ids',
        'images': '/tv/{series_id}/season/{season_number}/episode/{episode_number}/images',
        'translations': '/tv/{series_id}/season/{season_number}/episode/{episode_number}/translations',
        'videos': '/tv/{series_id}/season/{season_number}/episode/{episode_number}/videos',
        'addRating': '/tv/{series_id}/rating',
        'deleteRating': '/tv/{series_id}/rating',
    }
}

from .TMDB import TMDB
from .Search import Search
from .TV import TV
from .TVSeasons import TVSeasons
from .TVEpisodes import TVEpisodes
from .Configurations import Configurations
from .Genres import Genres
from .Networks import Networks

__all__ = ['TMDB', 'Search', 'TV', 'TVSeasons', 'TVEpisodes', 'Configurations', 'Genres', 'Networks']
