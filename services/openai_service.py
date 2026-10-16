from openai import OpenAI

from config import settings
from models.ticket import TicketResponse


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
    
    def get_response(self, messages):
        response = self.client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            messages=messages,
            response_format=TicketResponse,
        )
        return response.choices[0].message.parsed
