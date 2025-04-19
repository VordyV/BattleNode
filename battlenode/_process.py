import multiprocessing

class Process:

    def __init__(self, target):
        self.__process = multiprocessing.Process(target=target, args=())

    def start(self):
        self.__process.start()

    def stop(self):
        self.__process.terminate()

    @property
    def pid(self):
        return self.__process.pid