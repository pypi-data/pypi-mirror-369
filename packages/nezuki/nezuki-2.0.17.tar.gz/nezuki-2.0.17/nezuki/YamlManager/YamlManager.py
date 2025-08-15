from JsonManager import JsonManager
import yaml

class YamlManager:
    '''
        Questa classe serve per gestire un yaml file.
    '''
    def __init__(self, yaml_file:str) -> None:
        self.data = self.read_yaml(yaml_file)
        self.dataManager = JsonManager(self.data)
        
    def read_yaml(self, path: str) -> dict:
        """
            Legge il file da path assoluto e torna il contenuto del file in un JSON decodificato.

            Args:
                path: Path asosluto del file YAML da leggere

            Returns:
                dict: Torna il contenuto YAML nel formato JSON
        """
        try:
            with open(path, "r") as f:
                content_json = yaml.safe_load(f.read())
        except Exception as e:
            content_json = None
        return content_json
    
    
# x = YamlManager("/Users/andreacolangelo/Lavoro/github/pokedex/Python/pokedxTestBot/config/dev.yaml")
# j = JsonManager(x.data)
# print(j.retrieveKey("admins"))