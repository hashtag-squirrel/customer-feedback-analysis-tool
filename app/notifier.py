import requests
from app.models.feedback import Feedback
import os


notify_server_url = os.environ.get(
    key="NOTIFY_SERVER_URL",
    default="http://localhost/channel")


def notify_team(feedback: Feedback):

    requests.post(
        notify_server_url,
        data=f"""
        Negative feedback received. Requires immediate attention.

        Message: {feedback.message}
        Topics: {feedback.topics}
        Contact: {feedback.name}, {feedback.email}
        """,
        headers={
            "Title": "Priority feedback received",
            "Tags": "warning"
        })
