import threading
import queue
import logging
from pathlib import Path
from typing import Dict

class SendQueue:
    def __init__(self, api_client, max_workers=3):
        self.task_queue = queue.Queue()
        self.api_client = api_client
        self.max_workers = max_workers
        self.logger = logging.getLogger('SendQueue')
        self._init_workers()

    def _init_workers(self):
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._process_queue)
            worker.daemon = True
            worker.start()

    def _process_queue(self):
        while True:
            task = self.task_queue.get()
            try:
                success = self.api_client.send_pdf(
                    number=task['number'],
                    pdf_path=task['pdf_path'],
                    message=task['message']
                )
                
                if success:
                    task['status'] = 'completed'
                else:
                    task['status'] = 'failed'
                    
            except Exception as e:
                self.logger.error(f"Erro no worker: {str(e)}")
                task['status'] = 'error'
            finally:
                self.task_queue.task_done()

    def add_task(self, task_data: Dict):
        self.task_queue.put(task_data)
        self.logger.info(f"Nova tarefa adicionada à fila: {task_data['pdf_path'].name}")