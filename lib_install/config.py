from pathlib import Path

"""
Change default values and passwords below:
"""
ICECAST_ADMIN = "admin"
ICECAST_PASS = "hackme"
WIFI_PASS = "p@$$w0rD"
WIFI_COUNTRY = "FR"
WEB_ADMIN = "admin"
WEB_PASS = "hackme"
IBSS_PSK = "verySecretPassword"

# No change below this line ####################
SCRIPT_DIR = Path(__file__).parent.parent.resolve()
langCode = "fr"
lang = None
user = None
temp = None
type = None
num = 0
wlan = None
id = None
curr = None
isLast = False
servers = None
installConf = {}