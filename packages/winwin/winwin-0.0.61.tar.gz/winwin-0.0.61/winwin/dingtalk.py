from typing import Optional

import httpx


class DingtalkBot:
    def __init__(self, endpoint: str):
        self.url = endpoint

    def send_text(self, message: str, at: Optional[list[str]] = None):
        params = {"msgtype": "text", "text": {"content": message}}
        if at:
            params["at"] = {"atMobiles": at}
        httpx.post(self.url, json=params)

    def send_link(
        self, title: str, text: str, message_url: str, pic_url: Optional[str] = None
    ):
        params = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "messageUrl": message_url,
                "picUrl": pic_url,
            },
        }
        httpx.post(self.url, json=params)

    def send_markdown(self, title: str, text: str, at: Optional[list[str]] = None):
        params = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
        if at:
            params["at"] = {"atMobiles": at}
        httpx.post(self.url, json=params)
