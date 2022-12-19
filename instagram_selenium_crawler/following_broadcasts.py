from logging import getLogger
from .helpers import response_log_body, response_log


class InstagramFollowingBroadcastsCrawler:
    INSTAGRAM_BASE_URL = "https://www.instagram.com/"

    def __init__(self, client, logger=None):
        self.logger = getLogger(__name__) if logger is None else logger
        self.client = client
        self.driver = client.driver
        self.code = None

    def _get_following_broadcasts(self):
        return response_log(self.driver, 'https://www.instagram.com/api/v1/live/reels_tray_broadcasts')

    def get_following_broadcasts(self):
        self.logger.info(f"following broadcasts check start")

        response = self._get_following_broadcasts()

        if response is None:
            raise Exception(f'rate limit account')

        status = response['params']['response']['status']
        status_text = response['params']['response']['statusText']
        request_id = response["params"]["requestId"]

        if status != 200:
            raise Exception(f'status_code: {status} reason: {status_text}')

        body = response_log_body(self.driver, request_id)

        self.logger.info(f"following broadcasts check end")

        return body
