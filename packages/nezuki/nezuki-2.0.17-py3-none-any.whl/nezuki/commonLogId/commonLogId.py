from functools import wraps
import sys
from LogContext import LogContext
from commonLoggerSingleTon import get_logger

def auto_log_execution(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not LogContext.get_log_id():
            LogContext.generate_log_id()
        try:
            result = func(self, *args, **kwargs)
            return result
        finally:
            LogContext.clear_log_id()
    return wrapper

def log_exceptions(func):
    """Decoratore per loggare le eccezioni senza interrompere l'esecuzione."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = f"Exception: {exc_type.__name__}: {exc_value}"
            logger.logger.error(f"Si è verificato un errore: {error_message}")
            raise e
    return wrapper

class CombinedMeta(type):
    def __new__(cls, name, bases, dct):
        # Aggiungi un logger automaticamente alla classe
        dct['logger'] = get_logger()
        
        for attr, value in dct.items():
            if callable(value) and not attr.startswith("__"):
                value = auto_log_execution(value)  # Gestione automatica del logId
                value = log_exceptions(value)  # Gestione automatica delle eccezioni
                dct[attr] = value
        return super().__new__(cls, name, bases, dct)