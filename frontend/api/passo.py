import requests


class PasswordManager:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/passwords"):
        self.base_url = base_url
        self.session = requests.Session()

    def _get_headers(self, token: str):
        return {"Authorization": f"Bearer {token}"}

    def get_passwords(self, token: str):
        try:
            response = self.session.get(
                f"{self.base_url}/",
                headers=self._get_headers(token)
            )
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def create_password(self, token: str, data: dict):
        try:
            response = self.session.post(
                f"{self.base_url}/",
                json=data,
                headers=self._get_headers(token)
            )
            return response.status_code == 200
        except:
            return False

    def get_password_details(self, token: str, entry_id: int):
        try:
            response = self.session.get(
                f"{self.base_url}/{entry_id}/",
                headers=self._get_headers(token)
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def update_password(self, token: str, entry_id: int, data: dict) -> bool:
        try:
            response = self.session.put(
                f"{self.base_url}/{entry_id}/",
                json=data,
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.status_code == 200
        except:
            return False

    def delete_password(self, token: str, entry_id: int) -> bool:
        try:
            response = self.session.delete(
                f"{self.base_url}/{entry_id}/",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.status_code == 204
        except:
            return False