from loguru import logger
from .specialWindows import (
    ArcBrowser,
    Chrome,
    Firefox,
    Game,
    Notion,
    Spotify,
    VSCode,
    NotionCalendar,
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
    elif process == "Notion Calendar.exe":
        return NotionCalendar(handle)
    elif process == "HuntGame.exe":
        return Game(handle, "Hunt: Showdown")
    elif process == "eldenring.exe" or process == "ersc_launcher.exe":
        return Game(handle, "Elden Ring")
    elif process == "RocketLeague.exe":
        return Game(handle, "Rocket League")
    elif process == "Stardew Valley.exe":
        return Game(handle, "Stardew Valley")
    elif process == "Disco Elysium.exe":
        return Game(handle, "Disco Elysium")
    else:
        return Window(handle)
