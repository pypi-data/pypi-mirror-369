import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import os
import uuid
from datetime import datetime
from LogContext import LogContext
from ServerUtils import TreeManager

version="2.0.9"

class ExtendedLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET, pathLogs="/Logs", ownerModuleLog=False):
        super().__init__(name, level)
        self.pathLogs = pathLogs
        self.ownerModuleLog = ownerModuleLog
        self.treeManager = TreeManager(self.pathLogs)
        if not self.treeManager.checkPathExist(self.pathLogs):
            self.treeManager.createFolder("")

    def setModuleLog(self, moduleLog=True):
        """Imposta la variabile che indica se un log è interno oppure no e aggiorna il path dei log."""
        self.ownerModuleLog = moduleLog
        if moduleLog:
            self.pathLogs = os.path.join(self.pathLogs, "Module")  # Aggiunge "/Module" al path dei log
        else:
            self.pathLogs = self.pathLogs.replace("/Module", "")  # Rimuove "/Module" se già presente

        # Riapplica il formatter agli handler con il nuovo stato di ownerModuleLog
        for handler in self.handlers:
            if isinstance(handler.formatter, CustomFormatter):
                handler.formatter = CustomFormatter(
                    '%(asctime)s || %(levelname)s || %(esito_funzionale)s || %(module)s || %(funcName)s || %(logId)s || %(message)s || %(details)s',
                    log_instance=self
                )

class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', log_instance=None):
        super().__init__(fmt, datefmt, style)
        self.log_instance = log_instance

    def format(self, record):
        global version
        # Aggiunge logId al record dinamicamente
        record.logId = LogContext.get_log_id() or "No LogID"
        
        # Gestione del campo "EsitoFunzionale" e "Dettagli"
        record.esito_funzionale = getattr(record, 'esito_funzionale', '-1')
        record.details = getattr(record, 'details', '')
        record.internal = getattr(record, 'internal', False)
        record.versionLog = version

        # Formattazione del messaggio
        record.msg = record.msg.replace('\n', '<br>')
        record.details = record.details.replace('\n', '<br>')
        return super().format(record)

class LoggerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self, localMode=False, localFileLogPath="/Logs", logId="First init", ownerModuleLog=False):
        if not hasattr(self, 'initialized'):  # Verifica se l'istanza è già stata inizializzata
            self.isLocal = localMode
            print(localFileLogPath, "\n\n")
            self.pathLogs = localFileLogPath if localFileLogPath else "/Logs"  # Usare un percorso predefinito valido
            self.logId = logId
            self.ownerModuleLog = ownerModuleLog
            self.setup_logging()
            self.initialized = True  # Segnala che l'istanza è stata inizializzata

    def _update_log_id(self):
        """Aggiorna il log id."""
        self.logId = uuid.uuid1()
        return self.logId

    def setup_logging(self):
        """Configura il logger con gli handler e i formatter appropriati."""
        self.logger = ExtendedLogger(self.__class__.__name__, logging.DEBUG, self.pathLogs)
        self.logger.setLevel(logging.DEBUG)

        # Assicurarsi che la directory esista
        # os.makedirs(self.pathLogs, exist_ok=True)

        # Handlers per la rotazione dei log
        timed_handler = TimedRotatingFileHandler(f"{self.pathLogs}/bot_log_timed.log", when="D", interval=1, backupCount=30)
        size_handler = RotatingFileHandler(f"{self.pathLogs}/bot_log_size.log", maxBytes=200*1024*1024, backupCount=5)

        # Formatter
        formatter = CustomFormatter(
            '%(asctime)s || %(levelname)s || %(internal)s || %(versionLog)s || %(esito_funzionale)s || %(module)s || %(funcName)s || %(logId)s || %(message)s || %(details)s',
            log_instance=self
        )

        timed_handler.setFormatter(formatter)
        size_handler.setFormatter(formatter)

        # StreamHandler per loggare anche su console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Aggiungi handlers al logger
        self.logger.addHandler(timed_handler)
        self.logger.addHandler(size_handler)
        self.logger.addHandler(console_handler)

    def get_logs(self, query=''):
        """Ritorna i file di log dei file backup."""
        log_files = [f for f in os.listdir(self.pathLogs) if (f.endswith('.log') and "bot_log_size" in f)]
        logs = []
        for log_file in log_files:
            with open(os.path.join(self.pathLogs, log_file), 'r') as f:
                for line in f:
                    if query.lower() in line.lower():
                        logs.append(line.strip())
        
        # Ordina i log in ordine decrescente per data e ora
        logs.sort(key=lambda x: datetime.strptime(x.split(" - ")[0], '%Y-%m-%d %H:%M:%S,%f'), reverse=True)
        return logs

    def log(self, level, message, esito_funzionale='-1', details='', internal=False):
        """Metodo per eseguire il logging con gestione del logId e campi aggiuntivi."""
        log_id = LogContext.get_log_id() or "No LogID"
        self.logger.log(level, message, extra={'logId': log_id, 'esito_funzionale': esito_funzionale, 'details': details, 'internal': internal})

# Funzione di convenienza per ottenere il logger singleton
def get_logger(localMode=False, localFileLogPath="/Logs", logId="First init", ownerModuleLog=False):
    instance = LoggerSingleton(localMode, localFileLogPath, logId, ownerModuleLog)
    return instance.logger  # Ritorna direttamente l'oggetto logger