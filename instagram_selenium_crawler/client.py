import time
from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Client:

    def __init__(self, headless=True):
        self.headless = headless
        self.driver = self.get_driver(headless)

    def get_driver(self, headless):
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1980x1030")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        driver = webdriver.Chrome(options=options, desired_capabilities=capabilities)

        return driver

    def driver_quit(self):
        time.sleep(1)
        self.driver.quit()
