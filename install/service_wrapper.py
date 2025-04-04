import subprocess
import logging
import sys
from pathlib import Path

class ServiceWrapper:
    def __init__(self):
        self.logger = logging.getLogger('ServiceWrapper')
        self.nssm_path = Path("nssm.exe")
        
    def install_service(self):
        try:
            subprocess.run([
                str(self.nssm_path), 'install',
                'WhatsAppPrinterService',
                sys.executable,
                str(Path(__file__).parent.parent / "main.py")
            ], check=True)
            
            self.logger.info("Serviço instalado com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Falha na instalação do serviço: {str(e)}")
            return False

    def configure_service(self):
        try:
            subprocess.run([
                str(self.nssm_path), 'set', 'WhatsAppPrinterService',
                'Description', 'Serviço de impressão virtual WhatsApp'
            ], check=True)
            
            subprocess.run([
                str(self.nssm_path), 'set', 'WhatsAppPrinterService',
                'AppStdout', str(Path("logs/service.log"))
            ], check=True)
            
            self.logger.info("Serviço configurado")
            return True
        except Exception as e:
            self.logger.error(f"Falha na configuração: {str(e)}")
            return False