from pydantic import BaseModel
import uuid, httpx


class UserQuery(BaseModel):
    question : str



class A2ARequest(BaseModel):
    """Standard payload sent to every downstream A2A agent."""
    question:str
    request_id: str = ""

    def _model_post_init(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


class A2AResponse(BaseModel):
    """Standard payload received from every downstream A2A agent."""
    answer:str
    agent : str
    request_id : str = ""
