import requests
import json
import logging
import hashlib
import sys
import subprocess
import shutil
from pathlib import Path
from config.config_manager import ConfigManager

class AutoUpdater:
    def __init__(self):
        self.logger = logging.getLogger('Updater')
        self.repo_url = "https://api.github.com/repos/seu_usuario/whatsapp-printer/releases/latest"
        self.current_version = "1.0.0"  # Buscar de um arquivo version.txt
        self.temp_dir = Path("updates")
        self.config = ConfigManager()

    def check_for_updates(self) -> bool:
        try:
            response = requests.get(
                self.repo_url,
                timeout=10,
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            latest = response.json()
            
            if latest['tag_name'] > self.current_version:
                self.logger.info(f"Nova versão disponível: {latest['tag_name']}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar atualizações: {str(e)}")
            return False

    def download_update(self, asset_url: str):
        try:
            self.temp_dir.mkdir(exist_ok=True)
            
            # Verificar hash do arquivo
            response = requests.get(asset_url, stream=True)
            file_path = self.temp_dir / "update.zip"
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verificar integridade
            if self._verify_hash(file_path, response.headers.get('X-Checksum-Sha256')):
                return file_path
            return None
            
        except Exception as e:
            self.logger.error(f"Falha no download: {str(e)}")
            return None

    def apply_update(self, update_file: Path):
        try:
            # Implementar lógica de atualização segura
            backup_dir = self.temp_dir / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            # Fazer backup
            for file in Path(".").glob("*.exe"):
                shutil.copy(file, backup_dir)
            
            # Aplicar atualização
            shutil.unpack_archive(update_file, ".")
            
            self.logger.info("Atualização aplicada com sucesso")
            return True
        except Exception as e:
            self.logger.critical(f"Falha na atualização: {str(e)}")
            self._rollback_update(backup_dir)
            return False

    def _verify_hash(self, file_path: Path, expected_hash: str) -> bool:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest() == expected_hash

    def _rollback_update(self, backup_dir: Path):
        try:
            for file in backup_dir.glob("*"):
                shutil.copy(file, ".")
            self.logger.info("Rollback concluído")
        except Exception as e:
            self.logger.error(f"Erro no rollback: {str(e)}")

    def run_update_check(self):
        if self.check_for_updates():
            if self.config.load_config().get("auto_update", True):
                self.logger.info("Iniciando atualização automática...")
                # Lógica completa de download e aplicação