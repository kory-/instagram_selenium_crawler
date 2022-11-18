from logging import getLogger
from .helpers import response_log_body, response_log


class InstagramUserCrawler:
    INSTAGRAM_BASE_URL = "https://www.instagram.com/"

    def __init__(self, client, logger=None):
        self.logger = getLogger(__name__) if logger is None else logger
        self.client = client
        self.driver = client.driver
        self.code = None

    def get_user(self, account_id):
        url = self.INSTAGRAM_BASE_URL + account_id
        self.driver.get(url)

    def _get_user_api_log(self, account_id):
        return response_log(self.driver, rf'https://www.instagram\.com/api/v1/users/web_profile_info/\?username={account_id}')

    def get_user_by_account_id(self, account_id):
        self.logger.info(f"{account_id} 's user crawl start")

        self.get_user(account_id)

        response = self._get_user_api_log(account_id)

        if response is None:
            raise Exception(f'rate limit account')

        status = response['params']['response']['status']
        status_text = response['params']['response']['statusText']
        request_id = response["params"]["requestId"]

        if status != 200:
            raise Exception(f'status_code: {status} reason: {status_text}')

        body = response_log_body(self.driver, request_id)

        self.logger.info(f"{account_id} 's post crawl end")

        return body
