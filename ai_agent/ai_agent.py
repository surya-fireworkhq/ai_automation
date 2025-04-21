from browser_use.agent.service import Agent
from browser_use import Controller, ActionResult
from browser_use.browser.browser import BrowserContext
import os
import pytest
import json

expected_browser = (os.environ.get('BROWSER') or 'chrome').lower()

class AIAgent:

    controller = Controller()

    def __new__(cls, **params):
        llm = os.environ.get("LLM_MODEL_NAME")
        if "deepseek" in llm.lower():
            params["use_vision"] = False
        if expected_browser.lower() == "browserstack":
            cc = params['controller']
            # To add a common controller, create a controller function and append
            add_controller_functions = {"get_browserstack_session":"get browserstack session"}
            for i in add_controller_functions:
                cc.registry.registry.actions[i] = (
                    AIAgent.controller.registry.registry.actions)[i]
                params['task'] += f"\n{add_controller_functions[i]}"
        pytest.agent = Agent(**params)
        return pytest.agent

    @staticmethod
    @controller.registry.action('get browserstack session')
    async def get_browserstack_session(browser: BrowserContext):
        page = await browser.get_current_page()
        pytest.session_details = await page.evaluate(
            "_ => {}", f"browserstack_executor: {json.dumps({'action': 'getSessionDetails'})}"
        )
        return ActionResult(success=True)
