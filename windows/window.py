import win32gui
import win32process

from .windowsUtils import get_process_name, is_playing_audio
from .ignoredWindows import ignored_window_titles, ignored_processes


class Window:
    def __init__(self, handle: int):
        self.handle = handle
        _, self._pid = win32process.GetWindowThreadProcessId(handle)
        self.process = get_process_name(self._pid)

    # No idea why I'm setting some properties as private

    def __str__(self):
        return f"Process: {self.process}, Title: {self.get_title()}, Audio: {self.is_playing_audio()}"

    def __repr__(self):
        return f"Window({self.repr_content()})"

    def repr_content(self):
        return f"handle={self.handle}, process='{self.process}', title='{self.get_title()}', visible={self.is_visible()}, active={self.is_active()}, audio={self.is_playing_audio()}, placement={self.get_placement()}"

    def llm_repr(self):
        return f'{self._active_window_prefix()}Window:{{Title:"{self.get_title()}", Process:"{self.process}", Audio:{self.is_playing_audio()}}}'

    def get_title(self):
        return win32gui.GetWindowText(self.handle)

    def is_visible(self):
        return win32gui.IsWindowVisible(self.handle)

    def is_active(self):
        return win32gui.GetForegroundWindow() == self.handle

    def is_playing_audio(self):
        val, _ = is_playing_audio(self._pid)
        return val

    def get_placement(self):
        placement = win32gui.GetWindowPlacement(self.handle)
        return placement

    def is_watcher_relevant(self):
        return (
            self.get_title()
            and self.is_visible()
            and self.process not in ignored_processes
            and self.get_title() not in ignored_window_titles
        )

    def _active_window_prefix(self):
        if self.is_active():
            return "(Active) "
        return ""
