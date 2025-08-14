from logikal_utils.download import download
from logikal_utils.path import move, tmp_path, unzip
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

from logikal_browser import BrowserVersion
from logikal_browser.chromium import ChromiumBrowser


class ChromeVersion(BrowserVersion):
    name = 'chrome'

    def install(self) -> None:
        root = f'https://storage.googleapis.com/chrome-for-testing-public/{self.version}/linux64'

        if not self.path.exists():
            self.print(f'Installing Google Chrome {self.version}')
            tmp = tmp_path('logikal_browser', suffix=self.name)
            unzip(download(f'{root}/chrome-linux64.zip', tmp / 'chrome.zip'))
            move(tmp / 'chrome/chrome-linux64', self.path.parent)

        if not self.driver_path.exists():
            self.print(f'Installing Google Chrome WebDriver {self.driver_version}')
            tmp = tmp_path('logikal_browser', suffix=self.driver_name)
            unzip(download(f'{root}/chromedriver-linux64.zip', tmp / 'chromedriver.zip'))
            move(tmp / 'chromedriver/chromedriver-linux64', self.driver_path.parent)


class ChromeBrowser(ChromiumBrowser, WebDriver):
    """
    Google Chrome WebDriver.
    """
    version_class = ChromeVersion
    options_class = Options
    service_class = Service

    # See https://github.com/SeleniumHQ/selenium/issues/14660
    height_offset = 87
