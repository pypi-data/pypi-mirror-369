import requests

class ValueDetectClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")


    def detect_value(self, text: str) -> str:
        """
        发送文本到服务端，返回检测到的价值
        """
        url = f"{self.base_url}/detect_value"
        resp = requests.post(url, json={"text": text})
        resp.raise_for_status()
        return resp.json().get("detected_value", "")
    

    def test_connection(self):
        """
        测试与服务端的连接是否正常
        """
        try:
            resp = requests.get(f"{self.base_url}/health")
            resp.raise_for_status()
            return resp.json().get("status", "unknown")
        except requests.RequestException as e:
            return f"Connection failed: {e}"
