import uuid, httpx
from orchestrator.schema import A2ARequest, A2AResponse


class A2A_client:
    """
    Async HTTP client that speaks the A2A protocol.
    Usage:
        client = A2AClient(base_url="http://localhost:8001")
        response = await client.send(question="What is a Roth IRA?")
        print(response.answer)
    """
    def __init__(self,base_url:str, timeout:float = 10.0, max_retries:int = 2 ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._chat_url = f"{self.base_url}/chat"


    async def send(self, question:str)->A2AResponse:
        """
        Sends an A2A request and returns a typed A2AResponse.
        - Retries on network errors and 5xx responses
        - Does NOT retry on 4xx (client errors)
        """
        request = A2ARequest(question=question)
        payload = request.model_dump()

        last_error = None

        for attempt in range(1,self.max_retries+2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as http:
                    resp = await http.post(
                        self._chat_url,
                        json=payload,
                        headers = {
                            "X-Request-ID": request.request_id,
                            "Content-Type": "application/json",     
                        }
                    )

                    if resp.status_code < 500:
                        resp.raise_for_status()
                    elif resp.status_code >= 500:
                        last_error = httpx.HTTPStatusError(message=f"Server error{resp.status_code}",request=resp.request,response=resp)
                        continue
                    data = resp.json()
                    return A2AResponse(
                        answer = data.get("response",""),
                        agent = data.get("agent","financial"),
                        request_id=data.get("request_id", request.request_id),
                    )
            except Exception as e:
                last_error = e
                continue

        raise last_error













    




