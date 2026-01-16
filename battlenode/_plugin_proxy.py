from ._plugin import Plugin, BasePlugin
from ._plugin_statuses import PluginStatuses

class PPNotInitException(Exception): pass

class PluginProxy:
    def __init__(self, plugin: Plugin):
        self.__plugin = plugin

    def _get_instance(self) -> BasePlugin:
        if self.__plugin.status != PluginStatuses.RUNNING or not self.__plugin.instance: raise PPNotInitException(f"Module '{self.__plugin.name}' is not initialized")
        return self.__plugin.instance

    def __getattr__(self, item) -> object:
        instance = self._get_instance()
        attr = getattr(instance, item)
        return attr

    def __str__(self):
        return f"Plugin(name={self.__plugin.name}, version={self.__plugin.meta.version})"