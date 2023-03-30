import json
import logging
import os
import time

from instagram_selenium_crawler import Client, InstagramCommonCrawler, InstagramHashtagCrawler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

target_hashtag = '###target_hashtag_without_sharp###'
login_account_id = '###instagram_login_id###'
login_account_pw = '###instagram_login_pw###'

dirname = f'hashtag/{target_hashtag}/'
filename_prefix = f'{int(time.time())}_{target_hashtag}'

os.makedirs(dirname, exist_ok=True)

client = Client(headless=False)

next_max_id = None
next_page = None

# next_max_id="QVFBM21Bam5wdHNjM1V4R1dvMnNxYURONzRmbEdHTm5ucVlrcDc0QnEtS2RMRVN6UlkxTE5TcGtnbDNnN1JqXzlaWVh2RmNzQ1dHUWpLdzg4WnlFVk1mbg=="
# next_media_ids=    [
#         "2714711203075369621",
#         "2714740669070384594"
#     ]
# next_page=1672


def get_hashtag_posts(target_hashtag, next_max_id=None, next_media_ids=None, next_page=None):
    hashtag_json_str = hashtag.get_hashtag_posts(target_hashtag, next_max_id, next_media_ids, next_page)
    filename = f"{dirname}{filename_prefix}_{next_page if next_page else 0}.json"
    print(filename)

    with open(filename, 'w', newline='') as f:
        f.write(hashtag_json_str)

    hashtag_json = json.loads(hashtag_json_str)

    if next_max_id is None:
        next_max_id = hashtag_json['data']['recent']['next_max_id']
        next_page = hashtag_json['data']['recent']['next_page']
        next_media_ids = hashtag_json['data']['recent']['next_media_ids']
    else:
        next_max_id = hashtag_json['next_max_id']
        next_page = hashtag_json['next_page']
        next_media_ids = hashtag_json['next_media_ids']

    return hashtag_json, next_max_id, next_media_ids, next_page


try:
    login = InstagramCommonCrawler(client=client, logger=logger).login(login_account_id, login_account_pw)

    if login:
        hashtag = InstagramHashtagCrawler(client)

        if next_max_id is None:
            hashtag_json, next_max_id, next_media_ids, next_page = get_hashtag_posts(target_hashtag)

        while next_max_id is not None:
            time.sleep(2)

            hashtag_json, next_max_id, next_media_ids, next_page = get_hashtag_posts(target_hashtag, next_max_id,
                                                                                     next_media_ids, next_page)

            logger.info(f"next_max_id: {next_max_id}")

    client.driver_quit()

except Exception as e:
    logger.exception(f"Failed to function {e}")
    client.driver_quit()
