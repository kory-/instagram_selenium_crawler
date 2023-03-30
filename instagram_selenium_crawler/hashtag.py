import json
import time
from logging import getLogger
from .helpers import response_log_body, response_log, response_and_request_log
import requests as requests

def convert_pk_from_code(code):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    pk = 0
    for s in code:
        pk = pk * 64 + alphabet.find(s)
    return pk


class InstagramHashtagCrawler:
    INSTAGRAM_BASE_URL = "https://www.instagram.com/"

    def __init__(self, client, logger=None):
        self.logger = getLogger(__name__) if logger is None else logger
        self.client = client
        self.driver = client.driver
        self.cookies = None
        self.headers = None

    def get_hashtag(self, hashtag):
        url = self.INSTAGRAM_BASE_URL + f'explore/tags/{hashtag}/'
        self.driver.get(url)

    def _get_hashtag_first_log(self):
        return response_and_request_log(self.driver, r'https://www.instagram.com/api/v1/tags/web_info/')

    def _get_hashtag_api_log(self, code):
        pk = convert_pk_from_code(code)
        return response_log(self.driver, rf'https?://www.instagram.com/api/v1/media/{pk}/info/')

    def _get_hashtag_posts_from_api(self, hashtag, next_max_id, next_media_ids, next_page):
        url = f'https://www.instagram.com/api/v1/tags/{hashtag}/sections/'

        data = {
            'include_persistent': '0',
            'max_id': next_max_id,
            'next_media_ids[]': next_media_ids,
            'page': next_page,
            'surface': 'grid',
            'tab': 'recent'
        }

        self.logger.info(url)
        response = requests.post(
            url,
            headers=self.headers,
            cookies=self.cookies,
            data=data
        )

        return json.dumps(response.json())

    def get_hashtag_posts(self, hashtag, next_max_id=None, next_media_ids=None, next_page=None):
        self.logger.info(f"{hashtag} 's post crawl start")

        if self.cookies is None:
            self.get_hashtag(hashtag)

            time.sleep(3)

            self.cookies = {
                cookie['name']: cookie['value']
                for cookie in self.driver.get_cookies()
            }

            _response_log, _request_log = self._get_hashtag_first_log()

            if _response_log is None:
                raise Exception(f'rate limit account')

            status = _response_log['params']['response']['status']
            status_text = _response_log['params']['response']['statusText']
            request_id = _response_log["params"]["requestId"]

            if status != 200:
                raise Exception(f'status_code: {status} reason: {status_text}')

            self.headers = _request_log['params']['request']['headers']
            body = response_log_body(self.driver, request_id)


        if next_max_id:
            body = self._get_hashtag_posts_from_api(hashtag, next_max_id, next_media_ids, next_page)

        self.logger.info(f"{hashtag} 's post crawl end")

        return body
