import os
import sys
import logging
import inspect
import json
from logging.handlers import TimedRotatingFileHandler
from coloredlogs import ColoredFormatter

# Variabile globale per il logger di Nezuki
_nezuki_logger = None

def get_caller_info():
    """
    Restituisce una stringa formattata "File.py::Classe::Funzione".
    Se non disponibili, restituisce "_na_".
    """
    filename, classname, function = "_na_", "_na_", "_na_"
    try:
        stack = inspect.stack()
        for frame_info in stack[2:]:
            lower_filename = frame_info.filename.lower()
            if "logging" not in lower_filename and "logger" not in lower_filename:
                filename = os.path.basename(frame_info.filename) or "_na_"
                function = frame_info.function or "_na_"
                if "self" in frame_info.frame.f_locals:
                    classname = frame_info.frame.f_locals["self"].__class__.__name__
                break
    except Exception:
        pass
    return f"{filename}::{classname}::{function}"

def merge_configs(user_config):
    """
    Unisce la configurazione fornita dall'utente con quella di default.
    Se un parametro è mancante, viene impostato al suo valore predefinito.
    """
    default_config = {
        "level": logging.DEBUG,
        "console": {
            "enabled": True,
            "level": logging.DEBUG,
            "formatter": "%(asctime)s - %(name)s - %(levelname)s - %(context)s - %(internal_str)s - %(message)s"
        },
        "file": {
            "enabled": True,
            "filename": None,  # 🔴 Obbligatorio, deve essere passato dall'utente
            "level": logging.DEBUG,
            "formatter": "%(asctime)s - %(name)s - %(levelname)s - %(context)s - %(internal_str)s - %(message)s",
            "maxBytes": 100 * 1024 * 1024,  # 100MB
            "backupCount": 5,
            "when": "D",
            "interval": 30
        }
    }
    
    # Unione delle configurazioni con fallback ai valori di default
    merged_config = default_config.copy()
    if user_config:
        for key in user_config:
            if key in merged_config and isinstance(merged_config[key], dict):
                merged_config[key].update(user_config[key])  # Unisce i dizionari
            else:
                merged_config[key] = user_config[key]
    
    # ✅ Controllo se il filename è stato specificato
    if merged_config["file"]["enabled"] and not merged_config["file"]["filename"]:
        raise ValueError("Errore: Devi specificare un percorso per il file di log ('file.filename').")

    return merged_config

class CallerInfoFilter(logging.Filter):
    """Aggiunge 'context' e 'internal_str' ai record di log."""
    def filter(self, record):
        if not hasattr(record, "internal"):
            record.internal = False
        record.internal_str = "[INTERNAL]" if record.internal else "[USER]"
        record.context = get_caller_info()
        return True

class NezukiFormatter(logging.Formatter):
    """Formatter che garantisce che ogni log sia su una sola riga e contiene tutte le info."""
    def format(self, record):
        record.__dict__.setdefault("context", get_caller_info())
        record.__dict__.setdefault("internal_str", "[USER]")
        s = super().format(record)
        return s.replace("\n", "\\n").replace("\r", "\\r")

class SizeAndTimeRotatingFileHandler(TimedRotatingFileHandler):
    """Gestisce la rotazione del file di log sia per dimensione che per tempo."""
    def __init__(self, filename, when="D", interval=30, backupCount=5, maxBytes=100*1024*1024, **kwargs):
        self.maxBytes = maxBytes
        super().__init__(filename, when=when, interval=interval, backupCount=backupCount, **kwargs)
    def shouldRollover(self, record):
        return super().shouldRollover(record) or (os.path.exists(self.baseFilename) and os.stat(self.baseFilename).st_size >= self.maxBytes)

def configure_nezuki_logger(config):
    """L'utente chiama questa funzione per configurare il logger globale."""
    global _nezuki_logger
    _nezuki_logger = _create_logger(config)

def get_nezuki_logger():
    """Restituisce il logger globale di Nezuki. Se non è configurato, usa un logger di default."""
    global _nezuki_logger
    if _nezuki_logger is None:
        json_path = os.getenv("NEZUKILOGS")
        print(json_path)
        with open(json_path, "r") as f:
            default_config = json.load(f)
        _nezuki_logger = _create_logger(default_config)
    return _nezuki_logger

def _create_logger(config):
    """Crea un'istanza del logger con la configurazione fornita."""
    config = merge_configs(config)
    logger = logging.getLogger("Nezuki")
    logger.setLevel(config["level"])
    logger.propagate = False

    logger.handlers = []  # Pulisce gli handler esistenti
    logger.addFilter(CallerInfoFilter())

    # ✅ Console Handler con ColoredFormatter
    console_conf = config["console"]
    if console_conf["enabled"]:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(console_conf["level"])
        ch.setFormatter(ColoredFormatter(console_conf["formatter"]))
        ch.addFilter(CallerInfoFilter())
        logger.addHandler(ch)

    # ✅ File Handler
    file_conf = config["file"]
    if file_conf["enabled"]:
        filename = file_conf["filename"]
        dir_name = os.path.dirname(os.path.abspath(filename))
        os.makedirs(dir_name, exist_ok=True)

        fh = SizeAndTimeRotatingFileHandler(
            filename=filename,
            when=file_conf["when"],
            interval=file_conf["interval"],
            backupCount=file_conf["backupCount"],
            maxBytes=file_conf["maxBytes"]
        )
        fh.setLevel(file_conf["level"])
        fh.setFormatter(NezukiFormatter(file_conf["formatter"]))
        fh.addFilter(CallerInfoFilter())
        logger.addHandler(fh)

    return logger

class NezukiLogger:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super(NezukiLogger, cls).__new__(cls)
            cls._instance._configured = False
        return cls._instance

    def __init__(self, config=None):
        if self._configured:
            return
        
        # 🔄 Integra la configurazione dell'utente con i valori di default
        config = merge_configs(config)

        self.logger = logging.getLogger("Nezuki")
        self.logger.setLevel(config["level"])
        self.logger.propagate = False

        self._configure_handlers(config)
        self.logger.addFilter(CallerInfoFilter())  # ✅ Applica il filtro ai log
        self._configured = True

    def _configure_handlers(self, config):
        self.logger.handlers = []
        fmt_str = config["console"]["formatter"]

        # ✅ Console Handler con coloredlogs
        console_conf = config["console"]
        if console_conf["enabled"]:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(console_conf["level"])
            ch.setFormatter(ColoredFormatter(fmt_str))  # ✅ Mantiene i colori sulla console
            ch.addFilter(CallerInfoFilter())  # ✅ Aggiunge il filtro
            self.logger.addHandler(ch)

        # ✅ File Handler
        file_conf = config["file"]
        if file_conf["enabled"]:
            filename = file_conf["filename"]
            dir_name = os.path.dirname(os.path.abspath(filename))
            os.makedirs(dir_name, exist_ok=True)  # ✅ Assicura che la cartella esista

            fh = SizeAndTimeRotatingFileHandler(
                filename=filename,
                when=file_conf["when"],
                interval=file_conf["interval"],
                backupCount=file_conf["backupCount"],
                maxBytes=file_conf["maxBytes"]
            )
            fh.setLevel(file_conf["level"])
            fh.setFormatter(NezukiFormatter(file_conf["formatter"]))  # ✅ Usa il formatter corretto
            fh.addFilter(CallerInfoFilter())  # ✅ Applica il filtro
            self.logger.addHandler(fh)

def get_logger(config=None):
    return NezukiLogger(config).logger