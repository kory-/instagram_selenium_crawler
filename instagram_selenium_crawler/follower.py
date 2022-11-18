import json
import re
import time
import urllib.parse
from logging import getLogger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import requests as requests
from .helpers import response_log_body, response_and_request_log
from .user import InstagramUserCrawler


def _get_followers_json_link(account_id, count, after=None):
    follower_url = 'https://www.instagram.com/graphql/query/?query_id=17851374694183129&id={}&first={}'.format(
        urllib.parse.quote(account_id),
        count
    )

    if after:
        follower_url = follower_url + '&after={}'.format(urllib.parse.quote(after))

    return follower_url


class InstagramFollowerCrawler:
    INSTAGRAM_BASE_URL = "https://www.instagram.com/"

    def __init__(self, client, logger=None):
        self.logger = getLogger(__name__) if logger is None else logger
        self.client = client
        self.driver = client.driver
        self.cookies = None
        self.headers = None
        self.pk = None
        self.big_list = None


    def _get_follower_api_log(self):
        return response_and_request_log(self.driver,
                                        r'https?://www.instagram.com/api/v1/friendships/([\d]+)/followers/')

    def _get_user_pk_from_follower_api_log(self, log):
        match = re.findall(r'https?://www.instagram.com/api/v1/friendships/(\d+)/followers/',
                           log["params"]["response"]["url"])
        return match[0]

    def get_followers_by_api(self, account_id, max_id=None):
        self.logger.info(f"{account_id} 's follower crawl start")

        if self.pk is None:
            self.set_follower_config(account_id)

        if self.big_list:
            follower_response, next_max_id = self._get_followers_from_api(100, max_id)
        else:
            follower_response, next_max_id = self._get_followers_from_json(50, max_id)

        return follower_response, next_max_id

    def set_follower_config(self, account_id):
        InstagramUserCrawler(self.client).get_user(account_id)

        follower_button = WebDriverWait(self.driver, timeout=30).until(
            lambda d: d.find_element(by=By.XPATH, value="//a[contains(@href, '/followers')]"))

        follower_button.click()

        time.sleep(3)

        self.cookies = {
            cookie['name']: cookie['value']
            for cookie in self.driver.get_cookies()
        }
        _response_log, _request_log = self._get_follower_api_log()

        if _response_log is None:
            raise Exception(f'rate limit account')

        status = _response_log['params']['response']['status']
        status_text = _response_log['params']['response']['statusText']
        request_id = _response_log["params"]["requestId"]

        if status != 200:
            raise Exception(f'status_code: {status} reason: {status_text}')

        self.headers = _request_log['params']['request']['headers']
        self.pk = self._get_user_pk_from_follower_api_log(_response_log)

        body = response_log_body(self.driver, request_id)
        first_followers = json.loads(body)

        self.big_list = first_followers['big_list'] if 'big_list' in first_followers else None

        if self.big_list is None:
            self.pk = None
            raise Exception(f'rate limit account')

    def _get_followers_from_api(self, limit, next_max_id):
        url = f'https://www.instagram.com/api/v1/friendships/{self.pk}/followers/?count={limit}&search_surface=follow_list_page'
        if next_max_id:
            url = url + f'&max_id={next_max_id}'

        self.logger.info(url)
        response = requests.get(
            url,
            headers=self.headers,
            cookies=self.cookies)

        response_json = response.json()
        next_max_id = response_json['next_max_id'] if 'next_max_id' in response_json else None

        return json.dumps(response.json()), next_max_id

    def _get_followers_from_json(self, limit=50, next_max_id=None):
        url = _get_followers_json_link(self.pk, limit, next_max_id)

        self.logger.info(url)
        response = requests.get(
            url,
            headers=self.headers,
            cookies=self.cookies)
        response_json = response.json()
        next_max_id = None
        if response_json.get('data', {}).get('user', {}).get('edge_followed_by', {}).get('page_info', {}).get(
                'has_next_page', False):
            next_max_id = response_json.get('data').get('user').get('edge_followed_by').get('page_info').get(
                'end_cursor', None)

        return json.dumps(response.json()), next_max_id
