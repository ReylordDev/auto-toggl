import json
from .window import Window
from .windowsUtils import mozlz4_to_text
import os
from tldextract import extract
import logging

with open("projects.json", "r") as f:
    project_objs: list = json.load(f)
project_to_id = {project["alias"]: project["id"] for project in project_objs}

logger = logging.getLogger()

entertainment_list = [
    ("YouTube", "https://www.youtube.com"),
    ("Reddit", "https://www.reddit.com"),
    ("Twitter", "https://x.com"),
    ("Twitch", "https://www.twitch.tv"),
    ("Wookieepedia", "https://starwars.fandom.com"),
    ("TimeGuessr", "https://timeguessr.com"),
    ("123Movies", "https://ww4.123moviesfree.net"),
    ("Connect-The-Stars", "https://connectthestars.xyz/"),
]

entertainment_tabs = [
    ("Everything GTA RP related!", "Reddit"),
    ("X", "Twitter"),
]

habits_list = [
    ("Duolingo", "https://www.duolingo.com"),
    # ("Monkeytype", "https://monkeytype.com"),
]


class VSCode(Window):
    def __init__(self, handle: int):
        super().__init__(handle)
        title = self.get_title()
        title_parts = title.split(" - ")
        if len(title_parts) < 3:
            self.project_name = "No Project"
        else:
            self.project_name = title_parts[1]
        if len(title_parts) < 2:
            self.file_name = "No Tab"
        else:
            self.file_name = title_parts[0]
        self._priority = 5

    def __str__(self):
        return f"VSCode(Active-Tab: {self.file_name}, Project: {self.project_name}, Foreground: {self.is_active()}, Audio: {self.is_playing_audio()})"

    def __repr__(self):
        return f"VSCode({self.repr_content()}, project='{self.project_name}', file='{self.file_name}')"

    def llm_repr(self):
        return f'{self._active_window_prefix()}VisualStudioCode:{{Code-Project:"{self.get_project_name()}",File:"{self.get_file_name()}"}}'

    def get_file_name(self):
        title = self.get_title()
        title_parts = title.split(" - ")
        if len(title_parts) < 2:
            return None
        file_name = title_parts[0]
        file_name = file_name.strip("● ")
        return file_name

    def get_project_name(self):
        title = self.get_title()
        title_parts = title.split(" - ")
        if len(title_parts) < 3:
            project_name = None
        else:
            project_name = title_parts[1]
        return project_name

    def get_toggl_description(self):
        project_name = self.get_project_name()
        if not project_name:
            return self.get_file_name()
        return project_name

    def get_toggl_project_id(self):
        id = project_to_id["Coding"]
        return id


