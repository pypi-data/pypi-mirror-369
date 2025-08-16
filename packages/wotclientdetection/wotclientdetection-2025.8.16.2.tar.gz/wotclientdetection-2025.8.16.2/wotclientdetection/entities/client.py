import os
import re
import subprocess
import xml.etree.ElementTree as ET
import psutil
from packaging.version import Version
from wotclientdetection.constants import *
from wotclientdetection.shared import is_semver_version

class Client:

    def __init__(self, path, launcher_flavour, is_preffered=False):
        self.branch = ClientBranch.UNKNOWN
        self.launcher_flavour = launcher_flavour
        self.l10n = None
        self.path = path
        self.path_mods = None
        self.path_resmods = None
        self.mod_extension = None
        self.mod_extension_mask = None
        self.replay_extension = None
        self.replay_extension_mask = None
        self.realm = None
        self.type = ClientType.UNKNOWN
        self.client_version = None
        self.full_client_version = None
        self.exe_filename = None
        self.exe_version = None
        self.is_pdc_supported = False
        self.is_pdc_exists = False
        self.pdc_path = None
        self.is_preffered = is_preffered
        self.is_valid = False
        self.__read_client_data()

    def update(self):
        self.__invalidate()
        self.__read_client_data()

    def is_version_match(self, pattern):
        if not self.is_valid:
            return False
        regex = re.compile(pattern)
        match = regex.match(self.client_version)
        return bool(match)

    def is_started(self):
        if not self.is_valid:
            return False
        if not self.exe_filename:
            return False
        for process in psutil.process_iter():
            if process is None:
                continue
            if process.name() != self.exe_filename:
                continue
            if self.path in process.cwd():
                return True
        return False

    def run(self, replay_path=None):
        if not self.is_valid:
            return False
        if not self.exe_filename:
            return False
        executable_path = os.path.normpath(os.path.join(self.path, self.exe_filename))
        if not os.path.isfile(executable_path):
            return
        launch_args = [executable_path]
        if replay_path is not None:
            launch_args.append(replay_path)
        try:
            subprocess.run(launch_args, shell=True)
            return True
        except:
            pass
        return False

    def terminate(self):
        result = False
        if not self.is_valid:
            return result
        if not self.exe_filename:
            return result
        for process in psutil.process_iter():
            if process is None:
                continue
            if process.name() != self.exe_filename:
                continue
            if self.path in process.cwd():
                process.terminate()
                result = True
        return result

    def __is_valid_metadata(self):
        if not os.path.isdir(self.path):
            return
        for file in ('app_type.xml', 'game_info.xml', 'paths.xml', 'version.xml'):
            if not os.path.isfile(os.path.join(self.path, file)):
                return
        self.is_valid = True

    def __read_client_data(self):
        self.__is_valid_metadata()
        if not self.is_valid:
            return
        self.__read_app_type()
        self.__read_version()
        self.__read_game_info()
        self.__read_paths()
        self.__read_exe_filename()
        if not self.is_valid:
            self.__invalidate()
            return
        self.__read_exe_version()
        self.__read_pdc_state()

    def __read_app_type(self):
        app_type_path = os.path.normpath(os.path.join(self.path, 'app_type.xml'))
        if not os.path.isfile(app_type_path):
            return
        app_type_xml = ET.parse(app_type_path)
        root = app_type_xml.getroot()
        element = root.find('app_type')
        if element is None:
            return
        app_type = element.text.strip().lower()
        if app_type == 'hd':
            self.type = ClientType.HD
        elif app_type == 'sd':
            self.type = ClientType.SD

    def __read_version(self):
        version_path = os.path.normpath(os.path.join(self.path, 'version.xml'))
        if not os.path.isfile(version_path):
            return
        version_xml = ET.parse(version_path)
        root = version_xml.getroot()
        element = root.find('meta/realm')
        if element is not None:
            self.realm = element.text.strip()
        element = root.find('version')
        if element is None:
            return
        version = element.text.strip()
        version = version.replace('v.', '')
        version = version.strip()
        self.full_client_version = version
        # remove #build_number suffix
        version = version.split()[:-1]
        version = ' '.join(version)
        # get only semver version
        version = version.split(None, 1)
        if is_semver_version(version[0]):
            self.client_version = version[0]
        version = ' '.join(version)
        if self.client_version is None:
            self.client_version = version
        self.branch = ClientBranch.RELEASE
        if 'Common Test' in version:
            self.branch = ClientBranch.COMMON_TEST
        elif 'ST' in version:
            self.branch = ClientBranch.SUPERTEST
        elif 'SB' in version:
            self.branch = ClientBranch.SANDBOX
        elif 'Closed Test' in version:
            self.branch = ClientBranch.CLOSED_TEST

    def __read_game_info(self):
        game_info_path = os.path.normpath(os.path.join(self.path, 'game_info.xml'))
        if not os.path.isfile(game_info_path):
            return
        game_info_xml = ET.parse(game_info_path)
        root = game_info_xml.getroot()
        element = root.find('game/id')
        if element is not None:
            id = element.text.strip()
            if '.RPT.' in id:
                self.branch = ClientBranch.COMMON_TEST
        element = root.find('game/localization')
        if element is None:
            return
        self.l10n = element.text.strip()

    def __read_paths(self):
        paths_path = os.path.normpath(os.path.join(self.path, 'paths.xml'))
        if not os.path.isfile(paths_path):
            return
        paths_xml = ET.parse(paths_path)
        root = paths_xml.getroot()
        elements = root.findall('Paths/Path')
        if elements is None:
            return
        for element in elements:
            path = element.text.strip()
            path = path.replace('./', '')
            path = path.replace('/', '\\')
            if path.startswith('res_mods'):
                self.path_resmods = path
            elif path.startswith('mods'):
                self.path_mods = path
                mod_extension_mask = element.attrib.get('mask', None)
                if mod_extension_mask is not None:
                    mod_extension_mask = mod_extension_mask.strip()
                    self.mod_extension = mod_extension_mask[2:]
                    self.mod_extension_mask = mod_extension_mask
        self.replay_extension = ClientReplayName.DEFAULT
        # it can be stanalone client so we use check by realm
        is_lesta_client = self.realm in ClientRealm.LESTA_REALMS
        if is_lesta_client and is_semver_version(self.client_version):
            is_replay_ext_renamed = Version(self.client_version) >= Version('1.35.0.0')
            if is_replay_ext_renamed:
                self.replay_extension = ClientReplayName.LESTA
        self.replay_extension_mask = f'*.{self.replay_extension}'

    def __read_exe_filename(self):
        exe_filename = ClientExecutableName.DEFAULT
        is_lesta_client = self.realm in ClientRealm.LESTA_REALMS
        if is_lesta_client and is_semver_version(self.client_version):
            is_lesta_alpha = Version(self.client_version) >= Version('1.32.0.0')
            if is_lesta_alpha:
                exe_filename = ClientExecutableName.LESTA
        exe_filepath = os.path.normpath(os.path.join(self.path, exe_filename))
        self.is_valid &= os.path.isfile(exe_filepath)
        if self.is_valid:
            self.exe_filename = exe_filename

    def __read_exe_version(self):
        # NotImplemented
        pass

    def __read_pdc_state(self):
        if self.realm in ClientRealm.LESTA_REALMS:
            return
        self.is_pdc_supported = True
        if is_semver_version(self.client_version):
            self.is_pdc_supported = Version(self.client_version) >= Version('1.27.1.0')
        if not self.is_pdc_supported:
            return
        self.pdc_path = os.path.normpath(os.path.join(self.path, 'data.wgpdc'))
        self.is_pdc_exists = os.path.isfile(self.pdc_path)

    def __invalidate(self):
        self.branch = ClientBranch.UNKNOWN
        self.l10n = None
        self.path_mods = None
        self.path_resmods = None
        self.mod_extension = None
        self.mod_extension_mask = None
        self.replay_extension = None
        self.replay_extension_mask = None
        self.realm = None
        self.type = ClientType.UNKNOWN
        self.client_version = None
        self.full_client_version = None
        self.exe_filename = None
        self.exe_version = None
        self.is_pdc_supported = False
        self.is_pdc_exists = False
        self.pdc_path = None
        self.is_valid = False

    def __repr__(self):
        return (f'<Client branch={self.branch} launcherFlavour={self.launcher_flavour} l10n={self.l10n} path={self.path} pathMods={self.path_mods} pathResmods={self.path_resmods} realm={self.realm} type={self.type} clientVersion={self.client_version} exeVersion={self.exe_version} isPreffered={self.is_preffered}>')
