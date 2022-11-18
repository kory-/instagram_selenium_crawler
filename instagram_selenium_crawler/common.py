from logging import getLogger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time


class InstagramCommonCrawler:

    INSTAGRAM_BASE_URL = "https://www.instagram.com/"

    def __init__(self, client, logger=None):
        self.logger = getLogger(__name__) if logger is None else logger
        self.client = client
        self.driver = client.driver

    def login(self, id, password):
        self.logger.info(f"crawler account login start")
        login_url = self.INSTAGRAM_BASE_URL  # + 'accounts/login'
        self.driver.get(login_url)

        input_id = WebDriverWait(self.driver, timeout=30).until(lambda d: d.find_element(by=By.NAME, value="username"))
        input_pw = WebDriverWait(self.driver, timeout=30).until(lambda d: d.find_element(by=By.NAME, value="password"))

        input_id.send_keys(id)
        input_pw.send_keys(password)

        time.sleep(3)

        button_login = WebDriverWait(self.driver, timeout=30).until(
            lambda d: d.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/button')
        )

        time.sleep(1)
        button_login.click()
        time.sleep(10)

        if self.driver.current_url == self.INSTAGRAM_BASE_URL \
                or self.driver.current_url == self.INSTAGRAM_BASE_URL + 'accounts/onetap/?next=%2F' \
                or self.driver.current_url == self.INSTAGRAM_BASE_URL + '#reactivated':
            self.logger.info(f"crawler account login success")
            return True
        else:
            return False

