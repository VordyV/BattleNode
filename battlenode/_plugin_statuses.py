from enum import Enum

class PluginStatuses(Enum):
    LOADED = 0 #
    INITIALIZING = 1 #
    RUNNING = 2 #
    STOPPING = 3 #
    STOPPED = 4 #
    ERROR = 5 #
    RESTARTING = 6 #
    DISABLED = 7
    WAITING = 8 #