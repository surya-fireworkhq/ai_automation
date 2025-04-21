import pytest
from ai_agent.ai_agent import AIAgent as Agent
from custom_controllers.site_validation import SiteController


@pytest.mark.asyncio
class TestCase:

    controller = SiteController().controller

    async def test_custom_sample(self, browser, llm):
        """
        :param browser: Browser is fixture
        :param llm: llm decides which LLM should be used
        :Controller: should be declared always outside of function
        """
        task = (
            'Important: I am a UI Automation tester validating the tasks. '
            'Open the browser, perform firework action'
            'wait for 5 seconds'
        )
        agent_params = {
            "task": task,
            "llm": llm,
            "browser": browser,
            "controller": self.controller
        }
        agent = Agent(**agent_params)
        history = await agent.run()
        assert history is not None

    async def test_custom_sample_browser_context(self, context, llm):
        """
        :param context: Context is a Browser fixture
        :param llm: Llm decides which LLM should be used
        :Controller: Should be declared always outside of function
        """
        task = (
            'Important: I am a UI Automation tester validating the tasks.'
            'Open the browser'
            'perform firework action url="https://www.youtube.com"'
            'wait for 2 seconds'
        )
        agent_params = {
            "task": task,
            "llm": llm,
            "browser_context": context,
            "controller": self.controller
        }
        agent = Agent(**agent_params)
        history = await agent.run()
        assert history is not None
