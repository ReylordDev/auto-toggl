from toggl.tracker import get_time_entries, delete_time_entry
from loguru import logger


def delete_botched_time_entries():
    """
    Deletes all botched time entries from the last 3 months. Botched time entries are time entries that have a duration less than 60 seconds.
    """
    time_entries = get_time_entries()
    logger.debug(f"Found {len(time_entries)} botched time entries.")

    for time_entry in time_entries:
        if 0 <= time_entry.duration < 60:
            logger.debug(f"Deleting time entry: {time_entry.id}")
            delete_time_entry(time_entry.id)


if __name__ == "__main__":
    delete_botched_time_entries()
