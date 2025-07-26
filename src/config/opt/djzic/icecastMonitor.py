#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
import json
import time

# === CONFIG ===
SERVERS = XXXXXXXXXXX 
PORT = 8000
OUTPUT_FILE = "/var/www/html/admin/data/stats.json"
PEAKS_FILE = "/tmp/icecast_peaks.json"
SLEEP_SECONDS = 30


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

def query_icecast(ip, user="admin", password="hackme"):
    url = f"http://{ip}:{PORT}/admin/stats"
    try:
        r = requests.get(url, auth=(user, password), timeout=3)
        r.raise_for_status()
        root = ET.fromstring(r.content)

        listeners = 0
        peak = 0

        for source in root.findall(".//source"):
            l = int(source.findtext("listeners", "0"))
            p = int(source.findtext("listener_peak", "0"))
            listeners += l
            peak += p

        return {"listeners": listeners, "peak": peak}
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return {"listeners": 0, "peak": 0}

def main():
    while True:
        peaks = load_json(PEAKS_FILE)
        data = {"servers": {}, "timestamp": time.time()}

        global_peak = 0
        global_current = 0

        for ip in SERVERS:
            stats = query_icecast(ip)
            prev_peak = peaks.get(ip, 0)
            updated_peak = max(prev_peak, stats["listeners"])

            peaks[ip] = updated_peak
            data["servers"][ip] = {
                "listeners": stats["listeners"],
                "peak": updated_peak
            }

            global_current += stats["listeners"]
            global_peak = max(global_peak, updated_peak)

        # Update persistent global_max
        stored_max = peaks.get("_global_max", 0)
        new_global_max = max(stored_max, global_current)
        peaks["_global_max"] = new_global_max

        data["global_current"] = global_current
        data["global_peak"] = global_peak
        data["global_max"] = new_global_max

        save_json(PEAKS_FILE, peaks)
        save_json(OUTPUT_FILE, data)

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()

    time.sleep(SLEEP_SECONDS)
