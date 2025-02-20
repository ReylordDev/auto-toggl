# Auto Toggl

This is a python script starts a [Toggl](https://toggl.com/) timer depending on the current user activity. 

Most importantly, it automatically detects "slacking", such as watching YouTube videos, gaming or scrolling through social media, and tracks the time spent on these activities.

The script grabs the current windows, assigns priority values to them, and starts a Toggl timer for the appropriate, pre-defined project based on the highest priority window.

Consecutive entries for the same project are automatically merged into one entry.

Since the entries and projects are highly personalised to my own workflow, this repo may not be useful to others, except as inspiration for their own implementation.
