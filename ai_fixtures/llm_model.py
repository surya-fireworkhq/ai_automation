import os

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


@pytest.fixture()
def llm():
    llm = os.environ.get("LLM_MODEL_NAME")
    if "gpt" in llm.lower():
        llm = chatgpt()
    elif "deepseek" in llm.lower():
        llm = deepseek()
    elif "gemini" in llm.lower():
        llm = gemini()
    yield llm


def chatgpt():
    if os.getenv("OPENAI_API_KEY"):
        model = os.environ.get("LLM_MODEL_NAME") # "gpt-4o"
        # Initialize the model
        llm = ChatOpenAI(
            model=model,
            temperature=0.0,
            api_key=SecretStr(os.getenv("OPENAI_API_KEY"))
        )
        return llm
    else:
        raise "No API Key is provided"


def deepseek():
    if os.getenv("DEEPSEEK_API_KEY"):
        # Note: use_vision=False for deep-seek on Agent configuration
        model = os.environ.get("LLM_MODEL_NAME") # "deepseek-chat" or "deepseek-reasoner"
        llm = ChatOpenAI(
            base_url='https://api.deepseek.com/v1',
            model=model,
            api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY"))
        )
        return llm
    else:
        raise "No API Key is provided"


def gemini():
    if os.getenv("GEMINI_API_KEY"):
        model = os.environ.get("LLM_MODEL_NAME") # "gemini-2.0-flash-lite-001"
        llm = ChatGoogleGenerativeAI(model=model,
                             api_key=SecretStr(os.getenv("GEMINI_API_KEY")))
        return llm
    else:
        raise "No API Key is provided"
