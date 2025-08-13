from pydantic import BaseModel

class ResponseFunctionCall(BaseModel):
    name: str
    arguments: str|None
    parsed_arguments: dict|None

class AssistantResponse(BaseModel):
    final_response_str: str|None
    called_functions: dict