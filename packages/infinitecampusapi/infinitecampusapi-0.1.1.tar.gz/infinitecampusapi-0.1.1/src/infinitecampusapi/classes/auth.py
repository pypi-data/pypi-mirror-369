import requests


class Auth:
    url: str
    key: str
    secret: str
    access_token: str
    base_url: str

    def __init__(self, token_url, key, secret, base_url):
        self.token_url = token_url
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.access_token = self.__get_token()

    def __get_token(self) -> str:
        url = self.token_url
        data = {
            "grant_type": "client_credentials",
            "client_id": self.key,
            "client_secret": self.secret,
        }
        response = requests.post(url, data=data)
        access_token = response.json()["access_token"]
        return access_token
