# pylint: disable=import-outside-toplevel
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path
from sys import stderr
from time import sleep
from typing import Any

from logikal_utils.path import tmp_path
from logikal_utils.testing import hide_traceback
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from termcolor import colored
from xdg_base_dirs import xdg_cache_home

from logikal_browser.config import BROWSER_VERSIONS
from logikal_browser.scenarios import Settings
from logikal_browser.utils import assert_image_equal

logger = logging.getLogger(__name__)


class BrowserVersion(ABC):
    """
    Base class for browser versions.

    Args:
        version: The browser version to use. Defaults to the appropriate version specified in
            :data:`~logikal_browser.config.BROWSER_VERSIONS`.
        install: Whether to install the web browser and the web driver.
        install_path: The path to use for the installation.
            Defaults to ``$XDG_CACHE_HOME/logikal_browser``.

    """
    def __init__(
        self,
        version: str | None = None,
        install: bool = True,
        install_path: Path | None = None,
    ):
        install_path = install_path or (xdg_cache_home() / 'logikal_browser')

        self.version = version or BROWSER_VERSIONS.get(self.name)
        if not self.version:
            raise ValueError(f'The browser version must be specified for "{self.name}"')
        self.path = install_path / self.name / self.version / self.binary_name
        self.driver_path = install_path / self.driver_name / self.version / self.driver_binary_name
        if install:
            self.install()

    def __str__(self) -> str:
        return f'{self.name} ({self.version})'

    def __repr__(self) -> str:
        return (
            f'<{str(self.__class__.__name__)} ({self.version}) at "{self.path}" '
            f'with {self.driver_name} ({self.driver_version}) at "{self.driver_path}">'
        )

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def install(self) -> None:
        ...

    @property
    def binary_name(self) -> str:
        return self.name

    @property
    def driver_name(self) -> str:
        return f'{self.name}driver'

    @property
    def driver_binary_name(self) -> str:
        return self.driver_name

    @property
    def driver_version(self) -> str:
        return self.version

    @staticmethod
    def print(message: str) -> None:
        print(colored(message, 'yellow', attrs=['bold']), file=stderr)


