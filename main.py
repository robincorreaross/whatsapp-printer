import flet as ft
import logging
from pathlib import Path
from core.api_client import WhatsAppAPIClient
from core.send_queue import SendQueue
from ui.main_window import MainApp
from core.logging_manager import LoggingManager
from config.config_manager import ConfigManager
from utils.file_manager import FileManager
from utils.validators import Validators

def main(page: ft.Page):
    # Configuração inicial da página
    page.title = "WhatsApp Printer"
    page.window_width = 800
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Carregar configurações
    config = ConfigManager()
    if not config.validate_current_config():
        show_config_error(page)
        return

    # Sistema de logging
    log_container = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
        height=200
    )
    logger = LoggingManager(ui_container=log_container)

    # Gerenciador de arquivos
    file_manager = FileManager()

    # Cliente API
    api_client = WhatsAppAPIClient(
        server_url=config.load_config().get("server_url"),
        instance=config.load_config().get("instance"),
        api_key=config.load_config().get("api_key")
    )

    # Validar conexão com a API
    if not Validators.api_credentials(
        api_client.base_url,
        config.load_config().get("instance"),
        config.load_config().get("api_key")
    ):
        logger.logger.error("Credenciais da API inválidas")
        show_api_error(page)
        return

    # Sistema de filas
    send_queue = SendQueue(
        api_client=api_client,
        max_workers=config.load_config().get("max_workers", 3)
    )

    # Interface principal
    main_ui = MainApp(api_client, send_queue)
    
    # Layout completo
    page.add(
        ft.Column(
            [
                ft.Text("WhatsApp Printer", size=30, weight=ft.FontWeight.BOLD),
                main_ui,
                ft.Divider(),
                ft.Text("Logs do Sistema:", weight=ft.FontWeight.BOLD),
                log_container
            ],
            spacing=20,
            expand=True
        )
    )

    # Limpeza ao fechar
    page.window_prevent_close = True
    page.on_window_event = lambda e: on_window_event(e, page, file_manager)

def show_config_error(page: ft.Page):
    page.add(
        ft.AlertDialog(
            title=ft.Text("Configuração Necessária"),
            content=ft.Text("Por favor, execute o instalador e configure a API primeiro."),
            open=True
        )
    )

def show_api_error(page: ft.Page):
    page.add(
        ft.AlertDialog(
            title=ft.Text("Erro de Conexão"),
            content=ft.Text("Não foi possível conectar à API do WhatsApp. Verifique as credenciais."),
            open=True
        )
    )

def on_window_event(event: ft.ControlEvent, page: ft.Page, file_manager: FileManager):
    if event.data == "close":
        # Limpeza final
        file_manager.cleanup_temp_files()
        page.window_destroy()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")