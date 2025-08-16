import json, re, os, shutil, CloudFlare, time, typing, socket, subprocess
from sys import stdout
from time import sleep
from colorama import Fore, Style
from Common import *

@versione("2.0.0")
class TreeManager:
    """ Classe adibita alla gestione di file e cartelle con le classiche operazioni di creazione, aggiornamento, cancellazione, spostamento, rinomia ed altro """
    def __init__(self, base_path: str):
        """
            Inizializzatore dell'oggetto, richiede il path assoluto.
            
            Tip: Per passare il path assoluto se non è noto usare
            ```python
            os.path.dirname(__file__)
            ``` 
        """
        if not base_path.endswith("/"):
            self.base_path = f"{base_path}/"
        else:
            self.base_path = base_path

        if not base_path.startswith("/"):
            self.base_path = f"/{base_path}"
        else:
            self.base_path = base_path

    def _clean_file_name(self, fileName: str):
        """ Rimuove lo / iniziale al nome file """
        clean_file_name: str = fileName
        if fileName.startswith("/"):
            clean_file_name = fileName[1:]
        return clean_file_name

    def _clean_folder_name(self, folderName: str):
        """ Rimuove lo slash iniziale al nome della cartella passata in input """
        clean_folder_name: str = folderName
        if folderName.startswith("/"):
            clean_folder_name = folderName[1:]
        return clean_folder_name

    def moveFile(self, source: str, destination: str) -> bool:
        """ Funzione che permette di spostare un file da una sorgente ad una destinazione.
        
        Passare il nome del file che si vuole spostare ed il path asosluto della destinazione, il nome del file verrà mantenuto uguale.
        """
        full_origin = os.path.join(self.base_path, source)
        try:
            shutil.move(full_origin, destination)
            return True
        except Exception as e:
            return False
        
    def deleteFile(self, fileName: str) -> bool:
        """ Funzione che permette di eliminare un file"""
        fileName = self._clean_file_name(fileName)
        full_path = os.path.join(self.base_path, fileName)
        try:
            os.remove(full_path)
            return True
        except Exception as e:
            return False
    
    def createFolder(self, folderName: str) -> bool:
        """ Funzione che permette di creare una cartella o path di cartelle """
        folderName = self._clean_folder_name(folderName)
        full_new_folder = os.path.join(self.base_path, folderName)
        try:
            os.makedirs(full_new_folder, exist_ok=True) # Crea tutto il path di cartelle, se già esiste non viene generato errore, metterre exist_ok=False per far generare errore
            return True
        except Exception as e:
            return False
        
    def deleteFolder(self, folderName: str) -> bool:
        """ Funzione che permette di eliminare la cartella o path di cartelle, rimuoverà anche il relativo contenuto della cartella (file ed eventuali cartelle)"""
        folderName = self._clean_folder_name(folderName)
        full_remove_folder = os.path.join(self.base_path, folderName)
        try:
            shutil.rmtree(full_remove_folder)
            return True
        except Exception as e:
            return False
        
    def createFile(self, fileName: str, fileContent=None) -> bool:
        """ Funzione che permette di creare un file con o senza contenuto.

        Se il contenuto è un dizionario Python verrà salvato come JSON con le indentazioni.
        """
        # Per creare un nuovo file ci dobbiamo assicurare che il path esiste
        fileName = self._clean_file_name(fileName)
        full_path_file = os.path.join(self.base_path, fileName)
        self.createFolder(os.path.dirname(fileName))
        try:
            with open(full_path_file, "w", encoding="utf-8") as file:
                if isinstance(fileContent, dict):
                    # Il file è un JSON
                    json.dump(fileContent, file, indent=4)
                else:
                    if fileContent:
                        file.write(fileContent)
            return True
        except Exception as e:
            print(e)
            return False
        
    def readFile(self, fileName: str) -> str|None:
        """ Funzione che permette di leggere un file """
        # Per creare un nuovo file ci dobbiamo assicurare che il path esiste
        fileName = self._clean_file_name(fileName)
        full_path_file = os.path.join(self.base_path, fileName)
        try:
            with open(full_path_file, "r", encoding="utf-8") as file:
                fileContent = file.read()
            return fileContent
        except Exception as e:
            print(e)
            return False
        
    def checkPathExist(self, path: str) -> bool:
        """ Funzione che verifica se il path indicato esiste, può essere un path ad una cartella che file """
        path = self._clean_folder_name(path)
        full_path: str = os.path.join(self.base_path, path)
        return os.path.exists(full_path)
    
