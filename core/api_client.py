import requests
import base64
import logging
import certifi
import os
from pathlib import Path
from typing import Optional

class WhatsAppAPIClient:
    def __init__(self, server_url: str, instance: str, api_key: str, verify_ssl: bool = True):
        self.base_url = f"https://{server_url}/message/sendMedia/{instance}"
        self.headers = {"apikey": api_key, "Content-Type": "application/json"}
        self.logger = logging.getLogger('WhatsAppAPIClient')
        
        # Configuração avançada de SSL
        self.ssl_verify = self._configure_ssl(verify_ssl)
        self.custom_ca_bundle = None
        
        # Verificar se o certificado padrão existe
        if not os.path.exists(certifi.where()):
            self.logger.warning("Certificado CA raiz padrão não encontrado!")

    def _configure_ssl(self, verify_ssl: bool) -> bool:
        """Configura a verificação SSL com fallback seguro"""
        if verify_ssl:
            # Tenta usar o bundle do certifi primeiro
            if os.path.exists(certifi.where()):
                self.logger.info("Usando certificados CA do sistema via certifi")
                return certifi.where()
            
            # Fallback para certificados do sistema
            self.logger.warning("Usando certificados CA do sistema operacional")
            return True
        
        self.logger.warning("Verificação SSL DESATIVADA - Não use em produção!")
        return False

    def set_custom_certificate(self, cert_path: Path):
        """Permite usar um certificado CA personalizado"""
        if cert_path.exists():
            self.ssl_verify = str(cert_path)
            self.custom_ca_bundle = str(cert_path)
            self.logger.info(f"Usando certificado CA personalizado: {cert_path}")
        else:
            self.logger.error("Caminho do certificado personalizado inválido")

    def send_pdf(self, number: str, pdf_path: Path, message: str = "") -> bool:
        try:
            media_data = self._encode_pdf(pdf_path)
            
            payload = {
                "number": f"55{number}",
                "mediatype": "document",
                "mimetype": "application/pdf",
                "caption": message,
                "media": media_data,
                "fileName": pdf_path.name,
                "delay": 120
            }

            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30,
                verify=self.ssl_verify  # Configuração SSL aplicada aqui
            )

            response.raise_for_status()
            self.logger.info(f"PDF enviado para {number} com sucesso")
            return True
            
        except requests.exceptions.SSLError as e:
            self.logger.critical(f"Erro de SSL: {str(e)}")
            if self.custom_ca_bundle:
                self.logger.error("Verifique o certificado personalizado")
            else:
                self.logger.error("Possível problema com certificados CA")
            return False
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição: {str(e)}")
            return False
        except Exception as e:
            self.logger.critical(f"Erro não tratado: {str(e)}")
            return False