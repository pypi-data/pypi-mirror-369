from nezuki.Logger import *
logger = get_nezuki_logger()
from nezuki.Browser import Browser
from JWPlayer import JWPlayer
from selenium.webdriver.common.by import By
import re

class AnimeSaturn:
    def __init__(self, browser: Browser):
        """
        Inizializza l'oggetto Anime Saturn insieme al player
        
        Args:
            browser (Browser, required): Istanza del browser avviato (del modulo Nezuki)
        """
        self.browser = browser
        self.player = JWPlayer(self.browser)

    def get_title(self)->dict:
        """
            Estrae il titolo dell'anime e il numero dell'episodio dalla pagina di Anime Saturn.

            Returns:
                dict: Dizionario con le chiavi "titolo" e "episodio".

            Examples:
                >>> get_title()
                {'titolo': 'One Piece', 'episodio': '1050'}

                In caso di errore:
                >>> get_title()
                {'titolo': 'TOCHECKFILE_AnimeNameMissing', 'episodio': 'Episodio X'}
        """
        data_return: dict = {"titolo": 'TOCHECKFILE_AnimeNameMissing', "episodio": "Episodio X"}
        try:
            rowTitle = self.browser.find_element(By.XPATH, '//h4')
            pattern = r'(.+) Episodio (\d+)'
            string_parsed = re.match(pattern, rowTitle.text.strip())
            data_return = {"titolo": string_parsed.group(1), "episodio": string_parsed.group(2)}
            return data_return
        except Exception as e:
            return data_return
        
    