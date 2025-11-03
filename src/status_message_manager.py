import threading


class StatusMessageManager:
    _instance_lock = threading.Lock()

    def __init__(self, status_bar=None):
        self.status_bar = status_bar

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(StatusMessageManager, "_instance"):
            with StatusMessageManager._instance_lock:
                if not hasattr(StatusMessageManager, "_instance"):
                    StatusMessageManager._instance = StatusMessageManager(*args, **kwargs)
        return StatusMessageManager._instance
