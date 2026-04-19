from pydantic import BaseModel, Field
from typing import List


class User(BaseModel):
    username : str = None
    password :str = None
    CV_content : str = ""
    text_summary : str = ""
    questions : List[str] = []

class Analysis(BaseModel):
    summary: str = Field(description="Text Result")
    dictionary: str = Field(description="json string")

