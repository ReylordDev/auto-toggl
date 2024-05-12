from windows import get_windows


def main():
    windows = get_windows()
    for window in windows:
        print(window.__repr__())


if __name__ == "__main__":
    main()
