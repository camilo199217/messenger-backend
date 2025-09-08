from concurrent.futures import ThreadPoolExecutor


class TaskManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=5)
        return cls._instance

    def add_task(self, func, *args, **kwargs):
        self.executor.submit(func, *args, **kwargs)


manager = TaskManager()