class ArcBrowser(Window):
    local_appdata_folder = os.environ.get("LOCALAPPDATA")
    assert local_appdata_folder is not None
    # state_folder = os.path.join(local_appdata_folder, "Arc")
    ARC_PACKAGE_NAME = "TheBrowserCompany.Arc_ttt1ap7aakyb4"
    state_folder = os.path.join(
        local_appdata_folder, "Packages", ARC_PACKAGE_NAME, "LocalCache", "Local", "Arc"
    )
    assert os.path.exists(
        state_folder
    ), f"The Arc state folder path is not correct: {state_folder}"

    def __init__(self, handle: int):
        super().__init__(handle)
        # self._priority = 4

    def __str__(self):
        return f'ArcBrowser(Active-Space: "{self.get_space()}", Active-Tab: "{self.get_tab()}", Foreground: {self.is_active()}, Audio: {self.is_playing_audio()})'

    def __repr__(self):
        return f"ArcBrowser({self.repr_content()}, space='{self.get_space()}', tab='{self.get_tab()}'"

    def llm_repr(self):
        return f'{self._active_window_prefix()}Arc-Browser:{{Space:"{self.get_space()}", Tab:"{self.get_tab()}", Audio:{self.is_playing_audio()}}}'

    def get_title(self):
        return "Arc Browser"

    def get_tab(self):
        windows_config = os.path.join(self.state_folder, "StorableWindows.json")
        sidebar_config = os.path.join(self.state_folder, "StorableSidebar.json")
        with open(windows_config, "r", encoding="utf-8") as f:
            data = f.read()
        data = json.loads(data)
        item_last_active_dates = data["windows"][0]["itemLastActiveDates"]
        item_by_active_date = {}
        for i in range(0, len(item_last_active_dates), 2):
            item_id = item_last_active_dates[i]
            item_last_active_date = item_last_active_dates[i + 1]
            item_by_active_date[item_last_active_date] = item_id
        max_active_date = max(item_by_active_date.keys())
        most_recent_item = item_by_active_date[max_active_date]
        tab_id = most_recent_item
        with open(sidebar_config, "r", encoding="utf-8") as f:
            data = f.read()
        data = json.loads(data)
        for item in data["sidebar"]["containers"][1]["items"]:
            if isinstance(item, str):
                continue
            if item["id"] == tab_id:
                title = item["title"]
                if not title:
                    title = item["data"]["tab"]["savedTitle"]
                return title
        return "No Tab"

    def get_space(self):
        windows_config = os.path.join(self.state_folder, "StorableWindows.json")
        sidebar_config = os.path.join(self.state_folder, "StorableSidebar.json")
        with open(windows_config, "r", encoding="utf-8") as f:
            data = f.read()
        data = json.loads(data)
        space_id = data["windows"][0]["focusedSpaceID"]
        with open(sidebar_config, "r", encoding="utf-8") as f:
            data = f.read()
        data = json.loads(data)
        for space in data["sidebar"]["containers"][1]["spaces"]:
            if isinstance(space, str):
                continue
            if space["id"] == space_id:
                space_name = space["title"]
                return space_name
        return "No Space"

    def get_toggl_description(self):
        return self.get_space()


# Process: Spotify.exe, Title: Spotify Premium, Foreground: False, Audio: False
class Spotify(Window):
    def __init__(self, handle: int):
        super().__init__(handle)
        self._priority = 1

    def is_playing_audio(self):
        title = self.get_title()
        title_parts = title.split(" - ")
        if len(title_parts) < 2:
            return False
        return True

    def __str__(self):
        if self.is_playing_audio():
            return f"Spotify(Track: {self.get_track()}, Artist: {self.get_artist()}, Foreground: {self.is_active()}, Audio: {self.is_playing_audio()})"
        else:
            return f"Spotify(Foreground: {self.is_active()}, No Audio)"

    def __repr__(self):
        return f"Spotify({self.repr_content()}, track='{self.get_track()}', artist='{self.get_artist()}')"

    def llm_repr(self):
        if self.is_playing_audio():
            return f'{self._active_window_prefix()}Spotify:{{Track:"{self.get_track()}", Artist:"{self.get_artist()}", Audio:{self.is_playing_audio()}}}'
        else:
            return f"{self._active_window_prefix()}Spotify:{{Audio:{self.is_playing_audio()}}}"

    def get_track(self):
        if self.is_playing_audio():
            title = self.get_title()
            title_parts = title.split(" - ")
            track = " ".join(title_parts[1:])
            return track
        return "No Track"

    def get_artist(self):
        if self.is_playing_audio():
            title = self.get_title()
            title_parts = title.split(" - ")
            return title_parts[0]
        return "No Artist"


