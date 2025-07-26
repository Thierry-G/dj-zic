import subprocess
import re
import math

# 🔐 Your known hostnames (ESSIDs) on IBSS-DJzic
my_devices = {
    "dj-master",
    "dj-relay1"
}

def scan_ibss():
    try:
        result = subprocess.check_output(['iwlist', 'wlan0', 'scan'], stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        print("Scan failed:", e.output.decode('utf-8'))
        return []

    blocks = re.split(r'Cell \d+ - ', result)[1:]
    known = []
    #unknown = []

    for block in blocks:
        essid_match = re.search(r'ESSID:"([^"]+)"', block)
        signal_match = re.search(r'Signal level=(-?\d+) dBm', block)

        if essid_match and signal_match:
            essid = essid_match.group(1)
            rssi = int(signal_match.group(1))
            distance = estimate_distance(rssi)

            if essid in my_devices:
                known.append((essid, distance))
            else:
                continue
                unknown.append((essid, distance))

    return known #, unknown

def estimate_distance(rssi, tx_power=-30, path_loss_exponent=3.0):
    return round(10 ** ((tx_power - rssi) / (10 * path_loss_exponent)), 2)

def main():
    known = scan_ibss()
    #known, unknown = scan_ibss()

    if not known: #and not unknown:
        print("No IBSS-DJzic devices detected.")
        return

    print("📡 Distances to Known IBSS-DJzic Devices:\n")
    for essid, dist in known:
        print(f"{essid:<25} → {dist:.2f} meters")
    """
    if unknown:
        print("\n❓ Unknown Devices Nearby:\n")
        for essid, dist in unknown:
            print(f"{essid:<25} → {dist:.2f} meters")
    """
if __name__ == "__main__":
    main()
