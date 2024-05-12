from windows.window import Window
from windows.specialWindows import VSCode

project_ids = [
    202546216,  # Coding
    197977483,  # Entertainment
    198251740,  # Focused Work
    198130090,  # Gaming
    197970542,  # Habits
]


def window_to_project(window: Window):
    if isinstance(window, VSCode):
        return project_ids[0]
    # TODO: continue
    pass
