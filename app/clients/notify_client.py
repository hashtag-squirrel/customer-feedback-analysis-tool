import requests
from app.models.feedback import Feedback
import os
from abc import ABC, abstractmethod


class NotifyClient(ABC):
    @abstractmethod
    def notify_team(self, feedback: Feedback):
        pass


class NtfyNotifyClient(NotifyClient):

    def __init__(self):
        self.server_url = os.environ.get(
            key="NTFY_SERVER_URL",
            default="http://localhost/channel")

    def notify_team(self, feedback: Feedback):

        requests.post(
            self.server_url,
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
