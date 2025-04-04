import flet as ft
from pathlib import Path
import logging
from core.send_queue import SendQueue
from utils.validators import validate_phone_number

class MainApp(ft.UserControl):
    def __init__(self, api_client, queue):
        super().__init__()
        self.api_client = api_client
        self.queue = queue
        self.logger = logging.getLogger('UI')
        
        # Elementos da UI
        self.phone_field = ft.TextField(
            label="Número do WhatsApp",
            hint_text="Ex: 16991080895",
            prefix_text="55",
            max_length=13,
            on_change=self._validate_phone
        )
        
        self.message_field = ft.TextField(
            label="Mensagem (opcional)",
            multiline=True
        )
        
        self.file_picker = ft.FilePicker(
            on_result=self._file_picked
        )
        
        self.progress = ft.ProgressBar(
            visible=False,
            width=300
        )

    def _validate_phone(self, e):
        if validate_phone_number(e.control.value):
            e.control.error_text = None
        else:
            e.control.error_text = "Número inválido (apenas números, 13 dígitos)"
        self.update()

    def _file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            pdf_path = Path(e.files[0].path)
            self.queue.add_task({
                'number': self.phone_field.value,
                'pdf_path': pdf_path,
                'message': self.message_field.value
            })
            self._show_snackbar(f"Arquivo {pdf_path.name} adicionado à fila!")

    def build(self):
        return ft.Column(
            controls=[
                ft.Row([
                    self.phone_field,
                    self.message_field
                ]),
                ft.ElevatedButton(
                    "Selecionar PDF e Enviar",
                    on_click=lambda _: self.file_picker.pick_files(
                        allowed_extensions=["pdf"],
                        allow_multiple=False
                    )
                ),
                self.progress,
                self.file_picker
            ]
        )