class Firefox(Window):
    PROFILE_NAME = "1doawgbs.default"
    profile_path = os.path.join(
        os.environ["APPDATA"], "Mozilla", "Firefox", "Profiles", PROFILE_NAME
    )

    def __init__(self, handle: int):
        super().__init__(handle)
        self.get_recently_opened_tabs()
        self._priority = 3

    def __str__(self):
        return f'Firefox(Active-Tab: "{self.get_current_tab()}", Foreground: {self.is_active()}, Audio: {self.is_playing_audio()})'

    def __repr__(self):
        return f"Firefox({self.repr_content()}, tab='{self.get_current_tab()}', recent_tabs='{self.get_recently_opened_tabs()}')"

    def llm_repr(self):
        return f'{self._active_window_prefix()}Firefox:{{ActiveTab:"{self.get_current_tab()}", Audio:{self.is_playing_audio()}, RecentTabs:{self.get_recently_opened_tabs()}}}'

    def get_current_tab(self):
        title = self.get_title()
        if " – " not in title:
            return "No Tab"
        title_parts = title.split(" – ")
        tab_title = "".join(title_parts[0:-1])
        if " - " in tab_title:
            tab_title_parts = tab_title.split(" - ")
            website_name = tab_title_parts[-1]
            return website_name
        if " | " in tab_title:
            tab_title_parts = tab_title.split(" | ")
            website_name = tab_title_parts[0]
            return website_name
        if " / " in tab_title:
            tab_title_parts = tab_title.split(" / ")
            website_name = tab_title_parts[-1]
            return website_name
        return tab_title

    def get_recently_opened_tabs(self) -> list[dict[str, str]]:
        # TODO: Blacklist some tabs
        # TODO: Add recency limit (time or quantity based)
        recovery_file = os.path.join(
            self.profile_path, "sessionstore-backups", "recovery.jsonlz4"
        )
        if not os.path.exists(recovery_file):
            logger.info(f"Firefox recovery file not found: {recovery_file}")
            return []
        try:
            session_data = mozlz4_to_text(recovery_file)
        except PermissionError as e:
            logger.info(f"Firefox Permission Error: {e}")
            return []
        except Exception as e:
            logger.info(f"Firefox Error: {e}")
            return []
        session_data = json.loads(session_data)
        tab_names = []
        tab_urls = []
        tabs = []
        for window in session_data["windows"]:
            for tab in window["tabs"]:
                for entry in tab["entries"]:
                    title = entry["title"]
                    url = entry["url"]
                    tld = extract(url)
                    if tld in tab_urls:
                        continue
                    tab_urls.append(tld)
                    tab_names.append(title)
                    tabs.append({"title": title, "url": url})
        return tabs

    def get_type_and_cause(self):
        # TODO: Prioritize based on recency
        recent_tabs = self.get_recently_opened_tabs()
        for entertainment_site in entertainment_list:
            for tab in recent_tabs:
                if entertainment_site[1] in tab["url"]:
                    return "Entertainment", entertainment_site[0]
            if entertainment_site[0] in self.get_current_tab():
                return "Entertainment", entertainment_site[0]

        for habit_site in habits_list:
            for tab in recent_tabs:
                if habit_site[1] in tab["url"]:
                    return "Habits", habit_site[0]
            if habit_site[0] in self.get_current_tab():
                return "Habits", habit_site[0]
        return "Default", None

    def get_priority(self):
        ff_type, cause = self.get_type_and_cause()
        if ff_type == "Entertainment":
            return 7
        if ff_type == "Habits":
            return 4
        return self._priority

    def get_toggl_description(self):
        ff_type, cause = self.get_type_and_cause()
        if cause:
            return cause
        return None

    def get_toggl_project_id(self):
        ff_type, cause = self.get_type_and_cause()
        if ff_type == "Entertainment":
            id = project_to_id["Entertainment"]
            return id
        if ff_type == "Habits":
            id = project_to_id["Habits"]
            return id
        return None


class Notion(Window):
    def __init__(self, handle: int):
        super().__init__(handle)
        self._priority = 4

    def __str__(self):
        return f'Notion(Active-Page: "{self.get_page_title()}", Foreground: {self.is_active()}, Audio: {self.is_playing_audio()})'

    def __repr__(self):
        return f'Notion({self.repr_content()}, page="{self.get_page_title()}")'

    def llm_repr(self):
        return (
            f'{self._active_window_prefix()}Notion:{{Page:"{self.get_page_title()}"}}'
        )

    def get_page_title(self):
        title = self.get_title()
        if title == "<>":
            return "Dashboard"

        return title


