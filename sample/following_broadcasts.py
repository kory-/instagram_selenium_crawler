import logging
import os
import time
import json
import requests

from instagram_selenium_crawler import Client, InstagramCommonCrawler, InstagramFollowingBroadcastsCrawler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename="info.log")
logger.addHandler(handler)

login_account_id = '###instagram_login_id###'
login_account_pw = '###instagram_login_pw###'

client = Client(headless=False)

def get_following_broadcasts_result(client, logger, login_account_id, login_account_pw):

    login = InstagramCommonCrawler(client=client, logger=logger).login(login_account_id, login_account_pw)
    os.makedirs('live_jsons', exist_ok=True)

    if login:
        following_broadcasts = InstagramFollowingBroadcastsCrawler(client)
        following_broadcasts.driver.get(following_broadcasts.INSTAGRAM_BASE_URL)
        while True:
            user_json = following_broadcasts.get_following_broadcasts()

            print(time.time(), user_json)
            logger.info('time:{}, json:{}'.format(time.time(), user_json))

            if user_json and len(json.loads(user_json)['broadcasts']) > 0:
                with open(fr'live_jsons/{int(time.time())}.json', 'w', newline='') as f:
                    f.write(user_json)

                for broadcast in json.loads(user_json)['broadcasts']:
                    response = requests.get(broadcast['cover_frame_url'])
                    image = response.content

                    os.makedirs(broadcast['id'], exist_ok=True)
                    with open('{}/{}.jpg'.format(broadcast['id'], int(time.time())), "wb") as fi:
                        fi.write(image)

            time.sleep(60)
            following_broadcasts.driver.refresh()

    client.driver_quit()


try:
    get_following_broadcasts_result(client, logger, login_account_id, login_account_pw)
except RecursionError as e:
    logger.exception(f"Failed to function {e}")
    client.driver_quit()
    get_following_broadcasts_result(client, logger, login_account_id, login_account_pw)
except Exception as e:
    logger.exception(f"Failed to function {e}")
    client.driver_quit()
    get_following_broadcasts_result(client, logger, login_account_id, login_account_pw)
