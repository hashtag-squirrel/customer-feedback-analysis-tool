import os
import json
from openai import OpenAI
from abc import ABC, abstractmethod


class AiClient(ABC):
    sentiments: list[str] = ['positive', 'neutral', 'negative']

    topics: list[str] = [
            'login',
            'performance',
            'billing',
            'ux',
            'responses',
            'customer service',
            'other']

    schema: dict[str, str] = {
            'sentiment': str,
            'topics': str
        }

    @abstractmethod
    def analyze_feedback(self, feedback_msg: str) -> dict[str, str]:
        pass


class OpenAiClient(AiClient):

    def __init__(self) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OpenAI API Key missing.")

        # Environment variable is automatically used by the API
        self.ai_client = OpenAI()

    def analyze_feedback(self, feedback_msg: str) -> dict[str, str]:
        response = self.ai_client.responses.create(
            model="gpt-5-mini",
            instructions=f"""
                You receive a feedback message from a customer.
                You should return a json response including the
                message's sentiment {self.sentiments}, as well as the
                topics covered in the message which can be found in
                this list: {self.topics}.
                The json response should follow the schema {self.schema}.
                """,
            input=feedback_msg,
        )

        response_object = json.loads(response.output_text)
        print(response_object)

        return response_object
