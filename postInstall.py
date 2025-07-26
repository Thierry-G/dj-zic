import json
import os
from pathlib import Path
import subprocess
from lib_install.colors import printColored, colorText

def ssh_connect_auto(user, ip):
    """Fully automated SSH connection with zero user interaction"""
    key_path = f"/home/{user}/.ssh/id_rsa_djzic"
    known_hosts = f"/home/{user}/.ssh/known_hosts"
    
    # Ensure .ssh directory exists
    os.makedirs(os.path.dirname(known_hosts), exist_ok=True)
    
    # Non-interactively add host key to known_hosts
    try:
        # First try to remove any existing entry (ignore if not found)
        subprocess.run(
            ["ssh-keygen", "-R", ip, "-f", known_hosts],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )  # Don't check return code since failure is expected if key doesn't exist
        
        # Add new entry without verification
        result = subprocess.run(
            ["ssh-keyscan", "-H", ip],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )
        
        # Write directly without verification
        with open(known_hosts, "a") as kh:
            kh.write(result.stdout)
            
    except subprocess.CalledProcessError as e:
        if "ssh-keyscan" in str(e.cmd):
            print(f"❌ Failed to scan host key: {e.stderr.strip()}")
        else:
            print(f"❌ Unexpected error: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"❌ Host key setup error: {e}")
        return False

    # Test connection with strict settings
    command = [
        "ssh",
        "-i", key_path,
        "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=" + known_hosts,
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=5",
        f"{user}@{ip}",
        "exit"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ SSH connection successful")
            return True
        print(f"❌ SSH failed (code {result.returncode}): {result.stderr.strip()}")
        return False
    except subprocess.TimeoutExpired:
        print("⌛ SSH connection timed out")
        return False
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return False
    
def getIpv4(interface):
    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show", interface],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.split("\n"):
            if "inet " in line:
                return line.split()[1].split("/")[0]  # Extract IP address
    except subprocess.CalledProcessError:
        return "Invalid interface or command failed"

    return None

def main():
    relays = []
    confFile = Path(__file__).parent.resolve()
    printColored("Run this script with all devices up and running.","YELLOW")
    try:
        with open(f"{confFile}/djzic_Install.json", 'r') as f:
            data = json.load(f)

        lang = data['lang']
        wlan = data['wlan']
        user = data['user']
        devices = data['servers']

        currDevice = getIpv4('wlan0')
        for ip in devices:
            if ip != currDevice:
                print(f"Registering {currDevice} -> {ip}")
                ssh_connect_auto(user,ip)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()