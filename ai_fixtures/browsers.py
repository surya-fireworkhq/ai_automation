import subprocess
import urllib.parse
from browser_use import Browser
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from dotenv import load_dotenv

from ai_fixtures.reporting import *


load_dotenv()
expected_browser = (os.environ.get('BROWSER') or 'chrome').lower()


def get_browserstack_instance():
    username = os.getenv('BROWSERSTACK_USERNAME')
    access_key = os.getenv('BROWSERSTACK_ACCESS_KEY')

    project = os.getenv('BROWSERSTACK_PROJECT', 'Playwright AI Test')
    build = os.getenv('BROWSERSTACK_BUILD', 'Windows')
    build_tag = os.getenv('BROWSERSTACK_BUILD_TAG', '10')
    os_name = os.getenv('BROWSERSTACK_OS', 'windows').lower()
    os_version = os.getenv('BROWSERSTACK_OS_VERSION', '11')
    browser_name = os.getenv('BROWSERSTACK_BROWSER_NAME', 'chrome').lower()
    browser_version = os.getenv('BROWSERSTACK_BROWSER_VERSION', 'latest')

    if browser_name not in ["chrome", "firefox", "safari", "edge"]:
        raise Exception(f'Unsupported browser: {browser_name}')

    playwright_version = subprocess.getoutput('playwright --version').strip().split(" ")[1]

    browser_mapping = {
        "chrome": "chrome",
        "firefox": "playwright-firefox",
        "edge": "edge",
        "safari": "playwright-webkit",
    }
    bs_browser_name = browser_mapping[browser_name]

    capabilities = {
        'os': os_name,
        'os_version': os_version,
        'browser': bs_browser_name,
        'browser_version': browser_version,
        'browserstack.username': username,
        'browserstack.accessKey': access_key,
        'project': project,
        'build': build,
        'name': project,
        'buildTag': build_tag,
        'resolution': '1920x1080',
        'client.playwrightVersion': playwright_version,
        'browserstack.debug': 'true',
        'browserstack.console': 'info',
        'browserstack.networkLogs': 'true',
        'browserstack.interactiveDebugging': 'true'
    }

    cdp_url = 'wss://cdp.browserstack.com/playwright?caps=' + urllib.parse.quote(json.dumps(capabilities))
    config = BrowserConfig(wss_url=cdp_url)
    return Browser(config=config)


@pytest.fixture
async def browser(request):
    browser_env = os.environ.get("BROWSER")
    if browser_env.lower() == "browserstack":
        browser_instance = get_browserstack_instance()
    else:
        browser_instance = Browser()
    yield browser_instance
    if hasattr(pytest, "session_details"):
        pytest.browserstack_session_id = await get_session_id()
        test_failed_check(request, browser_instance, playwright=True)
    await browser_instance.close()


@pytest.fixture
async def context(browser):
    config = BrowserContextConfig(
        wait_for_network_idle_page_load_time=60.0,
        browser_window_size={'width': 1920, 'height': 1080},
        locale='en-US',
    )
    browser_context = BrowserContext(browser=browser, config=config)
    yield browser_context


async def get_session_id():
    session_id = ""
    if expected_browser == "browserstack":
        if hasattr(pytest, "session_details"):
            LOGGER.info("Browserstack session %s", pytest.session_details)
            session_id = json.loads(pytest.session_details)['hashed_id']
    return session_id
