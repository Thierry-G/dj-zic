import subprocess

def get_signal_info():
    output = subprocess.check_output(["iw", "dev", "wlan0", "link"]).decode()
    print(output)  # Parse based on actual fields you need
