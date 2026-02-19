import os
import json
from openai import OpenAI, RateLimitError, BadRequestError
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

    prompt: str = f"""
                You receive a feedback message from a customer.
                You should return a json response including the
                message's sentiment {sentiments}, as well as the
                topics covered in the message which can be found in
                this list: {topics}. 
                The json response should follow the schema {schema}.
                """

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

        try:
            response = self.ai_client.responses.create(
                model="gpt-5-mini",
                instructions=self.prompt,
                input=feedback_msg,
            )

            raw_text = response.output_text

            try:
                response_object: dict[str, str] = json.loads(raw_text)

                if not isinstance(response_object, dict):
                    raise ValueError("Response JSON is not an object")

                required_keys = self.schema.keys()

                if not required_keys.issubset(response_object.keys()):
                    missing = required_keys - response_object.keys()
                    raise ValueError(f"Missing keys: {missing}")

                return response_object

            except json.JSONDecodeError as e:
                print("Invalid JSON from AI:")
                print(raw_text)
                print(e)
                invalid_response = {
                    'sentiment': 'Unrecognized',
                    'topics': 'Could not parse topics'
                    }
                return invalid_response

        except RateLimitError as e:
            print("Rate or quota limit reached")
            print(e)
            return None

        except BadRequestError as e:
            print("Bad request (likely too many tokens)")
            print(e)
            return None
