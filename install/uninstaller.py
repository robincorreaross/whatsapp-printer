import sys
import ctypes
import subprocess
import shutil
import logging
import os
from pathlib import Path

class PrinterUninstaller:
    def __init__(self):
        self.logger = logging.getLogger('Uninstaller')
        self.app_name = "WhatsApp Printer"
        self.dirs_to_remove = [
            "logs",
            "temp",
            "config",
            "certs"
        ]
        
    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def remove_printer(self):
        try:
            subprocess.run([
                'rundll32', 'printui.dll,PrintUIEntry',
                '/dl',
                '/n', self.app_name,
                '/q'
            ], check=True)
            self.logger.info("Impressora removida com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Falha ao remover impressora: {str(e)}")
            return False

    def cleanup_files(self):
        try:
            # Remover atalho de inicialização
            startup_path = (
    Path(os.environ.get('ALLUSERSPROFILE', 'C:\\ProgramData')) /
    'Microsoft\\Windows\\Start Menu\\Programs\\StartUp' /
    f"{self.app_name}.lnk"
)
            
            if startup_path.exists():
                startup_path.unlink()
            
            # Remover diretórios
            for dir in self.dirs_to_remove:
                dir_path = Path(dir)
                if dir_path.exists():
                    shutil.rmtree(dir_path)
            
            self.logger.info("Arquivos removidos")
            return True
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {str(e)}")
            return False

    def remove_firewall_rule(self):
        try:
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                f'name="{self.app_name}"'
            ], check=True)
            self.logger.info("Regra de firewall removida")
        except Exception as e:
            self.logger.warning(f"Não foi possível remover regra de firewall: {str(e)}")

    def run_uninstallation(self):
        try:
            if not self.is_admin():
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)

            self.remove_printer()
            self.remove_firewall_rule()
            self.cleanup_files()
            
            self.logger.info("Desinstalação concluída com sucesso!")
            return True
            
        except Exception as e:
            self.logger.critical(f"Falha na desinstalação: {str(e)}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uninstaller = PrinterUninstaller()
    uninstaller.run_uninstallation()