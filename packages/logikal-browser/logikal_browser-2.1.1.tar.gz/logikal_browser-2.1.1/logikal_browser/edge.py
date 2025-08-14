from subprocess import run

from logikal_utils.download import download
from logikal_utils.path import move, tmp_path, unzip
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver

from logikal_browser import BrowserVersion
from logikal_browser.chromium import ChromiumBrowser


class EdgeVersion(BrowserVersion):
    name = 'edge'
    binary_name = 'microsoft-edge'
    driver_binary_name = 'msedgedriver'

    def install(self) -> None:
        if not self.path.exists():
            self.print(f'Installing Microsoft Edge {self.version}')
            root = 'https://packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable'
            url = f'{root}/microsoft-edge-stable_{self.version}-1_amd64.deb'
            tmp = tmp_path('logikal_browser', suffix=self.name)
            package = download(url, tmp / 'edge.deb')
            run(['dpkg', '-x', str(package), str(tmp / 'edge')], check=True)  # nosec
            move(tmp / 'edge/opt/microsoft/msedge', self.path.parent)

        if not self.driver_path.exists():
            self.print(f'Installing Microsoft Edge WebDriver {self.driver_version}')
            url = f'https://msedgedriver.microsoft.com/{self.version}/edgedriver_linux64.zip'
            tmp = tmp_path('logikal_browser', suffix=self.driver_name)
            unzip(download(url, tmp / 'edgedriver.zip'))
            move(tmp / 'edgedriver', self.driver_path.parent)


class EdgeBrowser(ChromiumBrowser, WebDriver):
    """
    Microsoft Edge WebDriver.
    """
    version_class = EdgeVersion
    options_class = Options
    service_class = Service

    # See https://github.com/SeleniumHQ/selenium/issues/14660
    height_offset = 78
    width_offset = 8
