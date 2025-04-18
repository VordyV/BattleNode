## Events
The full event name usually looks like this: `plugin.event`. The table below contains only the names of the events

| Event          | Arguments      | Description            |
|----------------|----------------|------------------------|
| `init`         | -              | Plugin initialization  |
| `shutdown`     | -              | Shutting down plug-in  |
| `statuschange` | PluginStatuses | Changing plugin status |

### Other events
Events that are not related to plugins are global and are called by the application itself. Such events have the application name `battlenode` in the name instead of the plugin name

| Event              | Arguments | Description                      |
|--------------------|-----------|----------------------------------|
| `battlenode.start` | -         | The application has started      |
| `battlenode.stop`  | -         | The application is shutting down |


