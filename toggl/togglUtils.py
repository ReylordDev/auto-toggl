from requests import Response
from loguru import logger


class GatewayTimeout(Exception):
    pass


class BadGateway(Exception):
    pass


def handleRequestErrors(response: Response):
    """
    Handle request errors and raise appropriate exceptions.

    Args:
        response (Response): The response object from the request.

    Raises:
        GatewayTimeout: Raised when the status code is 504.
        BadGateway: Raised when the status code is 502.
        Exception: Raised when the status code is unexpected.
    """
    status_code = response.status_code
    if status_code == 504:
        logger.error(f"504: Gateway Timeout: {response.text}")
        raise GatewayTimeout("TogglRequest failed")
    elif status_code == 502:
        logger.error(f"502: Bad Gateway: {response.text}")
        raise BadGateway("TogglRequest failed")
    elif status_code == 409:
        logger.error(f"409: Conflict: {response.text}")
        return
    else:
        logger.error(
            f"Request Unexpectedly failed: {response.reason}, {response.text}, {response.status_code}"
        )
        raise Exception("TogglRequest failed")
