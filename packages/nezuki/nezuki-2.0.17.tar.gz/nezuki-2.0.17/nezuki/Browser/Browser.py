import os
import time
import argparse
import typing
import urllib.request
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from nezuki.Logger import *
from nezuki.StreamingParser import JWPlayer
import aiohttp
import asyncio

logger = get_nezuki_logger()

class Browser:
    """ Classe che permette di avviare e controllare un browser """
    def __init__(self, browserName: typing.Literal['firefox', 'chrome'], headless: bool = True):
        """
            Classe che istanzia l'oggetto Browser

            Args:
                browserName (string, required): Nome del browser che si intende avviare
                headless (bool, optional): Esegui in modalità senza GUI (default True)
        """
        self.browserName = browserName
        self.headless = headless
        self.driver = None
        self.__m3u8_queue: list = []
        self.__mp4_queue: list = []

        logger.debug(f"Browser scelto è {browserName.capitalize()}", extra={"internal": True})

        self.options = self.setup_options()

    def setup_browser(self):
        """ Configura il browser e inizializza il driver """
        if self.browserName == "firefox":
            from selenium.webdriver.firefox.options import Options
            from selenium.webdriver.firefox.service import Service
            from webdriver_manager.firefox import GeckoDriverManager
            self.options = Options()
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
        elif self.browserName == "chrome":
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            options = Options()
            options.headless = self.headless
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            raise ValueError(f"Browser '{self.browserName}' non supportato.")
        
        logger.debug(f"Browser {self.browserName} avviato con successo.", extra={"internal": True})

    def setup_options(self, options: list = ['disable-gpu', 'no-sandbox']) -> 'Options':
        """
        Definisce e restituisce le opzioni per il browser.

        Args:
            options (list, optional): Lista di opzioni per il driver browser da settare (default ['disable-gpu', 'no-sandbox']), **se il browser richiesto è headless** viene aggiunta l'opzione automaticamente

        Returns:
            Options (list, optional): oggetto contenente le opzioni di configurazione per il browser selezionato (default ['disable-gpu', 'no-sandbox'])
        """
        if self.browserName == "firefox":
            from selenium.webdriver.firefox.options import Options
        elif self.browserName == "chrome":
            from selenium.webdriver.chrome.options import Options
        else:
            raise ValueError(f"Browser '{self.browserName}' non supportato.")
        self.options = Options()
        if self.headless:
            logger.debug(f"Aggiungo opzione headless", extra={"internal": True})
            self.options.add_argument("--headless")
        logger.debug(f"Aggiungo le opzioni {options}", extra={"internal": True})
        for option in options:
            self.options.add_argument(f"--{option}")
        return self.options

    def start(self):
        """
            Avvia il browser con le opzioni definite nel costruttore.
        """
        logger.debug(f"Avvio {self.browserName.capitalize()} con le opzioni {self.options}", extra={"internal": True})
        if self.browserName == "firefox":
            from selenium.webdriver import Firefox as GlobalBrowser
        elif self.browserName == "chrome":
            from selenium.webdriver import Chrome as GlobalBrowser

        self.driver = GlobalBrowser(options=self.options)

    def quit(self):
        """
            Chiude il browser se è stato avviato.
        """
        if self.driver:
            logger.debug(f"Chiudo il browser {self.browserName}", extra={"internal": True})
            self.driver.quit()
        else:
            logger.warning(f"Nessun browser da chiudere perché mai avviato", extra={"internal": True})

    def open_url(self, url: str):
        """
        Naviga verso l'URL specificato.

        Args:
            url (str): L'indirizzo web da visitare.
        """
        if self.driver:
            logger.debug(f"Apro in {self.browserName} l'url {url}", extra={"internal": True})
            self.driver.get(url)
        else:
            logger.warning(f"Non è stato avviato alcun browser, apertura url {url} fallita", extra={"internal": True})

    def find(self, selector: str, by: By = By.CSS_SELECTOR):
        """
        Trova un singolo elemento nella pagina.

        Args:
            selector (str): Selettore dell'elemento.
            by (By, optional): Metodo di selezione (es. By.ID, By.CLASS_NAME, By.XPATH). Default By.CSS_SELECTOR.

        Returns:
            WebElement: L'elemento trovato.
        """
        logger.debug(f"Cerco l'elemento {selector} secondo il filtro {by}", extra={"internal": True})
        return self.driver.find_element(by, selector)

    def find_all(self, selector: str, by: By = By.CSS_SELECTOR):
        """
        Trova tutti gli elementi che corrispondono al selettore.

        Args:
            selector (str): Selettore degli elementi.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.

        Returns:
            list[WebElement]: Lista di elementi trovati.
        """
        logger.debug(f"Cerco gli elementi {selector} secondo il filtro {by}", extra={"internal": True})
        return self.driver.find_elements(by, selector)

    def click(self, selector: str, by: By = By.CSS_SELECTOR):
        """
        Clicca su un elemento nella pagina.

        Args:
            selector (str): Selettore dell'elemento da cliccare.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.
        """
        logger.debug(f"Effettuo il click sull'elemento {selector} applicando il filtro {by}", extra={"internal": True})
        el = self.find(selector, by)
        el.click()

    def type(self, selector: str, text: str, by: By = By.CSS_SELECTOR):
        """
        Inserisce testo in un campo input.

        Args:
            selector (str): Selettore dell'input.
            text (str): Testo da inserire.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.
        """
        logger.debug(f"Scrivo il testo \"{text}\" nel campo {selector} con il filtro di ricera {by}", extra={"internal": True})
        el = self.find(selector, by)
        el.clear()
        el.send_keys(text)

    def wait_for(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10):
        """
        Attende la presenza di un elemento nel DOM.

        Args:
            selector (str): Selettore dell'elemento.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.
            timeout (int, optional): Tempo massimo di attesa in secondi. Default 10.

        Returns:
            WebElement: L'elemento trovato, se presente entro il timeout.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        logger.debug(f"Il browser è in attesa dell'elemento {selector} con filtro {by}, attende {timeout} secondi prima di dare timeout", extra={"internal": True})
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))

    def screenshot(self, path: str):
        """
        Salva uno screenshot della pagina corrente.

        Args:
            path (str): Percorso completo del file dove salvare lo screenshot.
        """
        if self.driver:
            logger.debug(f"Salvo lo screenshot della pagina nel path {path}", extra={"internal": True})
            self.driver.save_screenshot(path)
        else:
            logger.warning(f"Non è possibile fare uno screenshot ad un browser mai avviatoq", extra={"internal": True})

    def download_mp4(self, url: str, savePath: str):
        """
        Gestore dei download dei file mp4
        
        Args:
            url (string, required): URL del file MP4 da scaricare
            savePath (string, required): Il percorso assoluto di dove salvare il file MP4
        
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download_file(url, savePath))

    async def download_file(self, url: str, save_path: str):
        """
        Funzione asincrona per scaricare un file mp4.

        Args:
            url (str): L'URL del file MP4 da scaricare
            save_path (str): Il percorso dove salvare il file
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()  # Alza un errore se la risposta non è 200
                    with open(save_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)  # Leggi il file a blocchi di 1024 byte
                            if not chunk:
                                break
                            f.write(chunk)
                    logger.debug(f"File {save_path} scaricato con successo.", extra={"internal": True})
        except Exception as e:
            logger.error(f"Errore nel download del file {url}: {e}", extra={"internal": True})

    def download_mp4_batch(self, urls: list, save_dir: str):
        """
        Gestore per eseguire fino a 6 download simultanei di file MP4.

        Args:
            urls (list): Lista degli URL dei file MP4 da scaricare
            save_dir (str): Directory dove salvare i file
        """
        # Limite di download simultanei (6 alla volta)
        semaphore = asyncio.Semaphore(6)

        async def download_with_semaphore(url, save_path):
            async with semaphore:
                await self.download_file(url, save_path)

        tasks = []
        for idx, url in enumerate(urls):
            save_path = os.path.join(save_dir, f"file_{idx+1}.mp4")
            tasks.append(download_with_semaphore(url, save_path))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*tasks))