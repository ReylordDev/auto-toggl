from toggl.tracker import get_time_entries, delete_time_entry


def delete_botched_time_entries():
    time_entries = get_time_entries()

    for time_entry in time_entries:
        if 0 <= time_entry.duration < 60:
            print(f"Deleting time entry: {time_entry}")
            delete_time_entry(time_entry.id)


if __name__ == "__main__":
    delete_botched_time_entries()
