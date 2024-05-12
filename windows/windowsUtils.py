import psutil
from pycaw.pycaw import AudioUtilities
from pycaw.utils import AudioSession
from pycaw.api.endpointvolume import IAudioMeterInformation
import lz4.block


def get_process_name(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.ZombieProcess:
        return "Zombie Process"
    except psutil.NoSuchProcess:
        return "No Such Process"
    except psutil.AccessDenied:
        return "Access Denied"


def is_playing_audio(pid) -> tuple[bool, float]:
    sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.pid == pid:
            audio_meter = session._ctl.QueryInterface(IAudioMeterInformation)
            if audio_meter.GetPeakValue() > 0:
                return True, audio_meter.GetPeakValue()
    return False, 0


def mozlz4_to_text(filepath):
    # Given the path to a "mozlz4", "jsonlz4", "baklz4" etc. file,
    # return the uncompressed text.
    with open(filepath, "rb") as bytestream:
        bytestream.read(8)  # skip past the b"mozLz40\0" header
        valid_bytes = bytestream.read()
    text = lz4.block.decompress(valid_bytes)
    return text
