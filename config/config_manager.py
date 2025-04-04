import json
from pathlib import Path
import logging
from typing import Optional, Dict

class ConfigManager:
    def __init__(self, config_path: Path = Path("config/settings.json")):
        self.config_path = config_path
        self.logger = logging.getLogger('ConfigManager')
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_config({
                "server_url": "",
                "instance": "",
                "api_key": "",
                "max_workers": 3,
                "auto_delete": True
            })

    def load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")
            return {}

    def save_config(self, config: Dict) -> bool:
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {str(e)}")
            return False

    def validate_current_config(self) -> bool:
        config = self.load_config()
        return all([
            config.get("server_url"),
            config.get("instance"),
            config.get("api_key")
        ])