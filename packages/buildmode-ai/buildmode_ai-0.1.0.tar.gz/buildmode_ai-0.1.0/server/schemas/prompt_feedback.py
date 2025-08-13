from pydantic import BaseModel


class PromptFeedback(BaseModel):
    task_id: str
    original_prompt: str
    correction: str
    updated_prompt: str
