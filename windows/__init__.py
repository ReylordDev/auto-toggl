from .komorebic import get_full_visible_windows
from .windowCreator import create_window
import win32gui
import win32con
from .window import Window
from loguru import logger


# Legacy
def get_windows():
    visible_windows = get_full_visible_windows()
    windows = [window for window in visible_windows if window.is_watcher_relevant()]
    windows.sort(key=lambda window: window.is_active(), reverse=True)
    return windows


def get_windows_by_z_index():
    top_handle = win32gui.GetTopWindow(win32gui.GetDesktopWindow())
    iterator_handle = top_handle
    visible_windows = []
    while iterator_handle:
        window = create_window(iterator_handle)
        visible_windows.append(window)

        try:
            iterator_handle = win32gui.GetWindow(iterator_handle, win32con.GW_HWNDNEXT)
        except Exception as e:
            logger.error(f"Error: {e}")
            break
    windows = [window for window in visible_windows if window.is_watcher_relevant()]
    windows.sort(key=lambda window: window.is_active(), reverse=True)
    return windows


def get_active_window() -> Window:
    handle = win32gui.GetForegroundWindow()
    window = create_window(handle)
    return window
