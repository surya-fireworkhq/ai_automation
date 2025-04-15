from pydantic import BaseModel

class TestResultJson(BaseModel):
    title : str
    url: str
    status: str
    session: str
    confirmation_message: str
