import subprocess
import time

class StreamPlayer:
    def __init__(self, url, check_interval=5, precheck_duration=5):
        self.url = url
        self.check_interval = check_interval
        self.precheck_duration = precheck_duration
        self.mpg123_cmd = ["mpg123", "-o", "alsa", "-a", "default", "--quiet", self.url]

    def try_play_stream(self):
        try:
            print(f"🔎 Test du stream {self.url}...")
            process = subprocess.Popen(
                self.mpg123_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            time.sleep(self.precheck_duration)

            if process.poll() is not None:
                print("⚠️ Stream inactif ou vide. mpg123 s'est arrêté prématurément.")
                return False
            else:
                print("✅ Stream actif. Lecture en cours.")
                process.wait()
                return True
        except KeyboardInterrupt:
            print("\n🛑 Interruption manuelle.")
            return False
        except Exception as e:
            print(f"❌ Erreur pendant la lecture du stream : {e}")
            return False

    def run(self):
        print("🎧 Surveillance du stream en cours...")

        while True:
            active = self.try_play_stream()
            if not active:
                print(f"⏳ Nouvelle tentative dans {self.check_interval} secondes...\n")
                time.sleep(self.check_interval)
            else:
                print("🔁 Lecture terminée ou interrompue. Reprise de la surveillance.\n")


if __name__ == "__main__":
    watcher = StreamPlayer("http://localhost:8000/stream")
    watcher.run()
