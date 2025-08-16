import collections
from enum import Enum

class LauncherFlavour:
    UNKNOWN, WG, CHINA_360, STEAM, LESTA, STANDALONE = range(6)
    DEFAULT = WG

_LauncherMetadata = collections.namedtuple('LauncherMetadata', ('flavour', 'path', 'pointer', 'executable'))

LAUNCHERS_METADATA = (
    _LauncherMetadata(LauncherFlavour.WG, 'Wargaming.net\\GameCenter', 'data\\wgc_path.dat', 'wgc.exe'),
    _LauncherMetadata(LauncherFlavour.CHINA_360, '360 Wargaming\\GameCenter', 'data\\wgc_path.dat', 'wgc.exe'),
    _LauncherMetadata(LauncherFlavour.STEAM, 'Wargaming.net\\GameCenter for Steam', 'data\\wgc_path.dat', 'wgc.exe'),
    _LauncherMetadata(LauncherFlavour.LESTA, 'Lesta\\GameCenter', 'data\\lgc_path.dat', 'lgc.exe'),
    _LauncherMetadata(LauncherFlavour.STANDALONE, '', '', '')
)

class ClientBranch(Enum):
    UNKNOWN, RELEASE, COMMON_TEST, SUPERTEST, SANDBOX, CLOSED_TEST = range(6)


class ClientExecutableName:
    WG = 'WorldOfTanks.exe'
    LESTA = 'Tanki.exe'
    DEFAULT = WG


class ClientReplayName:
    WG = 'wotreplay'
    LESTA = 'mtreplay'
    DEFAULT = WG


class ClientType(Enum):
    UNKNOWN, SD, HD = range(3)


class ClientRealm:
    EU = 'EU'
    NA = 'NA'
    ASIA = 'ASIA'
    CT = 'CT'
    CN = 'CN'
    RU = 'RU'
    RPT = 'RPT'
    WG_REALMS = (EU, NA, ASIA, CT, CN)
    LESTA_REALMS = (RU, RPT)

CLIENT_REALM_TO_LAUNCHER_FLAVOUR_MAP = {
    ClientRealm.EU: LauncherFlavour.WG,
    ClientRealm.NA: LauncherFlavour.WG,
    ClientRealm.ASIA: LauncherFlavour.WG,
    ClientRealm.CT: LauncherFlavour.WG,
    ClientRealm.CN: LauncherFlavour.CHINA_360,
    ClientRealm.RU: LauncherFlavour.LESTA,
    ClientRealm.RPT: LauncherFlavour.LESTA,
}
