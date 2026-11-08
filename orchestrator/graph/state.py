from typing import TypedDict


class orchestratorState(TypedDict):
    question : str
    selected_agent :str
    response : str