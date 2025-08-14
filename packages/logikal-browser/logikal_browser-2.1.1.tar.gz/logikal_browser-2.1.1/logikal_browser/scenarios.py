from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Browser settings specification.

    Args:
        name: Name of the settings.
        width: Browser window width.
        height: Browser window height.
        full_page_height: Whether to use the full page height for screenshots.
        mobile: Whether it is a mobile browser.

    """
    name: str
    width: int
    height: int
    full_page_height: bool = True
    mobile: bool = False


@dataclass
class Scenario:
    """
    Browser scenario specification.

    Args:
        settings: Settings to use.
        browsers: Browsers to use. Defaults to using all configured browser versions.

    """
    settings: Settings | Iterable[Settings]
    browsers: Iterable[str] | None = None


@dataclass
class StandardScenario(Scenario):
    """
    Standard browser scenario specification.
    """
    settings: Settings


desktop_4k = StandardScenario(Settings('desktop_4k', width=2560, height=1440))  #:
desktop = StandardScenario(Settings(
    'desktop',
    width=1920 - 120,  # offset for e.g. top bar, bottom bar, dash bar, task bar
    height=1080 - 180,  # offset for e.g. dash bar
))  #:
laptop_l = StandardScenario(Settings('laptop_l', width=1440, height=900))  #:
laptop = StandardScenario(Settings('laptop', width=1024, height=768))  #:
tablet = StandardScenario(Settings('tablet', width=768, height=1024, mobile=True))  #:
mobile_l = StandardScenario(Settings('mobile_l', width=425, height=680, mobile=True))  #:
mobile_m = StandardScenario(Settings('mobile_m', width=375, height=600, mobile=True))  #:
mobile_s = StandardScenario(Settings('mobile_s', width=320, height=512, mobile=True))  #:
