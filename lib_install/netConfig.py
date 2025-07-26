import re
import shutil
import subprocess

from lib_install import config, utils, system
from lib_install.colors import printColored, colorText

def setNetwork():
    if config.wlan == "wlan1":
        wlan0IBBS()
        wlan1Network()
        printColored(f"✓ {config.lang.msg['wlan1Net']}","GREEN")
        dnsmasqConf()
        hostapdConf()
        wlan1WpaConf()
        setIpTables()
        setResolvConf()
    else:
        if config.type != 'single':
            wlan0Network()
        else:
            soloNetwork()
        
        printColored(f"✓ {config.lang.msg['wlan0Net']}","GREEN")
        dnsmasqConf()
        hostapdConf()
        setResolvConf()
        if config.type != 'single':
            wlan0WpaConf()
    utils.copyFile(f"{config.SCRIPT_DIR}/src/config/etc/systemd/network/20-eth0-dhcp.network","/etc/systemd/network/20-eth0-dhcp.network")
    enableIpForward()
    confIcecast2()

def soloNetwork():
    wlanNet = f"{config.temp}/10-wlan0.network"
    with open(wlanNet , 'w') as f:
        f.write("[Match]\n")
        f.write("Name=wlan0\n\n")
        f.write("[Network]\n")
        f.write(f"Address=10.1.{config.id}.1/24\n")
        f.write("IPForward=yes\n")
        f.write(f"Gateway=10.1.{config.id}.1\n\n")
        f.write("[Route]\n")
        f.write("Destination=10.0.0.0/8\n")
        f.write(f"Gateway=10.1.{config.id}.1\n")
    utils.copyFile(wlanNet, "/etc/systemd/network/10-wlan0.network")

def setIpTables():
    system.runSysctl(['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-s', '10.2.0.0/16', '-o', 'wlan0', '-j', 'MASQUERADE'])
    system.runSysctl(['sudo', 'iptables', '-A', 'FORWARD', '-i', 'wlan1', '-o', 'wlan0', '-j', 'ACCEPT'])
    system.runSysctl(['sudo', 'iptables', '-A', 'FORWARD', '-i', 'wlan0', '-o', 'wlan1', '-m', 'state', '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'])
    
    try:
        subprocess.run("sudo iptables-save | sudo tee /etc/iptables/rules.v4", shell=True, check=True)
        print("iptables rules saved successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to save iptables rules: {e}")

    printColored(f"✓ {config.lang.msg['iptables']}","GREEN") 

def wlan0WpaConf(): 
    wpaFile = f"{config.temp}/wpa_supplicant-wlan0.conf"
    with open(wpaFile , 'w') as file:
        file.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
        file.write("update_config=1\n")
        file.write(f"country={config.WIFI_COUNTRY}\n\n")
        file.write("network={\n")
        file.write("    ssid=\"dj.zic\"\n")
        file.write(f"   psk=\"{config.WIFI_PASS}\"\n")
        file.write("}\n")
    utils.copyFile(wpaFile,"/etc/wpa_supplicant/wpa_supplicant-wlan0.conf")
    
    wpaService = f"{config.temp}/wpa_supplicant@wlan0.service"
    with open(wpaService,'w') as file:
        file.write("[Unit]\n")
        file.write("Description=WPA supplicant for wlan0\n")
        file.write("Wants=network.target\n")
        file.write("Before=network.target\n\n")
        file.write("[Service]\n")
        file.write("Type=simple\n")
        file.write("ExecStart=/sbin/wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant-wlan0.conf -i wlan0\n")
        file.write("Restart=always\n\n")
        file.write("[Install]\n")
        file.write("WantedBy=multi-user.target\n")
    utils.copyFile(wpaService, "/etc/systemd/system/wpa_supplicant@wlan0.service")
    printColored(f"✓ {config.lang.msg['wpa']}","GREEN") 

def wlan1WpaConf():
    frequency =  "5180" # 4G:  "2412"
    wpaFile = f"{config.temp}/wpa_supplicant-wlan0.conf"
    with open(wpaFile,'w') as f:
        f.write("ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev\n")
        f.write("update_config=1\n")
        f.write("p2p_disabled=1\n")
        f.write(f"country={config.WIFI_COUNTRY}\n")
        f.write("ap_scan=2\n\n")
        f.write("network={\n")
        f.write("\tssid=\"IBSS-DJzicNet\n")
        f.write("\tkey_mgmt=WPA-PSK\n")
        f.write("\tproto=RSN\n")
        f.write(f"\tpsk=\"{config.IBSS_PSK}\"\n")
        f.write("\tmode=1\n")
        f.write("\tfrequency=2412\n")
        f.write("}\n")
    utils.copyFile(wpaFile,"/etc/wpa_supplicant/wpa_supplicant-wlan0.conf")
            
    wpaService = f"{config.temp}/wpa_supplicant@wlan0.service"
    with open(wpaService,'w') as f:
        f.write("[Unit]\n")
        f.write("Description=Ad-hoc (IBSS) interface\n")
        f.write("Requires=sys-subsystem-net-devices-%i.device\n")
        f.write("After=sys-subsystem-net-devices-%i.device\n")
        f.write("Before=network.target\n")
        f.write("Wants=network-pre.target\n")

        f.write("[Service]\n")
        f.write(f"Environment=\"SSID=IBSS-DJzicNet\" \"FREQUENCY={frequency}\"\n")
        f.write("Type=oneshot\n")
        f.write("RemainAfterExit=yes\n")
        f.write("ExecStartPre=/bin/ip link set %i up\n")
        f.write("ExecStartPre=/sbin/iw %I set type ibss\n")
        f.write("ExecStart=/sbin/iw %I ibss join $SSID $FREQUENCY\n")
        f.write("ExecStopPost=-/sbin/iw dev %I ibss leave\n")
        f.write("ExecStopPost=-/sbin/iw %I set type managed\n\n")
        f.write("[Install]\n")
        f.write("WantedBy=network.target\n")
    utils.copyFile(wpaService, "/etc/systemd/system/wpa_supplicant@wlan0.service")
    printColored(f"✓ {config.lang.msg['wpa']}","GREEN")

def hostapdConf():
    hostapd = f"{config.temp}/hostapd.conf"
    with open(hostapd , 'w') as f:
        f.write("ctrl_interface=/var/run/hostapd\n")
        f.write("ctrl_interface_group=0\n")
        f.write(f"interface={config.wlan}\n")
        f.write("ieee80211n=1\n")
        f.write("ssid=dj.zic\n")
        f.write("hw_mode=g\n")
        f.write(f"channel={config.curr['channel']}\n")
        f.write("wpa=2\n")
        f.write(f"wpa_passphrase={config.WIFI_PASS}\n")
        f.write("wpa_key_mgmt=WPA-PSK\n")
        f.write("wpa_pairwise=TKIP\n")
        f.write("rsn_pairwise=CCMP\n")
        f.write(f"country_code={config.WIFI_COUNTRY}\n")
    utils.copyFile(hostapd, "/etc/hostapd/hostapd.conf")
    printColored(f"✓ {config.lang.msg['hostapd']}","GREEN")
     
def dnsmasqConf():
    dnsmasq = f"{config.temp}/dnsmasq.conf"
    with open(dnsmasq , 'w') as f:
        f.write("domain-needed\n")
        f.write("bogus-priv\n")
        f.write("no-resolv\n")
        f.write("expand-hosts\n\n")
        f.write(f"listen-address=::1,127.0.0.1,10.1.{config.id}.1\n\n")
        f.write("domain=zic\n")
        f.write("local=/zic/\n")
        if config.wlan == 'wlan0' and config.num >=1:
            f.write("conf-file=/etc/djzic.conf\n")
            makeConfile(config.num)
        if config.type == 'single':
            f.write("local-ttl=5\n")
            f.write(f"address=/dj.zic/10.1.{config.id}.1\n")
        if config.wlan == 'wlan1':
            f.write("localise-queries\n")
            f.write("interface=wlan1\n")
            f.write("bind-interfaces\n")
            f.write(f"dhcp-range=10.2.{config.id}.50,10.2.{config.id}.200,12h\n")
            f.write(f"dhcp-option=6,10.2.{config.id}.1\n")
            f.write(f"dhcp-option=121,10.1.0.0/24,10.2.{config.id}.1\n")
            f.write(f"address=/dj.zic/10.1.{config.id}.1\n")
        else:
            f.write("interface=wlan0\n")
            f.write(f"dhcp-range=10.1.{config.id}.50,10.1.{config.id}.200,12h\n") 
            
    utils.copyFile(dnsmasq, "/etc/dnsmasq.conf")
    system.createSystemdOverride("dnsmasq", """\
[Unit]
After=network-online.target
Wants=network-online.target
""")
    printColored(f"✓ {config.lang.msg['dnsmasq']}","GREEN")

def makeConfile(num):
    djconf = f"{config.temp}/djzic.conf"
    with open(djconf , 'w') as f:
        for i in range (1, num +1):
            if i==0: continue
            f.write(f"address=/dj.zic/10.1.{i}.1\n")
    utils.copyFile(djconf,"/etc/djzic.conf")

def wlan1Network():
    wlanNet = f"{config.temp}/10-wlan1.network"    
    with open(wlanNet,'w') as f:
        f.write("[Match]\n")
        f.write("Name=wlan1\n\n")
        f.write("[Network]\n")
        f.write(f"Address=10.2.{config.id}.1/24\n")
        f.write("IPForward=yes\n")
        f.write("RequiredForOnline=no\n\n")
    utils.copyFile(wlanNet, "/etc/systemd/network/10-wlan1.network")
     
def wlan0IBBS():
    wlanNet = f"{config.temp}/10-wlan0.network"
    with open(wlanNet,'w') as f:
        f.write("[Match]\n")
        f.write("Name=wlan0\n\n")
        f.write("[Network]\n")
        f.write(f"Address=10.1.{config.id}.1/16\n")
        f.write("IPForward=yes\n")
        f.write("MulticastDNS=yes\n")
        f.write("LinkLocalAddressing=no\n")
        f.write("RequiredForOnline=no\n")
    utils.copyFile(wlanNet, "/etc/systemd/network/10-wlan0.network")
 
def wlan0Network():
    wlanNet = f"{config.temp}/10-wlan0.network"
    with open(wlanNet , 'w') as f:
        f.write("[Match]\n")
        f.write("Name=wlan0\n\n")
        f.write("[Network]\n")
        f.write(f"Address=10.1.{config.id}.1/16\n")
        f.write(f"Gateway=10.1.{config.id}.1\n\n")
        f.write("[Route]\n")
        f.write("Destination=10.0.0.0/8\n")
        f.write(f"Gateway=10.1.{config.id}.1\n")
        if config.wlan == 'wlan1':
            f.write("\n[Route]\n")
            f.write(f"Destination=10.2.{config.id}.0/16")
            f.write(f"Gateway=10.1.{config.id}.1\n") 
    utils.copyFile(wlanNet, "/etc/systemd/network/10-wlan0.network")
    
def enableIpForward():
    step = "ipForward"
    if utils.stepIsDone(step):
        return False
    else:
        sysctlConf = "/etc/sysctl.conf"
        
        utils.backupFile(sysctlConf)
        pattern = re.compile(r'^\s*#?\s*net\.ipv4\.ip_forward\s*=\s*\d+')
    
        try:
            with open(sysctlConf, "r") as f, open(sysctlConf + ".tmp", "w") as temp_f:
                line_found = False
                for line in f:
                    if pattern.match(line):
                        temp_f.write("net.ipv4.ip_forward=1\n")
                        line_found = True
                    else:
                        temp_f.write(line)

                if not line_found:
                    temp_f.write("\nnet.ipv4.ip_forward=1\n")
            shutil.move(sysctlConf + ".tmp", sysctlConf)    
            print(
                colorText(f"✓ {config.lang.msg['ipForward']} :", "GREEN"),
                colorText(f"{sysctlConf}", None)
            )
            utils.markDone(step)
        
        except Exception as e:
            print(
                colorText(f"✗ {config.lang.msg['errorOccured']} :", "RED"),
                colorText(f"{sysctlConf}: {e}", None)
            )

def confIcecast2():
    dest = '/etc/icecast2/icecast.xml'
    utils.backupFile(dest)
    if config.type != 'relay':  
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/etc/icecast2/icecast-master.xml",dest)    
    else:
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/etc/icecast2/icecast-relay.xml",dest)
    
    import xml.etree.ElementTree as ET

    tree = ET.parse(dest)
    root = tree.getroot()
    
    changes = {
        "source-password": f"{config.ICECAST_PASS}",
        "relay-password": f"{config.ICECAST_PASS}",
        "admin-user": f"{config.ICECAST_ADMIN}",
        "admin-password": f"{config.ICECAST_PASS}"
    }
    
    for tag, new_value in changes.items():
        for elem in root.iter(tag):
            elem.text = new_value
    tree.write(dest)

def setResolvConf():
    source = "/etc/resolv.conf"
    utils.backupFile(source)
    with open(source,'w') as f:
        f.write("nameserver 127.0.0.1\n")
        f.write("nameserver 1.1.1.1\n")
        f.write("nameserver 8.8.4.4\n")