class Chrome(Window):
    def __init__(self, handle: int):
        super().__init__(handle)
        self._priority = 3

    def __str__(self):
        return f'Chrome(Active-Tab: "{self.get_current_tab()}", Foreground: {self.is_active()}, Audio: {self.is_playing_audio()})'

    def __repr__(self):
        return f"Chrome({self.repr_content()}, tab='{self.get_current_tab()}')"

    def llm_repr(self):
        return f'{self._active_window_prefix()}Chrome:{{ActiveTab:"{self.get_current_tab()}", Audio:{self.is_playing_audio()}}}'

    def get_current_tab(self):
        title = self.get_title()
        if " - " not in title:
            return "No Tab"
        title_parts = title.split(" - ")
        tab_title = " - ".join(title_parts[0:-1])
        if " - " in tab_title:
            tab_title_parts = tab_title.split(" - ")
            website_name = tab_title_parts[-1]
            return website_name
        if " | " in tab_title:
            tab_title_parts = tab_title.split(" | ")
            website_name = tab_title_parts[0]
            return website_name
        if " / " in tab_title:
            tab_title_parts = tab_title.split(" / ")
            website_name = tab_title_parts[-1]
            return website_name
        if " : " in tab_title:
            tab_title_parts = tab_title.split(" : ")
            website_name = tab_title_parts[-1]
            return website_name
        return tab_title

    def get_type_and_cause(self):
        for entertainment_site in entertainment_list:
            if entertainment_site[0] in self.get_current_tab():
                return "Entertainment", entertainment_site[0]
        for tab in entertainment_tabs:
            if tab[0] == self.get_current_tab():
                return "Entertainment", tab[1]
        if "r/" in self.get_current_tab():
            return "Entertainment", "Reddit"
        return "Default", None

    def get_priority(self):
        ff_type, cause = self.get_type_and_cause()
        if ff_type == "Entertainment":
            return 7
        return self._priority

    def get_toggl_description(self):
        ff_type, cause = self.get_type_and_cause()
        if cause:
            return cause
        return None

    def get_toggl_project_id(self):
        ff_type, cause = self.get_type_and_cause()
        if ff_type == "Entertainment":
            id = project_to_id["Entertainment"]
            return id
        return None


class NvimQT(Window):
    def __init__(self, handle: int):
        super().__init__(handle)
        self._priority = 4

    def __str__(self):
        return f"Journal(Foreground: {self.is_active()})"

    def __repr__(self):
        return f"Journal({self.repr_content()})"

    def llm_repr(self):
        return f"{self._active_window_prefix()}Journal"

    def get_title(self):
        return "Journal"

    def get_toggl_description(self):
        return "Journal"

    def get_toggl_project_id(self):
        id = project_to_id["Habits"]
        return id


class NotionCalendar(Window):
    def __init__(self, handle: int):
        super().__init__(handle)
        self._priority = 1

    def __str__(self):
        return f'NotionCalendar(Title: "{self.get_title()}")'

    def __repr__(self):
        return f"NotionCalendar({self.repr_content()})"

    def llm_repr(self):
        return f'{self._active_window_prefix()}NotionCalendar:{{Title:"{self.get_title()}"}}'

    # May 6 – 12, 2024 · Notion Calendar
    def get_title(self):
        complete_title = super().get_title()
        title_parts = complete_title.split(" · ")
        if len(title_parts) < 2:
            return "No Title"
        title = title_parts[0]
        title = title.replace(" – ", "-").replace(" ", " ")
        return title


class HuntShowdown(Window):
    def __init__(self, handle: int):
        super().__init__(handle)
        self._priority = 10

    def get_toggl_description(self):
        return "Hunt: Showdown"

    def get_toggl_project_id(self):
        id = project_to_id["Gaming"]
        return id
