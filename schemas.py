from pydantic import BaseModel

class WebhookPayload(BaseModel):
    user_id: str
    event_id: str

class MLResponse(BaseModel):
    status: str
    message: str
    updated_items: int