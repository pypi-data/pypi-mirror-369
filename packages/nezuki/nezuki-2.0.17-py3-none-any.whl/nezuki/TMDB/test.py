from nezuki.Logger import configure_nezuki_logger
custom_config = {
    "file": {
        "filename": "/Users/kaitokid/Documents/vs_workspaces/Logs/TMDB.log",
        "maxBytes": 100 * 1024 * 1024,  
        "backupCount": 5,
        "when": "D",
        "interval": 1
    }
}
configure_nezuki_logger(custom_config)
from nezuki.TMDB import *
from nezuki.Database import *

class RetrieveInformations:
    """ Classe che permette di recuperare le informazioni sulle serie tv e film """

    def __init__(self):
        """ Inizializza l'oggetto """
        self.Database = Database("postgres", "postgresql")

    def getListSerie(self)->dict:
        query="select name, anno from tmdb.retrieve_info;"
        self.Database.connection_params("nezuki.net", "kaito", "kaitokid11", 25432)
        result = self.Database.doQueryNamed(query)
        return result

class SerieTV:
    def __init__(self, tmdb_id, database: Database):
        self.tmdb_id = tmdb_id
        self.database = database
        # self.save_configurations()

    def get_serie_info(self, language):
        SerieInfos = TV()
        self.serie_info = SerieInfos.details(series_id=self.tmdb_id, language=language, append_to_response='images,aggregate_credits')
    
    def save_serie_info(self):
        query = """
            INSERT INTO tmdb.tv_series (
                id, adult, backdrop_path, first_air_date, homepage, in_production, last_air_date,
                "name", original_name, poster_path, number_of_episodes, number_of_seasons,
                status, vote_average, vote_count, overview
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                adult = EXCLUDED.adult,
                backdrop_path = EXCLUDED.backdrop_path,
                first_air_date = EXCLUDED.first_air_date,
                homepage = EXCLUDED.homepage,
                in_production = EXCLUDED.in_production,
                last_air_date = EXCLUDED.last_air_date,
                "name" = EXCLUDED.name,
                original_name = EXCLUDED.original_name,
                poster_path = EXCLUDED.poster_path,
                number_of_episodes = EXCLUDED.number_of_episodes,
                number_of_seasons = EXCLUDED.number_of_seasons,
                status = EXCLUDED.status,
                vote_average = EXCLUDED.vote_average,
                vote_count = EXCLUDED.vote_count,
                overview = EXCLUDED.overview;
            """
        params=(self.tmdb_id, self.serie_info.get('adult'), self.serie_info.get('backdrop_path'), self.serie_info.get('first_air_date'), self.serie_info.get('homepage'), self.serie_info.get('in_production'), self.serie_info.get('last_episode_to_air').get('air_date'), self.serie_info.get('name'), self.serie_info.get('original_name'), self.serie_info.get('poster_path'), self.serie_info.get('number_of_episodes'), self.serie_info.get('number_of_seasons'), self.serie_info.get('status'), self.serie_info.get('vote_average'), self.serie_info.get('vote_count'), self.serie_info.get('overview'))
        print(params)
        print(self.database.doQuery(query, params=params))
        self.save_genres()
        self.save_networks()
        self.save_seasons()

    def save_genres(self):
        genres: list = self.serie_info.get('genres')
        for genre in genres:
            genere: str = genre.get('name').lower()
            id: int = genre.get('id')
            query="select id from tmdb.genres where genres.\"id\" = %s"
            params=(id,)
            genere_exist: dict = self.database.doQuery(query=query,params=params)
            if genere_exist.get('rows_affected')==0:
                query="INSERT INTO tmdb.genres (id, \"name\") VALUES(%s, %s)"
                params=(id,genere)
                self.database.doQuery(query=query,params=params)

            query="INSERT INTO tmdb.genres_series (id_serie, id_genere) VALUES(%s, %s) ON CONFLICT (id_serie, id_genere) DO NOTHING;"
            params=(self.tmdb_id,id)
            print(self.database.doQuery(query=query,params=params))

    def save_configurations(self):
        tmdbConfiguration = Configurations()
        tmdbGenres = Genres()
        countries = tmdbConfiguration.countries(language='it-IT')
        languages = tmdbConfiguration.languages()
        jobs = tmdbConfiguration.jobs()
        genres = tmdbGenres.tv(language='it')

        for country in countries:
            isoName = country.get('iso_3166_1')
            englishName = country.get('english_name')
            italianName = country.get('native_name')
            query="INSERT INTO tmdb.countries (iso_3166_1, english_name, italian_name) VALUES(%s, %s, %s) ON CONFLICT (id) DO NOTHING;"
            params=(isoName,englishName,italianName)
            self.database.doQuery(query=query,params=params)

        for language in languages:
            isoName=language.get('iso_639_1')
            englishName=language.get('english_name')
            name=language.get('name')
            query='INSERT INTO tmdb.languages ("name", iso_639_1, english_name) VALUES(%s, %s, %s) ON CONFLICT (id) DO NOTHING;'
            params=(name,isoName,englishName)
            self.database.doQuery(query=query,params=params)

        for genre in genres.get('genres'):
            id = genre.get('id')
            name = genre.get('name')
            query="INSERT INTO tmdb.genres (id, \"name\") VALUES(%s, %s) ON CONFLICT (id) DO NOTHING"
            params=(id,name)
            self.database.doQuery(query=query,params=params)

        for job in jobs:
            dipartimento: str = job.get('department')
            lavori: list = job.get('jobs')
            query="INSERT INTO tmdb.jobs (department, lavoro) VALUES(%s, %s) ON CONFLICT (department, lavoro) DO NOTHING;"
            for lavoro in lavori:
                params=(dipartimento,lavoro)
                self.database.doQuery(query=query,params=params)
                

    def save_networks(self):
        networks: list = self.serie_info.get('networks')
        tmdbNetwork = Networks()
        for network in networks:
            id=network.get('id')
            query='select id from tmdb.networks where networks."id" = %s'
            params=(id,)
            networkOnDb: dict = self.database.doQuery(query=query,params=params)
            if len(networkOnDb.get('results')) == 0:
                getNwtworkInfo: dict = tmdbNetwork.details(network_id=id)
                hq=getNwtworkInfo.get('headquarters')
                homepage=getNwtworkInfo.get('homepage')
                logo_path=getNwtworkInfo.get('logo_path')
                name=getNwtworkInfo.get('name')
                origin_country=getNwtworkInfo.get('origin_country')
                query='INSERT INTO tmdb.networks (id, headquarters, homepage, logo_path, "name", origin_country) VALUES(%s, %s, %s, %s, %s, %s);'
                params=(id,hq,homepage,logo_path,name,origin_country)
                self.database.doQuery(query=query,params=params)
            query='INSERT INTO tmdb.network_series (id_serie, id_emittente) VALUES(%s, %s) ON CONFLICT (id_serie, id_emittente) DO NOTHING;'
            params=(self.tmdb_id,id)
            self.database.doQuery(query=query,params=params)

    def save_seasons(self):
        seasons: list = self.serie_info.get('seasons') # viene usato serie_info perché ha tutte le stagioni con le info complete, Usando l'API TMDB delle stagioni è richiesto il numero per ottenere le stesse info
        for season in seasons:
            name=season.get('name')
            air_date=season.get('air_date')
            episode_numer=season.get('episode_count')
            id=season.get('id')
            overview=season.get('overview')
            poster_path=season.get('poster_path')
            season_number=season.get('season_number')
            vote_average=season.get('vote_average')
            query="INSERT INTO tmdb.seasons_series (id_serie, air_date, episode_count, id, \"name\", overview, poster_path, season_number, vote_average) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id_serie, season_number) DO NOTHING;"
            params=(self.tmdb_id,air_date,episode_numer,id,name,overview,poster_path,season_number,vote_average)
            self.database.doQuery(query=query,params=params)
            self.save_episodes(seasonNumber=season_number)

    def save_episodes(self, seasonNumber: int):
        tmdbEpisodes = TVSeasons() # come save_seasons si usa l'api di seasons TMDB perché ha tutti gli episodi e le rispettive info, così evitiamo lo spam di chiamate inutile a TMDB
        seasons: dict = tmdbEpisodes.details(series_id=self.tmdb_id,season_number=seasonNumber,language='it-IT')
        episodes: list = seasons.get('episodes')
        for episode in episodes:
            air_date=episode.get('air_date')
            episode_number=episode.get('episode_number')
            id=episode.get('id')
            name=episode.get('name')
            overview=episode.get('overview')
            production_code=episode.get('production_code')
            runtime=episode.get('runtime')
            season_number=episode.get('season_number')
            show_id=episode.get('show_id')
            still_path=episode.get('still_path')
            vote_average=episode.get('vote_average')
            vote_count=episode.get('vote_count')
            query='INSERT INTO tmdb.episodes (id, air_date, "name", overview, serie, still_path, season, episode_number, production_code, runtime, vote_average, vote_count) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (serie, season, episode_number) DO NOTHING;'
            params=(id,air_date,name,overview,show_id,still_path,season_number,episode_number,production_code,runtime,vote_average,vote_count)
            print(self.database.doQuery(query=query,params=params))
    

