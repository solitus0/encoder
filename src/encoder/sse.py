from queue import Queue
from threading import Lock


class SSEQueueSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SSEQueueSingleton, cls).__new__(cls)
                cls._instance.queue = Queue()
        return cls._instance
