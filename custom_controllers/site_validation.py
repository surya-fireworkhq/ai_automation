import time

from browser_use import Controller, ActionResult
from browser_use.browser.browser import BrowserContext
from custom_model.json_model import TestResultJson
import os

os.environ["ANONYMIZED_TELEMETRY"] = "false"


class SiteController:

    # output model is optional
    controller = Controller(output_model=TestResultJson)

    @staticmethod
    @controller.registry.action('perform firework action')
    async def perform_firework_action(url: str, browser: BrowserContext):
        # Access browser context if needed
        if "blank" in url:
            url = "https://www.firework.com"
        page = await browser.get_current_page()
        await page.goto(url)
        return ActionResult(extracted_content="Performed Firework Action")

    @staticmethod
    @controller.registry.action('wait for x seconds')
    async def wait_for_x_seconds(x: int):
        time.sleep(x)
        return ActionResult(is_done=True)
