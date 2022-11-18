import logging
import time
from instagram_selenium_crawler import Client, InstagramCommonCrawler, InstagramPostCrawler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

code = '###target_post_code###'
login_account_id = '###instagram_login_id###'
login_account_pw = '###instagram_login_pw###'
filename = fr'{int(time.time())}_{code}.json'

client = Client(headless=False)

try:
    login = InstagramCommonCrawler(client=client, logger=logger).login(login_account_id, login_account_pw)

    if login:
        post = InstagramPostCrawler(client)
        post_json = post.get_post_bycode(code)

        with open(filename, 'w', newline='') as f:
            f.write(post_json)

    client.driver_quit()

except Exception as e:
    logger.exception(f"Failed to function {e}")
    client.driver_quit()
