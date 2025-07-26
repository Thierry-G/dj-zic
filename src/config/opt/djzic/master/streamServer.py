import subprocess
import time
import os
import signal
import sys
import logging
import threading

class StreamServer:
    def __init__(self, enable_logging=True):
        """
        Commands:
        - ffmpeg: Streams audio to an Icecast server.
        - mpg123: Plays audio from the Icecast stream.
             self.ffmpeg_cmd = [
            'ffmpeg', '-f', 'alsa', '-i', 'plughw:2,0', '-use_wallclock_as_timestamps', '1', '-c:a', 'libmp3lame', '-b:a', '320k','-content_type', 'audio/mpeg', '-f', 'mp3', 'icecast://source:hackme@localhost:8000/stream'
        ]
        """
        self.ffmpeg_cmd = [
            'ffmpeg', 
            '-f', 'alsa',
            '-i', 'plughw:2,0',
            '-use_wallclock_as_timestamps', '1',
            '-c:a', 'libmp3lame',
            '-b:a', '320k',
            '-content_type', 'audio/mpeg',
            '-f', 'mp3', 'icecast://source:hackme@localhost:8000/stream'
        ]
        self.mpg123_cmd = ['mpg123', '-o', 'alsa', '-a', 'default', 'http://localhost:8000/stream']
        self.ffmpeg_process = None
        self.mpg123_process = None
        self.setup_logging(enable_logging)

    def setup_logging(self, enable_logging):
        """Sets up logging to file and console."""
        self.logger = logging.getLogger(__name__)
        if enable_logging:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            # Create a file handler
            file_handler = logging.FileHandler('/opt/djZic/log/streamServer.log')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            # Add the file handler to the logger
            self.logger.addHandler(file_handler)
        else:
            self.logger.addHandler(logging.NullHandler())

    def start(self):
        """Starts the ffmpeg and mpg123 processes."""
        try:
            self.logger.info("Starting ffmpeg...")
            self.ffmpeg_process = subprocess.Popen(self.ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log_process_output(self.ffmpeg_process, "ffmpeg")
            time.sleep(5)  # Wait for ffmpeg to start

            self.logger.info("Starting mpg123...")
            self.mpg123_process = subprocess.Popen(self.mpg123_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log_process_output(self.mpg123_process, "mpg123")
        except Exception as e:
            self.logger.error(f"Error starting processes: {e}")
            self.stop()

    def log_process_output(self, process, name):
        """Logs process output using threads."""
        def log_output(stream, log_func):
            try:
                for line in iter(stream.readline, b''):
                    log_func(f"{name}: {line.decode().strip()}")
            finally:
                stream.close()

        stdout_thread = threading.Thread(target=log_output, args=(process.stdout, self.logger.info), daemon=True)
        stderr_thread = threading.Thread(target=log_output, args=(process.stderr, self.logger.error), daemon=True)
        stdout_thread.start()
        stderr_thread.start()

    def stop(self):
        """Stops the ffmpeg and mpg123 processes."""
        if self.ffmpeg_process:
            self.logger.info("Stopping ffmpeg...")
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("ffmpeg did not terminate gracefully, killing it...")
                self.ffmpeg_process.kill()

        if self.mpg123_process:
            self.logger.info("Stopping mpg123...")
            self.mpg123_process.terminate()
            try:
                self.mpg123_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("mpg123 did not terminate gracefully, killing it...")
                self.mpg123_process.kill()

    def restart(self):
        """Restarts the StreamServer."""
        self.logger.info("Restarting StreamServer...")
        self.stop()
        time.sleep(2)  # Wait briefly before restarting
        self.start()

    def run(self):
        """Runs the server and handles termination signals."""
        self.start()
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received. Stopping server...")
            self.stop()

    def handle_signal(self, signum, frame):
        """Handles system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, stopping...")
        self.stop()
        sys.exit(0)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-logging', action='store_true', help='Disable logging')
    args = parser.parse_args()
    server = StreamServer(enable_logging=not args.no_logging)
    server.run()
