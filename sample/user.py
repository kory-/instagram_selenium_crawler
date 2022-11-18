import logging
import time
from instagram_selenium_crawler import Client, InstagramCommonCrawler, InstagramUserCrawler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

account_id = '###target_account_id###'
login_account_id = '###instagram_login_id###'
login_account_pw = '###instagram_login_pw###'
filename = fr'{int(time.time())}_{account_id}.json'

client = Client(headless=False)

try:
    login = InstagramCommonCrawler(client=client, logger=logger).login(login_account_id, login_account_pw)

    if login:
        user = InstagramUserCrawler(client)
        user_json = user.get_user_by_account_id(account_id)

        with open(filename, 'w', newline='') as f:
            f.write(user_json)

    client.driver_quit()

except Exception as e:
    logger.exception(f"Failed to function {e}")
    client.driver_quit()
