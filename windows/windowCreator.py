from .specialWindows import (
    ArcBrowser,
    Chrome,
    Firefox,
    Notion,
    Spotify,
    VSCode,
    NvimQT,
    NotionCalendar,
    HuntShowdown,
    EldenRing,
    RocketLeague,
)
from .windowsUtils import get_process_name
from .window import Window
import win32process


def create_window(handle: int):
    _, pid = win32process.GetWindowThreadProcessId(handle)
    process = get_process_name(pid)
    if process == "Code.exe":
        return VSCode(handle)
    elif process == "Arc.exe":
        return ArcBrowser(handle)
    elif process == "Spotify.exe":
        return Spotify(handle)
    elif process == "firefox.exe":
        return Firefox(handle)
    elif process == "Notion.exe":
        return Notion(handle)
    elif process == "chrome.exe":
        return Chrome(handle)
    elif process == "nvim-qt.exe":
        return NvimQT(handle)
    elif process == "Notion Calendar.exe":
        return NotionCalendar(handle)
    elif process == "HuntGame.exe":
        return HuntShowdown(handle)
    elif process == "eldenring.exe":
        return EldenRing(handle)
    elif process == "RocketLeague.exe":
        return RocketLeague(handle)
    else:
        return Window(handle)