class Browser(ABC, WebDriver):
    """
    Base class for browser-specific web drivers.

    Args:
        settings: The browser settings to use.
        version: The browser version to use.
        headless: Whether to run in headless mode.
        screenshot_path: The path where screenshots are stored.
        screenshot_tmp_path: The temporary path to use for screenshots.
        download_path: The path to use for downloads.

    """
    height_offset = 0  # correction for https://github.com/SeleniumHQ/selenium/issues/14660
    width_offset = 0  # correction for https://github.com/SeleniumHQ/selenium/issues/14660

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        settings: Settings,
        version: BrowserVersion | None = None,
        headless: bool = True,
        screenshot_path: Path = Path('screenshot'),
        screenshot_tmp_path: Path | None = None,
        download_path: Path | None = None,
        **kwargs: Any,
    ):
        self.version = version or self.version_class()
        logger.debug(f'Browser version: {repr(self.version)}')
        self.settings = settings
        logger.debug(f'Browser settings: {self.settings}')
        self.headless = headless
        if self.headless:
            logger.debug('Running in headless mode')
        self.screenshot_path = screenshot_path
        logger.debug(f'Using screenshot path "{self.screenshot_path}/"')
        self.screenshot_tmp_path = (
            screenshot_tmp_path or tmp_path('logikal_browser', suffix='image')
        )
        logger.debug(f'Using screenshot temporary path "{self.screenshot_tmp_path}/"')
        self.download_path = download_path or tmp_path('logikal_browser', suffix='downloads')
        logger.debug(f'Using download path "{self.download_path}/"')

        super().__init__(**{**kwargs, **self.init_args()})

    @abstractmethod
    def init_args(self) -> dict[str, Any]:
        ...

    @property
    @abstractmethod
    def version_class(self) -> type[BrowserVersion]:
        ...

    def _set_settings_window_size(self, height: int | None = None) -> None:
        width = self.settings.width + self.width_offset
        height = (self.settings.height if height is None else height) + self.height_offset
        logger.debug(f'Setting window size to width "{width}" height "{height}"')
        self.set_window_size(width, height)

    @contextmanager
    def auto_height(self, wait_milliseconds: int | None) -> Iterator[None]:
        if not self.settings.full_page_height:
            yield
            return
        logger.debug('Using full page height')
        self._set_settings_window_size()
        if wait_milliseconds:  # we use a small delay to mitigate height flakiness
            logger.debug(f'Waiting {wait_milliseconds} ms')
            sleep(wait_milliseconds / 1000)
        elements = [
            'document.body.clientHeight',
            'document.body.scrollHeight',
            'document.body.offsetHeight',
            'document.documentElement.clientHeight',
            'document.documentElement.scrollHeight',
            'document.documentElement.offsetHeight',
        ]
        script = f'return Math.max({','.join(elements)});'
        height = self.execute_script(script)
        logger.debug(f'Calculated page height: {height}')
        self._set_settings_window_size(height=height)
        try:
            yield
        finally:
            self._set_settings_window_size()

    @hide_traceback
    def check(self, name: str | None = None, wait_milliseconds: int | None = 100) -> None:
        """
        Create a screenshot and check it against an expected version.

        Args:
            name: The name of the check.
            wait_milliseconds: The milliseconds to wait before calculating the screenshot height
                for unlimited height checks.

        """
        name_parts = [self.screenshot_path.name, self.version.name, self.settings.name, name]
        full_name = '_'.join(part for part in name_parts if part is not None)
        expected = self.screenshot_path.with_name(full_name).with_suffix('.png')

        script = 'document.body.style.caretColor = "transparent";'  # hide the blinking caret
        self.execute_script(script)

        with self.auto_height(wait_milliseconds=wait_milliseconds):
            logger.debug('Taking screenshot')
            # Note: we are disabling debug remote logs because they contain the verbose image data
            logging.getLogger('selenium.webdriver.remote').setLevel(logging.INFO)
            actual = self.get_screenshot_as_png()
            logging.getLogger('selenium.webdriver.remote').setLevel(logging.DEBUG)

        assert_image_equal(
            actual=actual,
            expected=expected,
            image_tmp_path=self.screenshot_tmp_path,
        )

    def replace_text(self, element: Any, text: str) -> None:
        """
        Replace the text of an element.

        Args:
            element: The element to use.
            text: The new text value.

        """
        script = f'arguments[0].innerHTML = "{text}";'
        self.execute_script(script, element)

    def wait_for_element(
        self,
        by: str,
        value: str,
        timeout_seconds: int = 10,
        poll_frequency: float = 0.5,
    ) -> None:
        """
        Wait until a given element is present.

        Args:
            by: The selector type to use for locating the element.
            value: The selector value to use for locating the element.
            timeout_seconds: The maximal time to wait.
            poll_frequency: Sleep interval between checks.

        """
        logger.debug(f'Waiting for element "{value}" to be present')
        wait = WebDriverWait(driver=self, timeout=timeout_seconds, poll_frequency=poll_frequency)
        wait.until(expected_conditions.presence_of_element_located((by, value)))

    def wait_for_download(
        self,
        name: str,
        timeout_seconds: int = 60,
        poll_frequency: float = 0.5,
    ) -> None:
        """
        Wait until a file with a given name is downloaded.

        Args:
            name: The name of the file to wait for.
            timeout_seconds: The maximal time to wait.
            poll_frequency: Sleep interval between checks.

        """
        file_path = self.download_path / name
        logger.debug(f'Waiting for file "{file_path}" to download')
        wait = WebDriverWait(driver=self, timeout=timeout_seconds, poll_frequency=poll_frequency)
        wait.until(lambda *_: file_path.exists())

    def login(self, user: Any, force: bool = True) -> None:
        """
        .. note:: The ``django`` extra must be installed for this method to work.

        Log in a given user.

        Args:
            user: The user to log in.
            force: Whether to log the user in without going through the authentication steps.

        """
        try:
            from django.conf import settings
            from django.contrib.auth import login as django_auth_login
            from django.http import HttpRequest
        except ImportError as error:  # pragma: no cover
            raise RuntimeError('The `django` extra must be installed for login to work') from error
        if not force:
            raise NotImplementedError('Only the forced login is implemented currently')

        request = HttpRequest()
        request.session = import_module(settings.SESSION_ENGINE).SessionStore()
        django_auth_login(request, user)
        request.session.save()
        self.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': request.session.session_key,
        })
