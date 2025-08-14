import os
from abc import abstractmethod
from typing import Any

from logikal_utils.random import DEFAULT_RANDOM_SEED
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.service import ChromiumService

from logikal_browser import Browser


class ChromiumBrowser(Browser):
    """
    Abstract base class for Chromium-based WebDriver classes.
    """
    @property
    @abstractmethod
    def options_class(self) -> type[ChromiumOptions]:
        ...

    @property
    @abstractmethod
    def service_class(self) -> type[ChromiumService]:
        ...

    # See https://www.selenium.dev/documentation/webdriver/browsers/chrome/#options
    # See https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
    def init_args(self) -> dict[str, Any]:
        window_width = self.settings.width + self.width_offset
        window_height = self.settings.height + self.height_offset
        args = [
            '--new-window',
            '--window-position=0,0',
            f'--window-size={window_width},{window_height}',
            # Unwanted features
            '--enable-automation',
            '--no-experiments',
            '--disable-infobars',
            '--disable-breakpad',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-component-extensions-with-background-pages',
            '--disable-features=InterestFeedContentSuggestions,Translate',
            '--no-default-browser-check',
            '--no-first-run',
            '--ash-no-nudges',
            '--disable-search-engine-choice-screen',
            '--propagate-iph-for-testing',
            # Deterministic rendering (see https://issues.chromium.org/issues/40039960#comment29)
            '--disable-partial-raster',
            '--disable-skia-runtime-opts',
            '--force-color-profile=srgb',
            f'--js-flags=--random-seed={DEFAULT_RANDOM_SEED}',
        ]
        if os.getenv('DOCKER_RUN') == '1':  # pragma: no cover
            args += ['--no-sandbox']
        if self.headless:
            args += [
                '--headless=new',
                '--in-process-gpu',  # memory saving
                '--mute-audio',
                '--allow-pre-commit-input',  # see https://issuetracker.google.com/issues/172339334
                '--deterministic-mode',
            ]

        options = self.options_class()
        options.binary_location = str(self.version.path)
        preferences = {'download.default_directory': str(self.download_path)}
        options.add_experimental_option('prefs', preferences)
        if self.settings.mobile:
            args.append('--hide-scrollbars')
        for arg in args:
            options.add_argument(arg)

        service = self.service_class(executable_path=str(self.version.driver_path))

        return {'options': options, 'service': service}
