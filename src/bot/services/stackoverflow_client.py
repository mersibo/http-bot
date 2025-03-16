import requests

STACKOVERFLOW_API_URL = "https://api.stackexchange.com/2.3/questions"

class StackOverflowClient:
    @staticmethod
    def get_last_update(question_id):
        params = {"order": "desc", "sort": "activity", "site": "stackoverflow"}
        response = requests.get(f"{STACKOVERFLOW_API_URL}/{question_id}", params=params)

        if response.status_code == 200:
            data = response.json()
            if "items" in data and data["items"]:
                return data["items"][0].get("last_activity_date")
        return None
