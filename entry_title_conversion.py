from toggl import get_time_entries, update_time_entry
from datetime import date
from loguru import logger
import argparse

logger.add("entry_title_conversion.log", rotation="10 MB")


def get_all_entries():
    today = date.today()

    start = today.replace(month=today.month - 1)
    end = today

    entries = get_time_entries(
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d")
    )

    start = today.replace(month=today.month - 2)
    end = today.replace(month=today.month - 1)

    entries += get_time_entries(
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d")
    )

    start = today.replace(month=today.month - 3)
    end = today.replace(month=today.month - 2)

    entries += get_time_entries(
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d")
    )

    logger.info(f"Found {len(entries)} entries")
    return entries


def main():
    parser = argparse.ArgumentParser(description="Entry Title Conversion")
    parser.add_argument("old_title", type=str, help="Title to replace")
    parser.add_argument("new_title", type=str, help="Replacing title")
    args = parser.parse_args()
    entries = get_all_entries()
    unique_names = set()
    for entry in entries:
        unique_names.add(entry.description)
        if entry.description == args.old_title:
            logger.info(f"Updating entry {entry.id}")
            update_time_entry(entry.id, {"description": args.new_title})

    for name in unique_names:
        print(name)


if __name__ == "__main__":
    main()
