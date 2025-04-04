import requests
import base64
import logging
from pathlib import Path

class WhatsAppAPIClient:
    def __init__(self, server_url: str, instance: str, api_key: str):
        self.base_url = f"https://{server_url}/message/sendMedia/{instance}"
        self.headers = {"apikey": api_key, "Content-Type": "application/json"}
        self.logger = logging.getLogger('WhatsAppAPIClient')

    def _encode_pdf(self, pdf_path: Path) -> str:
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Falha ao codificar PDF: {str(e)}")
            raise

    def send_pdf(self, number: str, pdf_path: Path, message: str = "") -> bool:
        try:
            media_data = self._encode_pdf(pdf_path)
            
            payload = {
                "number": f"55{number}",  # Adiciona prefixo internacional automaticamente
                "mediatype": "document",
                "mimetype": "application/pdf",
                "caption": message,
                "media": media_data,
                "fileName": pdf_path.name,
                "delay": 120  # Timeout de 2 minutos
            }

            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )

            response.raise_for_status()
            self.logger.info(f"PDF enviado para {number} com sucesso")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição: {str(e)}")
            return False
        except Exception as e:
            self.logger.critical(f"Erro não tratado: {str(e)}")
            return False