@versione("2.0.0")
class TerminalManager:
    """ Classe adibita a fornire funzionalità non relative ai file come ad esempio check se una porta è libera, inviare una mail ed altro """
    def __init__(self)->None:
        self.FFManager = TreeManager(os.path.dirname(__file__))

    def checkPortAvailability(self, port:int):
        """ Verifica se la porta passata è libera o meno, True indica che è libera, False indica che è già in utilizzo """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
            except socket.error as e:
                return False  # Se la porta è già in uso, si verificherà un errore durante il bind
            return True  # Se la porta non è in uso, il bind avrà successo

    def _check_sub_domain_name(self, name: str) -> bool:
        """ Valida il nome del nuovo dominio da aggiungere """
        validation_rule = r'(^[a-zA-Z])([a-zA-Z.\-_0-9]+)([^\-._ ]+)$'
        pattern = re.compile(validation_rule)
        esito = pattern.search(name)
        if esito:
            return True
        else:
            return False
        
    def runShellCommand(self, command:str) -> bool:
        """ Esegue un comando shell """
        result = subprocess.run(command, shell=True, capture_output=True)
        try:
            if result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
        
    def _crete_record_dns_cloudflare(self, nomeDominio: str) -> bool:
        """ Funzione che crea un record DNS su Cloudflare """
        bearer_token: str = "ZLMTX_L_cCi8qpz2cE9ZHNa7IuSmthEGwhRN4poN" # Da spostare nel file property
        cloudflare: CloudFlare = CloudFlare.CloudFlare(token=bearer_token)
        zone_name: str = "kaito.link" # dominio principale
        ip_address: str = "38.242.194.35" # da fare con il file di config

        # Ottieni l'ID della zona basato sul nome della zona
        zones = cloudflare.zones.get(params={'name': zone_name})
        if not zones:
            raise Exception("Zona non trovata")
        zone_id = zones[0]['id']
        type_record: str = "A"
        dns_data = {
            'type': type_record,
            'name': nomeDominio,
            'content': ip_address,
            'ttl': 1,
            'proxied': False
        }
        # Crea il record DNS
        try:
            response = cloudflare.zones.dns_records.post(zone_id, data=dns_data)
            return True
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            print("/zones.dns_records.post %d %s - api call failed" % (e, e))
            if "%d" % (e) == "81057":
                return True
            return False
        except Exception as e:
            print("Errore non gestito:", e)
            return False
        
    def getEnv(self) -> str:
        self.env = os.getenv("env")
        if self.env is None:
            self.env = ""
            
    def createSubDomain(self, nomeDominio: str, https=True) -> bool:
        """ Funzione che crea un nuovo dominio di terzo livello ed abilita l'HTTPS e crea un record DNS su Cloudflare
            
            Se il nome è pippo.pluto si viene a creare un dominio di terzo livello pippo ed uno di quarto livello che è pluto.

            Il nome deve rispettare la seguente regola:
            (^[a-aA-Z])([a-zA-Z.-_0-9]+)([^-._ ]+)$ ovvero iniziare per una qualsiasi lettera e contenere nel nome caratteri alfanumerici e/o . _ - e non deve finire per uno di questi 3 caratteri (anche lo spazio è escluso)       
        """
        self.getEnv()

        if self.env.upper() == "PROD":
            if self._check_sub_domain_name(nomeDominio):
                path_abs_subdomains: str = "/var/www/"
                path_abs_sites: str = "/etc/apache2/sites-available/"
                save_base_path: str = self.base_path
                self.base_path = path_abs_subdomains

                content_apache_domain: str = '''<VirtualHost *:80>

            ServerAdmin kaito
            ServerName __nomedominio__.kaito.link
            DocumentRoot /var/www/__nomedominio__.kaito.link

            # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
            # error, crit, alert, emerg.
            # It is also possible to configure the loglevel for particular
            # modules, e.g.
            #LogLevel info ssl:warn

            ErrorLog ${ ..APACHE_LOG_DIR}/error.log
            CustomLog ${ ..APACHE_LOG_DIR}/access.log combined

            # For most configuration files from conf-available/, which are
            # enabled or disabled at a global level, it is possible to
            # include a line for only one particular virtual host. For example the
            # following line enables the CGI configuration for this host only
            # after it has been globally disabled with "a2disconf".
            #Include conf-available/serve-cgi-bin.conf
    RewriteEngine on
    RewriteCond %{ ..SERVER_NAME} =__nomedominio__.kaito.link
    RewriteRule ^ https://%{ ..SERVER_NAME}%{ ..REQUEST_URI} [END,NE,R=permanent]
    </VirtualHost>'''.replace("__nomedominio__", nomeDominio).replace("{ ..", "{")
                # Creiamo innanzitutto la cartella e un file HTML index di default
                if self.createFolder(nomeDominio):
                    html_5_base_content: str = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nomeDominio}</title>
    </head>
    <body>
        Dominio {nomeDominio} creato con successo.
    </body>
    </html>"""
                    self.FFManager.createFile(f"{nomeDominio}.kaito.link/index.html", html_5_base_content)
                    self.base_path = path_abs_sites
                    # possiamo creare il file di Apache per aggiungerlo

                    try:
                        create_file_config: bool = self.FFManager.createFile(f"{nomeDominio}.kaito.link.conf", content_apache_domain)
                    except Exception as e:
                        # create_command = f'sudo bash -c "printf \\"{content_apache_domain}\\" > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                        create_command = f'sudo bash -c "echo \'{content_apache_domain}\' > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                        self.runShellCommand(create_command)

                    if not create_file_config:
                        # create_command = f'sudo bash -c "printf \\"{content_apache_domain}\\" > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                        create_command = f'sudo bash -c "echo \'{content_apache_domain}\' > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                        self.runShellCommand(create_command)
                    command: str = f"sudo a2ensite {nomeDominio}.kaito.link"
                    self.runShellCommand(command)
                    command = "sudo systemctl restart apache2"
                    self.runShellCommand(command)
                    if self._crete_record_dns_cloudflare(nomeDominio):
                        pass
                    else:
                        print("ERRORE CLOUDFLARE")

                    # Abilitiamo i certificati HTTPS
                    if https:
                        time.sleep(15)
                        https_enable: str = f"sudo certbot --apache -d {nomeDominio}.kaito.link --non-interactive --agree-tos --email sergio.catacci@icloud.com --redirect --keep-until-expiring"
                        self.runShellCommand(https_enable)
                self.base_path = save_base_path

            else:
                return False
        else:
            self.printColor("Non puoi creare un dominio su questa macchina.\nLa creazione è possibile fare solo su un server.", "red")
        
    def printAnimated(self, testo:str = "", durata:float = 0, carattereDaAnimare:str = "", numeroVolte:int = 1 ) -> None:
        """
            La funzione mette in coda al testo un elemento che entro un certo tempo aggiunge un elemento ala fine del testo per un numero di volte stabilito.

            è possibile fare anche il testo animato colorato passando ciò che la funzione printColor torna.
        """
        stdout.write(testo)
        stdout.flush()
        for _ in range(numeroVolte):
            sleep(durata)
            stdout.write(carattereDaAnimare)
            stdout.flush()
        stdout.write("\n")
        stdout.flush()

    def printColor(self, text:str, color: typing.Literal['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'], doPrint: bool=True) -> str:
        """
            Ritorna il testo colorato da visualizzare sulla shell, se non serve fare la print passare l'argomento doPrint a False
        """
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }

        if color.lower() in colors:
            testoColorato = colors[color.lower()] + text + Style.RESET_ALL
        else:
            testoColorato = text

        if doPrint:
            print(testoColorato)

        return testoColorato


#tt = TerminalManager()
#tt.createSubDomain("test")
# tt.printColor("Test", "magenta")
# tt.printAnimated(tt.printColor("Test animato colorato", "yellow"), 1, tt.printColor(".", "red"), 5)
# print("Test python")


@versione("1.0.1")
@deprecated("1.0.3", "Classe in dismissione per due classi distinte, una adibita esclusivamente a gestione file e folder")
class ServerUtils:
    """ Classe che mette si interaccia con la Shell del server eseguendo comandi """

    base_path: str
    """Path assoluto della working directory"""

    def __init__(self, base_path: str) -> None:
        # Modelliamo il base_path in modo che finisca sempre per / e che inizi sempre per / in quanto è path assoluto
        if not base_path.endswith("/"):
            self.base_path = f"{base_path}/"
        else:
            self.base_path = base_path

        if not base_path.startswith("/"):
            self.base_path = f"/{base_path}"
        else:
            self.base_path = base_path

    # -------
    # ------- START FILE & FOLDER MANAGER
    # -------

    def _clean_file_name(self, fileName: str):
        """ Rimuove lo / iniziale al nome file """
        clean_file_name: str = fileName
        if fileName.startswith("/"):
            clean_file_name = fileName[1:]
        return clean_file_name

    def _clean_folder_name(self, folderName: str):
        """ Rimuove lo slash iniziale al nome della cartella passata in input """
        clean_folder_name: str = folderName
        if folderName.startswith("/"):
            clean_folder_name = folderName[1:]
        return clean_folder_name

    def moveFile(self, source: str, destination: str) -> bool:
        """ Funzione che permette di spostare un file da una sorgente ad una destinazione.
        
        Passare il nome del file che si vuole spostare ed il path asosluto della destinazione, il nome del file verrà mantenuto uguale.
        """
        full_origin = os.path.join(self.base_path, source)
        try:
            shutil.move(full_origin, destination)
            return True
        except Exception as e:
            return False
        
    def deleteFile(self, fileName: str) -> bool:
        """ Funzione che permette di eliminare un file"""
        fileName = self._clean_file_name(fileName)
        full_path = os.path.join(self.base_path, fileName)
        try:
            os.remove(full_path)
            return True
        except Exception as e:
            return False
    
    def createFolder(self, folderName: str) -> bool:
        """ Funzione che permette di creare una cartella o path di cartelle """
        folderName = self._clean_folder_name(folderName)
        full_new_folder = os.path.join(self.base_path, folderName)
        try:
            os.makedirs(full_new_folder, exist_ok=True) # Crea tutto il path di cartelle, se già esiste non viene generato errore, metterre exist_ok=False per far generare errore
            return True
        except Exception as e:
            return False
        
    def deleteFolder(self, folderName: str) -> bool:
        """ Funzione che permette di eliminare la cartella o path di cartelle, rimuoverà anche il relativo contenuto della cartella (file ed eventuali cartelle)"""
        folderName = self._clean_folder_name(folderName)
        full_remove_folder = os.path.join(self.base_path, folderName)
        try:
            shutil.rmtree(full_remove_folder)
            return True
        except Exception as e:
            return False
        
    def createFile(self, fileName: str, fileContent=None) -> bool:
        """ Funzione che permette di creare un file con o senza contenuto.

        Se il contenuto è un dizionario Python verrà salvato come JSON con le indentazioni.
        """
        # Per creare un nuovo file ci dobbiamo assicurare che il path esiste
        fileName = self._clean_file_name(fileName)
        full_path_file = os.path.join(self.base_path, fileName)
        self.createFolder(os.path.dirname(fileName))
        try:
            with open(full_path_file, "w", encoding="utf-8") as file:
                if isinstance(fileContent, dict):
                    # Il file è un JSON
                    json.dump(fileContent, file, indent=4)
                else:
                    if fileContent:
                        file.write(fileContent)
            return True
        except Exception as e:
            print(e)
            return False
        
    def checkPathExist(self, path: str) -> bool:
        """ Funzione che verifica se il path indicato esiste, può essere un path ad una cartella che file """
        path = self._clean_folder_name(path)
        full_path: str = os.path.join(self.base_path, path)
        return os.path.exists(full_path)
    
    def read_file(self, fileName: str) -> bool:
        wi

    # -------
    # ------- END FILE & FOLDER MANAGER
    # -------


    # -------
    # ------- START HTTP MANAGER
    # -------
    
    def checkPortAvailability(self, port:int):
        """ Verifica se la porta passata è libera o meno, True indica che è libera, False indica che è già in utilizzo """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
            except socket.error as e:
                return False  # Se la porta è già in uso, si verificherà un errore durante il bind
            return True  # Se la porta non è in uso, il bind avrà successo

    def _check_sub_domain_name(self, name: str) -> bool:
        """ Valida il nome del nuovo dominio da aggiungere """
        validation_rule = r'(^[a-zA-Z])([a-zA-Z.\-_0-9]+)([^\-._ ]+)$'
        pattern = re.compile(validation_rule)
        esito = pattern.search(name)
        if esito:
            return True
        else:
            return False
        
    def runShellCommand(self, command:str) -> bool:
        result = subprocess.run(command, shell=True, capture_output=True)
        try:
            if result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
        
    def _crete_record_dns_cloudflare(self, nomeDominio: str) -> bool:
        """ Funzione che crea un record DNS su Cloudflare """
        bearer_token: str = "RtLbFg9k0aI7KhTqptZUpLm5oMM-mUaRHksbLXUe" # Da spostare nel file property
        cloudflare: CloudFlare = CloudFlare.CloudFlare(token=bearer_token)
        zone_name: str = "kaito.link" # dominio principale
        ip_address: str = "109.199.97.87" # da fare con il file di config

        # Ottieni l'ID della zona basato sul nome della zona
        zones = cloudflare.zones.get(params={'name': zone_name})
        if not zones:
            raise Exception("Zona non trovata")
        zone_id = zones[0]['id']
        type_record: str = "A"
        dns_data = {
            'type': type_record,
            'name': nomeDominio,
            'content': ip_address,
            'ttl': 1,
            'proxied': False
        }
        # Crea il record DNS
        try:
            response = cloudflare.zones.dns_records.post(zone_id, data=dns_data)
            return True
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            print("/zones.dns_records.post %d %s - api call failed" % (e, e))
            if "%d" % (e) == "81057":
                return True
            return False
        except Exception as e:
            print("Errore non gestito:", e)
            return False
            
    def createSubDomain(self, nomeDominio: str, https=True) -> bool:
        """ Funzione che crea un nuovo dominio di terzo livello ed abilita l'HTTPS e crea un record DNS su Cloudflare
            
            Se il nome è pippo.pluto si viene a creare un dominio di terzo livello pippo ed uno di quarto livello che è pluto.

            Il nome deve rispettare la seguente regola:
            (^[a-aA-Z])([a-zA-Z.-_0-9]+)([^-._ ]+)$ ovvero iniziare per una qualsiasi lettera e contenere nel nome caratteri alfanumerici e/o . _ - e non deve finire per uno di questi 3 caratteri (anche lo spazio è escluso)       
        """
        if self._check_sub_domain_name(nomeDominio):
            path_abs_subdomains: str = "/var/www/"
            path_abs_sites: str = "/etc/apache2/sites-available/"
            save_base_path: str = self.base_path
            self.base_path = path_abs_subdomains

            content_apache_domain: str = '''<VirtualHost *:80>

        ServerAdmin kaito
        ServerName __nomedominio__.kaito.link
        DocumentRoot /var/www/__nomedominio__.kaito.link

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${ ..APACHE_LOG_DIR}/error.log
        CustomLog ${ ..APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
RewriteEngine on
RewriteCond %{ ..SERVER_NAME} =__nomedominio__.kaito.link
RewriteRule ^ https://%{ ..SERVER_NAME}%{ ..REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>'''.replace("__nomedominio__", nomeDominio).replace("{ ..", "{")
            # Creiamo innanzitutto la cartella e un file HTML index di default
            if self.createFolder(nomeDominio):
                html_5_base_content: str = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nomeDominio}</title>
</head>
<body>
    Dominio {nomeDominio} creato con successo.
</body>
</html>"""
                self.createFile(f"{nomeDominio}.kaito.link/index.html", html_5_base_content)
                self.base_path = path_abs_sites
                # possiamo creare il file di Apache per aggiungerlo

                try:
                    create_file_config: bool = self.createFile(f"{nomeDominio}.kaito.link.conf", content_apache_domain)
                except Exception as e:
                    # create_command = f'sudo bash -c "printf \\"{content_apache_domain}\\" > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                    create_command = f'sudo bash -c "echo \'{content_apache_domain}\' > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                    self.runShellCommand(create_command)

                if not create_file_config:
                    # create_command = f'sudo bash -c "printf \\"{content_apache_domain}\\" > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                    create_command = f'sudo bash -c "echo \'{content_apache_domain}\' > {path_abs_sites}{nomeDominio}.kaito.link.conf"'
                    self.runShellCommand(create_command)
                command: str = f"sudo a2ensite {nomeDominio}.kaito.link"
                self.runShellCommand(command)
                command = "sudo systemctl restart apache2"
                self.runShellCommand(command)
                if self._crete_record_dns_cloudflare(nomeDominio):
                    pass
                else:
                    print("ERRORE CLOUDFLARE")

                # Abilitiamo i certificati HTTPS
                if https:
                    time.sleep(15)
                    https_enable: str = f"sudo certbot --apache -d {nomeDominio}.kaito.link --non-interactive --agree-tos --email sergio.catacci@icloud.com --redirect --keep-until-expiring"
                    self.runShellCommand(https_enable)
            self.base_path = save_base_path

        else:
            return False
        
    def scriviTestoAnimato(self, testo:str = "", durata:float = 0, carattereDaAnimare:str = "", numeroVolte:int = 1 ) -> None:
        """ Funzione che stampa un messaggio sul terminale con i caratteri che compaiono uno alla volta in un certo tempo massimo    
        """
        stdout.write(testo)
        stdout.flush()
        for _ in range(numeroVolte):
            sleep(durata)
            stdout.write(carattereDaAnimare)
            stdout.flush()
        stdout.write("\n")
        stdout.flush()

    def scriviTestoColorato(self, text:str, color:str) -> str:
        """
        Stampa il testo colorato sulla console.

        Args:
            text (str): Il testo da stampare.
            color (str): Il colore del testo. Deve essere uno di:
                        'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'.
        """
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }

        if color.lower() in colors:
            testoColorato = colors[color.lower()] + text + Style.RESET_ALL
        else:
            testoColorato = text

        return testoColorato

    
        
