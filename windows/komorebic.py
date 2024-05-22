import subprocess
import json
from .windowCreator import create_window, Window
import win32gui
import win32con
from pywintypes import error


def get_komorebic_state():
    output = subprocess.run(["komorebic.exe", "state"], capture_output=True)
    komorebic_str = output.stdout.decode("utf-8")
    state = json.loads(komorebic_str)
    return state


def get_current_workspace_windows() -> list[Window]:
    state = get_komorebic_state()
    # print(f"Monitor Focus: {state['monitors']['focused']}")
    workspaces = state["monitors"]["elements"][0]["workspaces"]["elements"]
    current_workspace_windows = []
    active_workspace = None
    for workspace in workspaces:
        name = workspace["name"]
        focused = workspace["containers"]["focused"]
        # print(f"Workspace: {name}, Focused: {focused}")
        if not focused:
            # print(workspace["containers"])
            continue
        active_workspace = name
        containers = workspace["containers"]["elements"]
        for container in containers:
            stack = container["windows"]["elements"]
            for window_state in stack:
                handle = window_state["hwnd"]
                window = create_window(handle)
                current_workspace_windows.append(window)
        floating_windows = workspace["floating_windows"]
        for floating_window in floating_windows:
            handle = floating_window["hwnd"]
            window = create_window(handle)
            current_workspace_windows.append(window)
    # print(f"Active Workspace: {active_workspace}")
    if not active_workspace:
        print("No active workspace")
    return current_workspace_windows


def get_partial_visible_windows() -> list[dict[str, str]]:
    output = subprocess.run(["komorebic.exe", "visible-windows"], capture_output=True)
    if not output.stdout:
        raise Exception("No output from komorebic")
    komorebic_str = output.stdout.decode("utf-8")
    windows_state = json.loads(komorebic_str)
    monitor = windows_state.keys().__iter__().__next__()
    # TODO: Add support for multiple monitors
    return windows_state[monitor]


def get_all_windows():
    window_handles = []
    win32gui.EnumWindows(lambda hwnd, _: window_handles.append(hwnd), None)
    windows = [
        create_window(handle)
        for handle in window_handles
        if win32gui.IsWindowVisible(handle)
    ]
    return windows


def get_full_visible_windows() -> list[Window]:
    all_windows = get_windows_by_z_index()
    try:
        partial_visible_windows = get_partial_visible_windows()
    except Exception as e:
        # Komorebic is not running
        return [
            window
            for window in all_windows
            if window.is_visible() and window.is_watcher_relevant()
        ]
    visible_windows = []
    for partial_window in partial_visible_windows:
        process = partial_window["exe"]
        title = partial_window["title"]
        for window in all_windows:
            if window.process == process and window.get_title() == title:
                visible_windows.append(window)
                break
    return visible_windows


def get_windows_by_z_index():
    top_handle = win32gui.GetTopWindow(win32gui.GetDesktopWindow())
    iterator_handle = top_handle
    windows = []
    while iterator_handle:
        window = create_window(iterator_handle)
        windows.append(window)

        try:
            iterator_handle = win32gui.GetWindow(iterator_handle, win32con.GW_HWNDNEXT)
        except error:
            print("Error getting next window")
            print(error)
            break
    return windows
