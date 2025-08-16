import os
from wotclientdetection.entities.launcher import Launcher, LauncherStandalone
from wotclientdetection.constants import *

class LauncherManager:

    def __init__(self):
        self.__inititalized = False
        self.__launchers = []
        self.initialize()

    @property
    def initialized(self):
        return self.__inititalized

    def initialize(self):
        if self.__inititalized:
            return
        self.enumerate_launchers()
        self.__inititalized = True

    def finalize(self):
        if not self.__inititalized:
            return
        self.__launchers.clear()
        self.__inititalized = False

    def enumerate_launchers(self, force=False):
        if force:
            self.__launchers.clear()
        if len(self.__launchers):
            return
        for metadata in LAUNCHERS_METADATA:
            if metadata.flavour == LauncherFlavour.STANDALONE:
                self.__launchers.append(LauncherStandalone(metadata, ''))
                continue
            path = os.path.normpath(os.path.join(os.path.expandvars('%ProgramData%'), metadata.path))
            if not os.path.isdir(path):
                continue
            pointer_file_path = os.path.normpath(os.path.join(path, metadata.pointer))
            if not os.path.isfile(pointer_file_path):
                continue
            try:
                with open(pointer_file_path, 'r', newline='\n') as pointerFile:
                    real_path = os.path.normpath(pointerFile.read().strip())
            except:
                continue
            executable_path = os.path.normpath(os.path.join(real_path, metadata.executable))
            if not os.path.isfile(executable_path):
                continue
            launcher = Launcher(metadata, real_path)
            self.__launchers.append(launcher)

    def get_launcher(self, flavour=None, realm=None) -> Launcher | LauncherStandalone:
        if not self.__inititalized:
            return None
        if flavour is None:
            flavour = CLIENT_REALM_TO_LAUNCHER_FLAVOUR_MAP.get(realm, LauncherFlavour.UNKNOWN)
        for launcher in self.__launchers:
            if launcher.flavour == flavour:
                return launcher
        return None

    def get_launchers(self) -> list[Launcher | LauncherStandalone]:
        if not self.__inititalized:
            return None
        return self.__launchers

    def remove_launcher(self, flavour):
        if not self.__inititalized:
            return
        launcher = self.get_launcher(flavour)
        if launcher is None:
            return
        self.__launchers.remove(launcher)