tt = RetrieveInformations()
list_names: list = tt.getListSerie().get("results")

searchTv = Search()

for list_name in list_names:
    name = list_name.get('name')
    anno = list_name.get('anno')
    lista_tmdb_results: dict = searchTv.tv(query=name, include_adult=True, language='it-IT', year=anno)
    if lista_tmdb_results.get('total_results'):
        for tmdb_result in lista_tmdb_results.get('results'):
            serie = SerieTV(tmdb_result.get('id'), tt.Database)
            serie.get_serie_info('it-IT')

            serie.save_serie_info()

# test_search = Search()

# result_search = test_search.tv(query="Mr Robot", language='it-IT')
# print("Risultati find TV: \n", result_search)

# test_tv = TV()

# result_tv = test_tv.details(series_id=62560, language='it-IT')
# print("Risultati Detail TV: \n", result_tv)

# test_tv = TVSeasons()

# result_tvseasons = test_tv.details(series_id=62560, season_number=1, language='it-IT')
# print("Risultati Detail TV: \n", result_tvseasons)

# test_tvepisodes = TVEpisodes()

# result_tvepisodes = test_tvepisodes.details(series_id=62560, season_number=1, episode_number=1, language='it-IT')
# print("Risultati Detail TV: \n", result_tvepisodes)