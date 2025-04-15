# AI Automation

We are using Browser-use library for our AI Automation

🌐 Browser-use is the easiest way to connect your AI agents with the browser.

# Quick start

With UV (Python>=3.11):
To Install UV check documentation - [here](https://docs.astral.sh/uv/)

Step 1: Create a Virtual env using uv

```bash
uv venv <virtualenv-name> 
```

Step 2: Setup requirements on environments

```bash
uv pip install -r ai_req.txt
```

Step 3: Install Playwright

```bash
playwright install
```

Setup up your agent:

Add your LLM Model for the provider you want to use to your `.env` file.

```bash
LLM_MODEL_NAME=
```
For eg:) Setup LLM Model Name
```
if Chatgpt - "gpt-4o"
if Gemini - "gemini-2.0-flash-lite"
if Deepseek - "deepseek-chat"
```
Add your API keys for the LLM provider you want to use to your `.env` file.

```bash
OPENAI_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
```

For other settings, models, and more, check out the [documentation 📕](https://docs.browser-use.com).
