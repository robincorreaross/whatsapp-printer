import logging
import os
from pathlib import Path
from datetime import datetime
import flet as ft

class LoggingManager:
    def __init__(self, log_file: Path = Path("logs/app.log"), ui_container: ft.Column = None):
        self.log_file = log_file
        self.ui_container = ui_container
        
        # Criar estrutura de diretórios
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configurar logger base
        self.logger = logging.getLogger("WhatsAppPrinter")
        self.logger.setLevel(logging.DEBUG)

        # Formato comum
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para arquivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Handler customizado para UI
        if ui_container:
            ui_handler = self.UIHandler(ui_container)
            ui_handler.setFormatter(formatter)
            self.logger.addHandler(ui_handler)

    class UIHandler(logging.Handler):
        def __init__(self, container: ft.Column):
            super().__init__()
            self.container = container
            self.level_map = {
                logging.INFO: ("blue", "ℹ"),
                logging.SUCCESS: ("green", "✓"),
                logging.WARNING: ("orange", "⚠"),
                logging.ERROR: ("red", "✗")
            }
            
            # Adiciona nível customizado SUCCESS
            logging.addLevelName(25, "SUCCESS")

        def emit(self, record):
            color, icon = self.level_map.get(record.levelno, ("black", ""))
            log_entry = ft.Text(
                value=f"{self.format(record)}",
                color=color,
                selectable=True
            )
            self.container.controls.append(log_entry)
            self.container.update()

    def setup_success_level(self):
        success_level = 25
        logging.addLevelName(success_level, "SUCCESS")
        
        def success(self, message, *args, **kwargs):
            if self.isEnabledFor(success_level):
                self._log(success_level, message, args, **kwargs)
        
        logging.Logger.success = success

    def cleanup_old_logs(self, days=7):
        # Implementar rotação de logs
        pass