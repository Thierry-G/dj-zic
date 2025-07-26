import subprocess
import json
import logging
from pathlib import Path
import loggerConfig

class CheckServices:
    def __init__(self, enable_logging=True):
        self.OUTPUT_FILE = Path("/var/www/html/data/status.json")
        self.STREAM_FILE = Path("/var/www/html/data/stream.json")
        self.CONFIG_FILE = Path("/var/www/html/admin/data/config.json")
        self.stream_content = {}
        self.logger = loggerConfig.setup_logging(enable_logging=enable_logging)
        self.enable_logging = enable_logging

    def check_service_status(self, service_name):
        try:
            cmd = f"systemctl is-active {service_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return 1 if result.stdout.strip() == "active" else 0
        except Exception as e:
            self.logger.error(f"Checkservice {e}")
            return 0
        
    def get_stream_status(self):
        if self.STREAM_FILE.exists():
            with open(self.STREAM_FILE, "r") as f:
                stream_content = json.load(f)
        else:
            stream_content = {}
        return stream_content

    def get_services_status(self):
        services = ["icecast2", "djZic-stream", "djZic-status", "dnsmasq", "lighttpd", "hostapd"]
        return {service: self.check_service_status(service) for service in services}

    def write_status(self, is_silent, services_status):
        if self.enable_logging:  # Only log if enabled
            self.logger.info(f"Updating status: is_silent={is_silent}, services_status={services_status}")
        status = {
            "sound": "silent" if is_silent else "active",
            "services": services_status,
        }
        if self.OUTPUT_FILE.exists():
            with open(self.OUTPUT_FILE, "r") as f:
                existing_content = json.load(f)
        else:
            existing_content = {}

        existing_content.update(status)

        current_stream = self.get_stream_status()
        if current_stream != self.stream_content:
            existing_content.update(current_stream)
            self.stream_content = current_stream

        with open(self.OUTPUT_FILE, "w") as f:
            json.dump(existing_content, f)
        self.logger.info(f"Status written to {self.OUTPUT_FILE}")
