import sys
import os
import ctypes
import winreg
import subprocess
import logging
import shutil
from pathlib import Path
from config.config_manager import ConfigManager
from utils.validators import Validators

class PrinterInstaller:
    def __init__(self):
        self.logger = logging.getLogger('Installer')
        self.config = ConfigManager()
        self.app_name = "WhatsApp Printer"
        self.required_dirs = [
            "logs",
            "temp",
            "config",
            "certs"
        ]
        self.startup_folder = os.path.join(
            os.environ.get('ALLUSERSPROFILE', 'C:\\ProgramData'),
            'Microsoft\\Windows\\Start Menu\\Programs\\StartUp'
        )

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def create_directories(self):
        try:
            for dir in self.required_dirs:
                dir_path = Path(dir)
                dir_path.mkdir(exist_ok=True, parents=True)
                self.logger.info(f"Diretório criado: {dir_path.resolve()}")
            
            # Aplicar permissões restritivas
            for dir in ["config", "certs"]:
                subprocess.run(
                    ['icacls', str(dir), '/inheritance:r', '/grant:r', '*S-1-5-32-544:(OI)(CI)F'],
                    check=True
                )
        except Exception as e:
            self.logger.error(f"Erro ao criar diretórios: {str(e)}")
            raise

    def register_printer(self):
        try:
            # Verificar se já existe
            if self._printer_exists():
                self.logger.warning("Impressora já está registrada")
                return True

            # Registrar driver
            subprocess.run([
                'rundll32', 'printui.dll,PrintUIEntry',
                '/ia',
                '/m', "Microsoft Print To PDF",
                '/f', "%windir%\\inf\\ntprint.inf"
            ], check=True)

            # Criar impressora
            subprocess.run([
                'rundll32', 'printui.dll,PrintUIEntry',
                '/if',
                '/b', self.app_name,
                '/f', "%windir%\\inf\\ntprint.inf",
                '/r', 'file:',
                '/m', "Microsoft Print To PDF",
                '/u',
                '/q'
            ], check=True)

            self.logger.info("Impressora virtual registrada com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Falha ao registrar impressora: {str(e)}")
            return False

    def _printer_exists(self) -> bool:
        try:
            output = subprocess.check_output(
                ['wmic', 'printer', 'get', 'name'],
                text=True
            )
            return self.app_name in output
        except:
            return False

    def create_startup_shortcut(self):
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            shortcut_path = os.path.join(self.startup_folder, f"{self.app_name}.lnk")

            # Usar objeto WScript para criar atalho
            vbs_script = f"""
            Set oWS = WScript.CreateObject("WScript.Shell")
            Set oLink = oWS.CreateShortcut("{shortcut_path}")
            oLink.TargetPath = "{exe_path}"
            oLink.WorkingDirectory = "{os.getcwd()}"
            oLink.Description = "{self.app_name}"
            oLink.Save
            """
            
            subprocess.run(
                ['cscript', '//B', '//Nologo'],
                input=vbs_script,
                text=True,
                check=True
            )
            
            self.logger.info(f"Atalho de inicialização criado: {shortcut_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao criar atalho: {str(e)}")
            return False

    def install_dependencies(self):
        try:
            requirements = Path(__file__).parent.parent / "requirements.txt"
            if not requirements.exists():
                self.logger.error("Arquivo requirements.txt não encontrado")
                return False

            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True
            )
            
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
                check=True
            )
            
            self.logger.info("Dependências instaladas com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Falha ao instalar dependências: {str(e)}")
            return False

    def _configure_firewall(self):
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name="{self.app_name}"',
                f'program="{exe_path}"',
                'dir=in',
                'action=allow',
                'enable=yes'
            ], check=True)
            self.logger.info("Regra de firewall configurada")
        except Exception as e:
            self.logger.warning(f"Não foi possível configurar firewall: {str(e)}")

    def run_installation(self):
        try:
            if not self.is_admin():
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)

            self.create_directories()
            
            if not self.register_printer():
                raise Exception("Falha no registro da impressora")

            if not self.create_startup_shortcut():
                raise Exception("Falha ao criar atalho de inicialização")

            if not self.install_dependencies():
                raise Exception("Falha na instalação de dependências")

            self._configure_firewall()
            
            self.config.save_config({
                "server_url": input("URL do servidor Evolution API: "),
                "instance": input("Nome da instância: "),
                "api_key": input("Chave API: "),
                "max_workers": 3,
                "auto_delete": True
            })
            
            self.logger.info("Instalação concluída com sucesso!")
            return True
            
        except Exception as e:
            self.logger.critical(f"Falha na instalação: {str(e)}")
            return False