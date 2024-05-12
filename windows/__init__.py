from .komorebic import get_full_visible_windows
from .windowCreator import create_window
import win32gui
from .window import Window


def get_windows():
    visible_windows = get_full_visible_windows()
    windows = [window for window in visible_windows if window.is_watcher_relevant()]
    windows.sort(key=lambda window: window.is_active(), reverse=True)
    return windows


def get_active_window() -> Window:
    handle = win32gui.GetForegroundWindow()
    window = create_window(handle)
    return window