# ttt = ServerUtils(os.path.dirname(__file__))
# ttt.createSubDomain("passkey")
# ttt.createSubDomain("prod.test")
# ttt.createSubDomain("prod.tg3")
# ttt.createFolder("TestNoSlash")
# ttt.createFolder("/TestSlash")
# ttt.createFolder("TestNoSlash/Test1/Test2/TTT")
# ttt.deleteFolder("/TestNoSlash/Test1/Test2")
# ttt.createFile("TestNoSlash/Test1/test.txt")
# ttt.createFile("TestNoSlash/Test1/Test2/text.txt", "ciao")
# ttt.deleteFile("/Test1/test.txt")
# ttt.deleteFolder("Test1")
# ttt.createFile("Test1/text.json", {"ok": True, "test": {"nodo1": {"chiave1": "string"}}})
# ttt.deleteFile("text.json")
# ttt.deleteFolder("TestNoSlash")
# print(ttt.checkPathExist("TestNoSlash"))
# print(ttt.checkPathExist("TestNoSlash1"))
# print(ttt.checkPathExist("TestNoSlash/Test1/Test2/text.txt"))
# print(ttt.checkPathExist("TestNoSlash/Test1/Test21/text.txt"))
# print(ttt.checkPortAvailability(0))
# print(ttt.checkPortAvailability(10))
# ttt.createFolder("../Test")
# ttt.deleteFolder("../Test")
# ttt.createFile("../Test/Test.json", {"ok": {"not_ok": False}})
# ttt.deleteFolder("../Test")