from pydantic import BaseModel, Field
from typing import List


class User(BaseModel):
    username : str = None
    password :str = None
    CV_content : str = ""
    text_summary : str = ""
    questions : List[str] = []

class Analysis(BaseModel):
    summary: str = Field(description="Rezumatul textului")
    dictionary: str = Field(description="Un string ce conține un JSON valid (ex: '{\"key\": \"value\"}')")

