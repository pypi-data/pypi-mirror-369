import threading
import uuid

class LogContext:
    _thread_local = threading.local()

    @staticmethod
    def get_log_id():
        return getattr(LogContext._thread_local, 'logId', None)

    @staticmethod
    def set_log_id(log_id):
        LogContext._thread_local.logId = log_id

    @staticmethod
    def generate_log_id():
        new_log_id = str(uuid.uuid4())
        LogContext.set_log_id(new_log_id)
        return new_log_id

    @staticmethod
    def clear_log_id():
        LogContext._thread_local.logId = None