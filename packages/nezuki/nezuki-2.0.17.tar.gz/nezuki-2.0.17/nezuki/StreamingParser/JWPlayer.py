import time
from nezuki.Logger import *
logger = get_nezuki_logger()
from nezuki.Browser import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class JWPlayer:
    def __init__(self, browser: Browser):
        """ Inizializza l'oggetto JWPlayer e crea "player" per controllarlo ed ottenere altre informazioni
        
        Args:
            browser (Browser, required): Istanza del browser avviato (del modulo Nezuki)
        
        """
        self.browser = browser
        self.player = self.__init_player()
        self.__queueDownload: list = []

    def __init_player(self):
        """
        Funzione interna per inizializzare il player e poterlo controllare dopo
        """
        time.sleep(3)
        script = "return jwplayer();"
        self.consolePlayer = self.__execute_js_player(script)
        return self.consolePlayer

    def play(self):
        """Effettua il play nel player"""
        script = "return jwplayer().play();"
        to_ret = False
        if self.__execute_js_player(script):
            to_ret = True
        return to_ret

    def mute(self):
        """Mette il muto nel player"""
        script = "return jwplayer().setMute(true);"
        to_ret = False
        if self.__execute_js_player(script):
            to_ret = True
        return to_ret
    
    def unmute(self):
        """Mette il muto nel player"""
        script = "return jwplayer().setMute(false);"
        to_ret = False
        if self.__execute_js_player(script):
            to_ret = True
        return to_ret
    
    def pause(self):
        """Mette in pausa la riproduzione nel player"""
        script = "return jwplayer().pause();"
        to_ret = False
        if self.__execute_js_player(script):
            to_ret = True
        return to_ret

    def stop(self):
        """Ferma la riproduzione nel player"""
        script = "return jwplayer().stop();"
        to_ret = False
        if self.__execute_js_player(script):
            to_ret = True
        return to_ret

    def getItemPlayer(self)->dict|None:
        """Ottiene il file attualmente in riproduzione nel player
        
        Returns:
            dict: Se il player ha effettivamente un file ritorna il dizionario con la chiave type che indica il tipo di file e url che è l'url del file in riproduzione

        Examples:
            >>> getItemPlayer()
            {"type": "m3u8", "url": "https://exampkle.org/playlist.m3u8"}

            In caso di errore o file non riconosciuto:
            >>> getItemPlayer()
            None

        """
        script = "return jwplayer().getPlaylistItem().file;"
        url = self.__execute_js_player(script)
        if url:
            if ".m3u8" in url:
                to_ret: dict = {"type": "m3u8", "url": url}
            elif ".mp4" in url:
                to_ret: dict = {"type": "mp4", "url": url}
            else:
                to_ret = None
        else:
            to_ret = None
            logger.warning(f"Non posso capire il tipo di file perché non è valido il player", extra={"internal": True})
        return to_ret

    def __execute_js_player(self, script: str):
        """Funzione interna che serve per eseguire uno specifico script per il player
        
        Args:
            script (string, required): Lo script che si intende eseguire
        """
        logger.debug(f"Eseguo lo script {script}", extra={"internal": True})
        try:
            # Attendi fino a quando il player è pronto
            to_ret = self.browser.driver.execute_script(script)
        except Exception as e:
            to_ret = None
            logger.error(f"Errore durante l'esecuzione del JS: {e}", extra={"internal": True})
        logger.debug(f"Lo script ha tornato: {to_ret}", extra={"internal": True})
        return to_ret