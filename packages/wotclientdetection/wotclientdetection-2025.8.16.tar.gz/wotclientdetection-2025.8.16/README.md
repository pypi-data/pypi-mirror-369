# wotclientdetection

Programatically detect and delegate WoT/MT launchers and clients.  
Based on original code from [OpenWG.Utils](https://gitlab.com/openwg/openwg.utils) and rewritten in Python.  
Currently supports only Windows.

## Installation

```
pip install wotclientdetection
```

## Examples

```py
from wotclientdetection import LauncherManager

manager = LauncherManager()
launchers = manager.get_launchers()
for launcher in launchers:
    clients = launcher.get_clients()
    for client in clients:
        print(client.path)
```

```py
from wotclientdetection import LauncherManager, LauncherFlavour, ClientBranch, ClientRealm

manager = LauncherManager()
launcher = manager.get_launcher(LauncherFlavour.WG)
client = launcher.get_client(realm=ClientRealm.EU)
```

```py
from wotclientdetection import LauncherManager, LauncherFlavour, ClientBranch, ClientRealm

STANDALONE_GAME_PATH = 'C:\Games\wot_standalone'

manager = LauncherManager()
launcher = manager.get_launcher(LauncherFlavour.STANDALONE)
launcher.register_client(STANDALONE_GAME_PATH)
```
