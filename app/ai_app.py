import os
from openai import OpenAI
from app.models import Feedback
import json


def get_ai_response(feedback_msg):

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    sentiments = ['positive', 'neutral', 'negative']
    topics = ['login', 'performance', 'billing', 'ux', 'responses', 'customer service', 'other']

    schema = {
        'sentiment': str,
        'topics': str
    }

    response = client.responses.create(
        model="gpt-5-mini",
        instructions="You receive a feedback message from a customer."
                     "You should return a json response including the message's sentiment"
                     f"{sentiments}, as well as the topics covered in the message"
                     f"which can be found in this list: {topics}."
                     f"The json response should follow the schema {schema}.",
        input=feedback_msg,
    )

    response_object = json.loads(response.output_text)
    print(response_object)

    return response_object