import os
import time

import pytest
from ai_agent.ai_agent import AIAgent as Agent
from custom_controllers.dashboard import Dashboard


@pytest.mark.asyncio
class TestCase:

    controller = Dashboard().controller

    async def test_create_short_video(self, context, llm):
        biz_url = 'https://business-staging.fireworktv.com/business/gpB3JQ/channel/L4bMDWr/videos'
        token = "?token="+os.environ.get("NABOO_TOKEN")
        initial_actions = [
            {'open_tab': {'url': biz_url+token}},
        ]
        path = "/Users/surya/ai_automation/ai_automation/videos/default_event_trailer.mp4"
        path = os.path.abspath(path)
        title = f"Test-Ai-sv-{time.time_ns()}"

        task = (
            'click on "+ Add videos" button'
            'Click on Upload video button'
            f'Upload a short video file_path={path} '
            'Wait for Next button to be enabled '
            'click Next button after enabled '
            f'Enter "{title}" in Title input field '
            'Click on Product interaction field and change to "CTA" option '
            'wait for 2 seconds '
            'Click on View and change to "See Full Recipe" option '
            f'Enter "https://www.google.com" in Insert link input field '
            'Click Upload button '
            'Wait for 2 seconds '
            'Refresh the webpage'
            'Click on Videos button '
            f'Enter {title} in search field '
            'Press Enter Key '
            f'Verify video title={title} is present '
        )
        agent_params = {
            "task": task,
            "llm": llm,
            "browser_context": context,
            "controller": self.controller,
            "initial_actions": initial_actions
        }
        agent = Agent(**agent_params)
        history = await agent.run()
        assert history is not None
