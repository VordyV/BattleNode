from ._config import Configurator
from loguru import logger
import multiprocessing
import battlenode

class Process:

    def __init__(self, target):
        self.__process = multiprocessing.Process(target=target, args=())

        