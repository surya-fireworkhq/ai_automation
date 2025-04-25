import time
from email.policy import strict

from browser_use import Controller, ActionResult
from browser_use.browser.browser import BrowserContext
from custom_model.json_model import TestResultJson
import os
from base64 import b64encode
from utils.pw_element import PwElement

os.environ["ANONYMIZED_TELEMETRY"] = "false"


class Dashboard:

    # output model is optional
    controller = Controller(output_model=TestResultJson)
    # UPLOAD_INPUT = ('xpath=//input[@type="file"]')
    UPLOAD_INPUT = 'css=input[accept=".mp4,.mov"]'

    @staticmethod
    @controller.registry.action('wait for x seconds')
    async def wait_for_x_seconds(x: int):
        time.sleep(x)
        return ActionResult(success=True)

    @staticmethod
    @controller.registry.action('Upload a short video')
    async def upload_short_video(file_path: str, browser: BrowserContext):
        page = await browser.get_current_page()
        await page.wait_for_selector(Dashboard.UPLOAD_INPUT, state="hidden")
        file_chooser = page.locator(Dashboard.UPLOAD_INPUT)
        await file_chooser.set_input_files([file_path])
        return ActionResult(success=True)
