import os
import subprocess
import xml.etree.ElementTree as ET
import psutil
from wotclientdetection.entities.client import Client

class LauncherBase:

    def __init__(self, metadata, path):
        self._clients = []
        self.metadata = metadata
        self.path = path
        self.enumerate_clients()

    @property
    def flavour(self):
        return self.metadata.flavour

    @property
    def executable(self):
        return self.metadata.executable

    def enumerate_clients(self):
        self._clients.clear()

    def register_client(self, path, isPreffered=False):
        if self.is_registered(path):
            return
        client = Client(path, self.flavour, isPreffered)
        if not client.is_valid:
            return
        self._clients.append(client)

    def get_clients(self) -> list[Client]:
        return self._clients

    def get_client(self, branch=None, realm=None) -> Client:
        for client in self._clients:
            if branch is not None and branch == client.branch:
                return client
            if realm is not None and realm == client.realm:
                return client
        return None

    def get_preffered_client(self) -> Client:
        for client in self._clients:
            if client.is_preffered:
                return client
        return None

    def is_registered(self, path):
        for client in self._clients:
            if client.path == path:
                return True
        return False


class LauncherStandalone(LauncherBase):

    def __init__(self, metadata, path):
        super(LauncherStandalone, self).__init__(metadata, path)

    def __repr__(self):
        return (f'<LauncherStandalone metadata={self.metadata} path={self.path}>')


class Launcher(LauncherBase):

    def __init__(self, metadata, path):
        super(Launcher, self).__init__(metadata, path)

    def enumerate_clients(self):
        super(Launcher, self).enumerate_clients()
        preferences_path = os.path.normpath(os.path.join(self.path, 'preferences.xml'))
        if not os.path.isfile(preferences_path):
            return
        preferences_xml = ET.parse(preferences_path)
        root = preferences_xml.getroot()
        self.__get_preffered_client_from_preferences(root)
        self.__get_clients_from_preferences(root)
        self.__get_clients_from_apps()

    def is_started(self):
        for process in psutil.process_iter():
            if process is None:
                continue
            if process.name() != self.executable:
                continue
            if self.path in process.cwd():
                return True
        return False

    def run(self):
        executable_path = os.path.normpath(os.path.join(self.path, self.executable))
        if not os.path.isfile(executable_path):
            return
        try:
            subprocess.run(executable_path, shell=True)
            return True
        except:
            pass
        return False

    def terminate(self):
        for process in psutil.process_iter():
            if process is None:
                continue
            if process.name() != self.executable:
                continue
            if self.path in process.cwd():
                process.terminate()
                return True
        return False

    def __get_preffered_client_from_preferences(self, root):
        element = root.find('application/games_manager/selectedGames/WOT')
        if element is None:
            return
        path = element.text.strip()
        self.register_client(path, isPreffered=True)

    def __get_clients_from_preferences(self, root):
        elements = root.findall('application/games_manager/games/game')
        if elements is None:
            return
        for element in elements:
            child = element.find('working_dir')
            if child is None:
                continue
            path = child.text.strip()
            self.register_client(path)

    def __get_clients_from_apps(self):
        apps_path = os.path.normpath(os.path.join(self.path, 'apps'))
        for root, _, files in os.walk(apps_path):
            for file in files:
                if 'wot.' not in root:
                    continue
                manifestPath = os.path.normpath(os.path.join(root, file))
                try:
                    with open(manifestPath, 'r', newline='\n') as manifestFile:
                        clientPath = manifestFile.read().strip()
                except Exception:
                    pass
                self.register_client(clientPath)

    def __repr__(self):
        return (f'<Launcher metadata={self.metadata} path={self.path}>')
