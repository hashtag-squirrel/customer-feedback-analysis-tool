import os
import json
from typing import List, Dict
from openai import OpenAI
from abc import ABC, abstractmethod


class AiService(ABC):
    sentiments: List[str] = ['positive', 'neutral', 'negative']

    topics: List[str] = [
            'login',
            'performance',
            'billing',
            'ux',
            'responses',
            'customer service',
            'other']

    schema: Dict[str, str] = {
            'sentiment': str,
            'topics': str
        }

    @abstractmethod
    def get_ai_response(self, feedback_msg: str):
        pass


class OpenAiService(AiService):
    ai_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    def get_ai_response(self, feedback_msg: str) -> Dict[str, str]:
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
