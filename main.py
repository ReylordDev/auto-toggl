from windows import get_windows


def main():
    windows = get_windows()
    for window in windows:
        print(window)


if __name__ == "__main__":
    main()
