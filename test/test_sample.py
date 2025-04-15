import asyncio
import pytest
from browser_use.agent.service import Agent
from custom_controllers.site_validation import SiteController



@pytest.mark.asyncio
class TestCase:

    controller = SiteController().controller

    async def test_sample(self, browser, llm):
        """
        :param browser: Browser is fixture
        :param llm:  llm decides which LLM should be used
        :Controller: should be declared always outside of function
        """
        task = (
            'Important: I am a UI Automation tester validating the tasks. '
            'Open the browser, perform firework action, and wait for 10 seconds'
        )
        agent_params = {
            "task": task,
            "llm": llm,
            "browser": browser,
            "use_vision": False,
            "controller": self.controller
        }
        agent = Agent(**agent_params)
        history = await agent.run()
        assert history is not None

    async def test_sample_browser_context(self, context, llm):
        """
        :param context: Context is a Browser fixture
        :param llm: Llm decides which LLM should be used
        :Controller: Should be declared always outside of function
        """
        task = (
            'Important: I am a UI Automation tester validating the tasks.'
            'Open the browser, perform firework action url="https://www.youtube.com", and wait for 10 seconds'
        )
        agent_params = {
            "task": task,
            "llm": llm,
            "browser_context": context,
            "use_vision": False,
            "controller": self.controller
        }
        agent = Agent(**agent_params)
        history = await agent.run()
        assert history is not None
