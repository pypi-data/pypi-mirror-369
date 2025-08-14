from logikal_utils.project import PYPROJECT

#: The available browser versions as specified in the ``tool.browser.versions`` section in
#: ``pyproject.toml``.
#:
#: .. tip:: The currently available versions can be found on the following URLs:
#:
#:  * `Chrome <https://googlechromelabs.github.io/chrome-for-testing/#stable>`_
#:  * `Edge <https://learn.microsoft.com/en-us/deployedge/microsoft-edge-relnote-stable-channel>`_
#:  * `Edge WebDriver <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver>`_
BROWSER_VERSIONS = PYPROJECT.get('tool', {}).get('browser', {}).get('versions', {})
