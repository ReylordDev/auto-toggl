from windows import get_windows
from toggl import get_projects
from pprint import pprint


def main():
    windows = get_windows()
    for window in windows:
        print(window.__repr__())
    max_prio_window = max(windows, key=lambda x: x.priority)
    projects = get_projects()
    for project in projects:
        print(project)


if __name__ == "__main__":
    main()
