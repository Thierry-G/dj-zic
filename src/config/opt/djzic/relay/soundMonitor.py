import numpy as np
import subprocess
import time
import checkServices as cs
from silenceDetector import SilenceDetector
from threading import Thread


class SoundMonitor:
    def __init__(self, enable_logging=True):
        self.Silence_Detector = SilenceDetector()
        self.SERVICES = cs.CheckServices()
        self.last_status = None
        self.last_sound_status = None
    
    def monitorServices(self):
        while True:
            try:
                services_status = self.SERVICES.get_services_status()
                stream_status = self.SERVICES.get_stream_status()
                if self.last_sound_status == "inactive":
                    out = self.last_sound_status
                else :
                    out = "silent" if self.last_sound_status else "active"
                

                current_status = {
                    "sound": out,
                    "services": services_status,
                    "stream": stream_status
                }

                print(current_status)
                
                if current_status != self.last_status:
                    self.SERVICES.write_status(self.last_sound_status, services_status)
                    print(f"ℹ️ Services status updated: {services_status}")
                    self.last_status = current_status

                time.sleep(0.5)  # Check services every 0.5 seconds
            except Exception as e:
                print(f"❌ Error in monitorServices: {e}")
                time.sleep(0.7)

    def monitorSound(self):
        sndInterface = "loopin"
        arecord_cmd = [
           "sudo", "arecord", "-D", sndInterface, "-f", "S16_LE", "-c", "2", "-r", "48000", "-t", "raw"
        ]
        arecord_proc = subprocess.Popen(arecord_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            try:
                data = arecord_proc.stdout.read(self.Silence_Detector.CHUNK * 2 * 2)  # Read CHUNK samples, 2 bytes per sample, 2 channels
                if not data:
                    self.last_sound_status = 'inactive'
                    print("⚠️ No data read from arecord.")
                    break

                audio_data = np.frombuffer(data, dtype=np.int16)
                is_silent = self.Silence_Detector.is_silent(audio_data)
                print(f"ℹ️ Silence detected: {is_silent}, Last sound status: {self.last_sound_status}")
                
                if is_silent != self.last_sound_status and self.last_sound_status != "inactive":
                    print(f"ℹ️ Sound status updated: {'silent' if is_silent else 'active'}")
                    self.last_sound_status = is_silent

                time.sleep(0.1)  # Reduce CPU usage

            except Exception as e:
                print(f"❌ Error in monitorSound: {e}")
                time.sleep(0.7)

    def monitor(self):
        service_thread = Thread(target=self.monitorServices)
        service_thread.start()
        self.monitorSound()

if __name__ == "__main__":
    monitor = SoundMonitor()
    monitor.monitor()