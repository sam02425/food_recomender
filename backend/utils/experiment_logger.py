import csv
import os
from datetime import datetime

class ExperimentLogger:
    def __init__(self, file_path, logger_instance=None):
        self.file_path = file_path
        self.logger = logger_instance
        # Ensure the file exists and has a header
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'event', 'data'])

    def log(self, event, data):
        with open(self.file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), event, data])
        if self.logger:
            self.logger.info(f"Experiment event logged: {event} - {data}")