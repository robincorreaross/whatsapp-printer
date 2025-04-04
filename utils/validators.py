import re
from pathlib import Path
import requests

class Validators:
    @staticmethod
    def phone_number(number: str) -> bool:
        pattern = r'^\d{13}$'  # 55 + 2 dígitos DDD + 9 dígitos número
        return re.fullmatch(pattern, number) is not None

    @staticmethod
    def pdf_file(path: Path) -> bool:
        return path.exists() and path.is_file() and path.suffix.lower() == '.pdf'

    @staticmethod
    def server_connection(server_url: str, timeout=5) -> bool:
        try:
            test_url = f"https://{server_url}/status"
            response = requests.get(test_url, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    def api_credentials(server_url: str, instance: str, api_key: str) -> bool:
        test_url = f"https://{server_url}/instance/connectionState/{instance}"
        try:
            response = requests.get(
                test_url,
                headers={"apikey": api_key},
                timeout=10
            )
            return response.json().get("state") == "open"
        except Exception:
            return False