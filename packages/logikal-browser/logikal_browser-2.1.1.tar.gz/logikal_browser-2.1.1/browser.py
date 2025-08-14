#!/usr/bin/env python3
from logikal_browser.chrome import ChromeBrowser
from logikal_browser.scenarios import desktop

browser = ChromeBrowser(settings=desktop.settings, headless=False)
browser.get('https://logikal.io')
input('Press <ENTER> to stop the program... ')
