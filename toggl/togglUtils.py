from requests import Response
from requests.exceptions import Timeout
import logging

logger = logging.getLogger()


def handleRequestErrors(response: Response):
    status_code = response.status_code
    print(status_code)
    if status_code == 504:
        logger.error(f"504: Gateway Timeout: {response.text}")
        raise Timeout("Gateway Timeout")
    logger.error(f"Request Unexpectedly failed: {response.reason}")
    raise Exception("TogglRequest failed")
