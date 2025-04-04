import os
import time
from pathlib import Path
import logging
from typing import Optional

class FileManager:
    def __init__(self, temp_dir: Path = Path("temp")):
        self.temp_dir = temp_dir
        self.logger = logging.getLogger('FileManager')
        self._init_directory()

    def _init_directory(self):
        try:
            self.temp_dir.mkdir(exist_ok=True)
            self.logger.info(f"Diretório temporário criado: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"Falha ao criar diretório: {str(e)}")
            raise

    def safe_delete(self, path: Path, retries=3, delay=1) -> bool:
        for i in range(retries):
            try:
                os.remove(path)
                self.logger.info(f"Arquivo removido: {path}")
                return True
            except PermissionError:
                if i < retries - 1:
                    time.sleep(delay)
                    continue
                self.logger.error(f"Falha ao remover arquivo: Permissão negada")
                return False
            except FileNotFoundError:
                self.logger.warning(f"Arquivo não encontrado: {path}")
                return True
            except Exception as e:
                self.logger.error(f"Erro inesperado ao deletar: {str(e)}")
                return False

    def generate_temp_path(self, prefix: str = "doc") -> Path:
        timestamp = int(time.time() * 1000)
        return self.temp_dir / f"{prefix}_{timestamp}.pdf"

    def cleanup_temp_files(self, max_age_hours=24):
        # Implementar limpeza periódica
        pass