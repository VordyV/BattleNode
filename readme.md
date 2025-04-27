## Events
The full event name usually looks like this: `plugin.event`. The table below contains only the names of the events

| Event               | Arguments                                                                                                                 | Description                     |
|---------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| `init`              | -                                                                                                                         | Plugin initialization           |
| `shutdown`          | -                                                                                                                         | Shutting down plug-in           |
| `statuschange`      | [PluginStatuses](#plugin-statuses)                                                                                        | Changing plugin status          |
| `process.submitted` | [JobSubmissionEvent](https://apscheduler.readthedocs.io/en/3.x/modules/events.html#apscheduler.events.JobSubmissionEvent) | Process started                 |
| `process.executes`  | [JobEvent](https://apscheduler.readthedocs.io/en/3.x/modules/events.html#apscheduler.events.JobEvent)                     | Process completed without error |
| `process.error`     | [JobExecutionEvent](https://apscheduler.readthedocs.io/en/3.x/modules/events.html#apscheduler.events.JobExecutionEvent)   | Process failed                  |

### Other events
Events that are not related to plugins are global and are called by the application itself. Such events have the application name `battlenode` in the name instead of the plugin name

| Event              | Arguments | Description                      |
|--------------------|-----------|----------------------------------|
| `battlenode.start` | -         | The application has started      |
| `battlenode.stop`  | -         | The application is shutting down |
| `battlenode.error` | str       | There was an unexpected error    |

### Plugin Statuses
| Status         | Description                                                                                |
|----------------|--------------------------------------------------------------------------------------------|
| `LOADED`       | Successful import and pre-initialization                                                   |
| `INITIALIZING` | Full initialization, the init event and the child process are called                       |
| `RUNNING`      | It's working                                                                               |
| `STOPPING`     | During the shutdown process, the shutdown event is called and the child process is stopped |
| `STOPPED`      | Stopped                                                                                    |
| `ERROR`        | Something happened at one of the stages of either initialization or shutdown               |
| `RESTARTING`   | During shutdown and reloading                                                              |
| `DISABLED`     | Cannot be loaded, this action is prohibited                                                |
| `WAITING`      | First status after registration in the loader. Awaiting import                             |


