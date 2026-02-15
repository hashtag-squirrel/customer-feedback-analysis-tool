import os
from openai import OpenAI
from app.models import Feedback

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

feedback_text = """
your app is fast, but the last update broke login on my ipad.
please fix asap, i need this for work.
"""

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
    input=feedback_text,
)

print(response.output_text)