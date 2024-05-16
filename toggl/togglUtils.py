from requests import Response
import logging
import time

logger = logging.getLogger()


def handleRequestErrors(response: Response):
    status_code = response.status_code
    if status_code == 504:
        logger.error(f"504: Timeout: {response.text}")
        time.sleep(5)
        return
    logger.error(f"Request Unexpectedly failed: {response.reason}")
    raise Exception("TogglRequest failed")
