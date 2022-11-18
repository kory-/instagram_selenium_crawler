import json
import logging
import os
import time

from instagram_selenium_crawler import Client, InstagramCommonCrawler, InstagramFollowerCrawler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

account_id = '###target_account_id###'
login_account_id = '###instagram_login_id###'
login_account_pw = '###instagram_login_pw###'
dirname = f'followers/{account_id}/'
filename_prefix = f'{int(time.time())}_{account_id}'

os.makedirs(dirname, exist_ok=True)

client = Client(headless=False)


def get_follower(account_id, max_id, count):
    follower_json, next_max_id = follower.get_followers_by_api(account_id, max_id)

    with open(f"{dirname}{filename_prefix}_{count}.json", 'w', newline='') as f:
        f.write(follower_json)

    return json.loads(follower_json), next_max_id


try:
    login = InstagramCommonCrawler(client=client, logger=logger).login(login_account_id, login_account_pw)

    if login:
        i = 1
        follower = InstagramFollowerCrawler(client)

        follower_json, next_max_id = get_follower(account_id, None, i)

        while next_max_id is not None:
            time.sleep(2)
            i = i + 1

            follower_json, next_max_id = get_follower(account_id, next_max_id, i)
            logger.info(f"next_max_id: {next_max_id}")

    client.driver_quit()

except Exception as e:
    logger.exception(f"Failed to function {e}")
    client.driver_quit()
