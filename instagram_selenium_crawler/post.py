from logging import getLogger
from .helpers import response_log_body, response_log


def convert_pk_from_code(code):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    pk = 0
    for s in code:
        pk = pk * 64 + alphabet.find(s)
    return pk


class InstagramPostCrawler:
    INSTAGRAM_BASE_URL = "https://www.instagram.com/"

    def __init__(self, client, logger=None):
        self.logger = getLogger(__name__) if logger is None else logger
        self.client = client
        self.driver = client.driver
        self.code = None

    def get_post(self, code):
        url = self.INSTAGRAM_BASE_URL + f'p/{code}/'
        self.driver.get(url)

    def _get_post_log(self, code):
        return response_log(self.driver, rf'https?://www.instagram.com/p/{code}/')

    def _get_post_api_log(self, code):
        pk = convert_pk_from_code(code)
        return response_log(self.driver, rf'https?://www.instagram.com/api/v1/media/{pk}/info/')

    def get_post_bycode(self, code):
        self.logger.info(f"{code} 's post crawl start")

        self.get_post(code)

        response = self._get_post_log(code)

        status = response['params']['response']['status']
        status_text = response['params']['response']['statusText']

        if status != 200:
            raise Exception(f'status_code: {status} reason: {status_text}')

        api_response = self._get_post_api_log(code)

        if api_response is None:
            raise Exception(f'rate limit account')

        status = api_response['params']['response']['status']
        status_text = api_response['params']['response']['statusText']
        request_id = api_response["params"]["requestId"]

        if status != 200:
            raise Exception(f'status_code: {status} reason: {status_text}')

        body = response_log_body(self.driver, request_id)

        self.logger.info(f"{code} 's post crawl end")

        return body
