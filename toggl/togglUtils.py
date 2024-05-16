from requests import Response
import logging

logger = logging.getLogger()


def handleRequestErrors(response: Response):
    status_code = response.status_code
    if status_code == 504:
        logger.error(f"504: Gateway Timeout: {response.text}")
        return
    logger.error(f"Request Unexpectedly failed: {response.reason}")
    raise Exception("TogglRequest failed")
