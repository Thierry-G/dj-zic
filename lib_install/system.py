import os
from pathlib import Path
import subprocess
import sys
from lib_install import config, utils
from lib_install.colors import printColored, colorText

def updateHostname(new_name):
    path = '/etc/hosts'
    updated = False
    new_line = f"127.0.1.1\t{new_name}\n"
    lines = []

    with open(path, 'r') as f:
        for line in f:
            if line.startswith("127.0.1.1"):
                lines.append(new_line)
                updated = True
            else:
                lines.append(line)

    if not updated:
        lines.append(new_line)

    with open(path, 'w') as f:
        f.writelines(lines)

    subprocess.run(["hostnamectl", "set-hostname", new_name], check=True)
    print(f"✅ Hostname changed to: {new_name}")

def setUpDefault():
   
    runSysctl(['sudo', 'rfkill', 'block', 'bluetooth'])
    runSysctl(['sudo', 'systemctl', 'stop', 'bluetooth.service'])
    runSysctl(['sudo', 'systemctl', 'disable', 'bluetooth.service'])
    runSysctl(['sudo', 'systemctl', 'enable', '--now', 'systemd-networkd'])
    runSysctl(['sudo', 'systemctl', 'disable', '--now', 'NetworkManager'])
    runSysctl(['sudo', 'systemctl', 'mask', 'NetworkManager'])
    runSysctl(['sudo', 'rfkill', 'unblock', 'wifi'])
 
def setWlan0Default():
    createSystemdOverride("hostapd", """\
[Unit]
Requires=systemd-networkd.service
After=systemd-networkd.service
""")
    createSystemdOverride("dnsmasq", """\
[Unit]
After=network-online.target
Wants=network-online.target
""")
    createSystemdOverride("icecast2", """\
[Unit]
After=network-online.target
Wants=network-online.target
""")
    createSystemdOverride("lighttpd", """\
[Unit]
After=icecast2.service
""")
    createSystemdOverride("wpa_supplicant@wlan0", """\
[Unit]
After=network.target
Wants=network.target
""")
    
    
def setWlan1Default():    
    createSystemdOverride("hostapd", """\
[Unit]
After=systemd-networkd.service
Requires=systemd-networkd.service
""")
    createSystemdOverride("dnsmasq", """\
[Unit]
After=network-online.target systemd-networkd.service hostapd.service
Wants=network-online.target systemd-networkd.service hostapd.service

[Service]
ExecStartPre=/bin/sleep 5
Restart=always
RestartSec=5
#StartLimitBurst=10
#StartLimitInterval=30
""")

def enableServices():
    if config.type != 'single':
        runSysctl(['systemctl', 'enable', 'wpa_supplicant@wlan0.service'],'wpa_supplicant@wlan0.service enabled successfully','Failed to enable wpa_supplicant@wlan0.service')
    #if config.wlan == 'wlan1':
    #    runSysctl(['systemctl', 'disable', 'systemd-networkd-wait-online.service'], 'systemd-networkd-wait-online.service successfully disabled','Failed to enable wpa_supplicant@wlan0.service')
    runSysctl(['systemctl', 'unmask', 'hostapd'],'Hostapd service unmasked successfully', 'Failed to unmask hostapd')
    runSysctl(['systemctl', 'enable', 'hostapd'],'Hostapd service enabled successfully','Failed to enable hostapd.service')
    runSysctl(['systemctl', 'enable', 'djZic-stream.service'],'djZic-stream service enabled successfully','Failed to enable djZic-stream.service')
    runSysctl(['systemctl', 'enable', 'djZic-status.service'], 'djZic-status service enabled successfully', 'Failed to enable djZic-status.service')
    runSysctl(['systemctl', 'enable', 'icecast-monitor.service'],'icecast-monitor.service enabled successfully','Failed to enable icecast-monitor.service')

def updateSudoers():
    sudoersFile = "/etc/sudoers.d/090_djZic"
    source = f"{config.SCRIPT_DIR}/src/config/etc/sudoers.d/090_djZic"
    utils.copyFile(source, sudoersFile )
    
    if config.type != 'single':
        lines = [
           f"www-data ALL=(ALL) NOPASSWD: /usr/bin/ssh -i /home/{config.user}/.ssh/id_rsa_djzic {config.user}@10.1.*.* *",
           f"www-data ALL=(ALL) NOPASSWD: /usr/local/bin/sync-uploads.sh *",
           "www-data ALL=(ALL) NOPASSWD: /usr/sbin/tcpdump",
           "www-data ALL=(ALL) NOPASSWD: /usr/sbin/arp -n"
        ]
        
        try:
            with open(sudoersFile, 'r') as f:
                content = f.readlines()
        except FileNotFoundError:
            print(f"❌ Sudoers file not found: {sudoersFile}")
            return False
        
        added_lines = []
        modified = False
        for line in lines:
            # Check if line already exists (ignore whitespace differences)
            line_exists = any(
                line.strip() == existing_line.strip()
                for existing_line in content
            )
            
            if not line_exists:
                # Ensure proper formatting
                formatted_line = line.strip() + '\n'
                
                # Add to content and record
                content.append(formatted_line)
                added_lines.append(formatted_line.strip())
                modified = True
        
        # Write back if modifications were made
        if modified:
            try:
                # Ensure file ends with newline
                if content and not content[-1].endswith('\n'):
                    content.append('\n')
                
                with open(sudoersFile, 'w') as f:
                    f.writelines(content)
                
                print("✓ Added sudoers rules:")
                for added_line in added_lines:
                    print(f"  - {added_line}")
                return True
            except Exception as e:
                print(f"❌ Failed to update sudoers file: {str(e)}")
                return False
        else:
            print("ℹ️ All sudoers rules already exist")
            return True

def installServices():
    source = f"{config.SCRIPT_DIR}/src/config/etc/systemd/system"
    if config.type == 'master':
        utils.copyFile(f"{source}/master-djZic-status.service","/etc/systemd/system/djZic-status.service")
        utils.copyFile(f"{source}/master-djZic-stream.service","/etc/systemd/system/djZic-stream.service")
    else:
        utils.copyFile(f"{source}/relay-djZic-status.service","/etc/systemd/system/djZic-status.service")
        utils.copyFile(f"{source}/relay-djZic-stream.service","/etc/systemd/system/djZic-stream.service")

def installIcecast():
    
    printColored(f"\n{config.lang.msg['icecast2Install']}","BLUE")
    
    preconfig_cmds = [
        "echo 'icecast2 icecast2/hostname string localhost' | sudo /usr/bin/debconf-set-selections",
        "echo 'icecast2 icecast2/admin_password password hackme' | sudo /usr/bin/debconf-set-selections",
        "echo 'icecast2 icecast2/admin_username string admin' | sudo /usr/bin/debconf-set-selections",
    ]
    
    for cmd in preconfig_cmds:
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            printColored(f"✗ {config.lang.msg['cliFailed']}: {e}","RED")
            return False

    # Non-interactive installation of Icecast2
    install_cmd = "sudo DEBIAN_FRONTEND=noninteractive apt install -y icecast2"
    result = subprocess.run(install_cmd, shell=True)
    if result.returncode == 0:
        printColored(f"✓ {config.lang.msg['icecast2Success']}","GREEN")
    else:
        printColored(f"✗ {config.lang.msg['icecast2Failed']}","RED")

def runSysctl(cmd, success_msg=None, error_msg=None):
    
    print( 
          colorText( f"\n{config.lang.msg['execute']}: ", "BLUE"),
          colorText( f"{' '.join(cmd)}\n", None)
    )
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        return_code = process.poll()
        if return_code == 0:
            message = success_msg if success_msg else config.lang.msg['clicompleted']
            print( 
                  colorText(f"✓ {message}", "GREEN") 
            )
            return True
        else:
            message = error_msg if error_msg else config.lang.msg['cliFailed']
            print(
                colorText(f"✗ {message}","RED") 
            )
            return False

    except Exception as e:
        print( colorText( f"✗ {config.lang.msg['errorOccured']}", "RED") +  str(e) )
        return False

def installPackages():
    step = "installPackages"
    
    if utils.stepIsDone(step):
        return
    else:
        PACKAGE_LIST = [
            "dnsmasq",
            "lighttpd",
            "qrencode",
            "php-fpm",
            "php-xml",
            "php-curl",
            "dnsutils",
            "hostapd",
            "libasound2-dev",
            "mpg123",
            "ffmpeg",
            "netcat-openbsd",
            "tcpdump",
            "fonts-noto-color-emoji"
        ]
        if config.wlan == "wlan1":
            PACKAGE_LIST.append("iptables")
        
        for package in PACKAGE_LIST:
            if not runSysctl(
                ["sudo", "apt", "install", "-y", package],
                success_msg=f"\n{package},  {config.lang.msg['packageSuccess']}",
                error_msg=f"\n{config.lang.msg['packageFailed']}: {package}."
            ): return False
        
        if config.wlan == "wlan1":
            runSysctl(
                ["sudo", "DEBIAN_FRONTEND=noninteractive", "apt", "install", "-y", "iptables-persistent"],
                success_msg=f"iptables-persistent: {config.lang.msg['packageSuccess']}",
                error_msg=f"{config.lang.msg['packageFailed']}: iptables-persistent."
            )
            
        installIcecast()
        utils.markDone(step)

def updateAndUpgrade():
    step = "aptUpdate"
    
    if utils.stepIsDone(step):
        return
    else:
        try:
            print(colorText(f"\n{config.lang.msg['execute']}: ", "BLUE") + "sudo apt update")
            printColored(f"{config.lang.msg['wait']}", "YELLOW", True)

            # Real-time output for 'apt update'
            process = subprocess.Popen(['sudo', 'apt', 'update'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in process.stdout:
                print(line, end='')
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, 'apt update')

            printColored(f"\n{config.lang.msg['checkUpdate']}", "RESET", True)

            # Real-time output for 'apt list --upgradable'
            process = subprocess.Popen(['sudo', 'apt', 'list', '--upgradable'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            upgradable_output = ""
            for line in process.stdout:
                print(line, end='')
                upgradable_output += line
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, 'apt list --upgradable')

            if "upgradable" in upgradable_output:
                printColored(f"\n{config.lang.msg['upgradeAvailable']}\n", "RESET", True)
                print(
                    colorText(f"{config.lang.msg['execute']} :", "BLUE"),
                    colorText("sudo apt upgrade", None)
                )
                # Real-time output for 'apt upgrade'
                process = subprocess.Popen(['sudo', 'apt', 'upgrade', '-y'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                printColored(f"{config.lang.msg['wait']}", "RESET", True)
                for line in process.stdout:
                    print(line, end='')
                process.wait()
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, 'apt upgrade')

            utils.markDone(step)
            printColored(f"\n✓ {config.lang.msg['aptUpdated']}", "GREEN")
            return True

        except subprocess.CalledProcessError as e:
            print(
                colorText(f"{config.lang.msg['errorOccured']}: ", "RED"),
                colorText(f"{getattr(e, 'stderr', str(e))}", None)
            )
            return False

def changeFilePermissions(filePath, mode):
    try:
        os.chmod(filePath, mode)
        print(
            colorText(f"✓ {config.lang.msg['permission']}","GREEN"),
            colorText( f"{filePath} -> {oct(mode)}", None)
        )
    except Exception as e:
        print(
            colorText(f"✗ {config.lang.msg['permissionE']}: ","RED"),
            colorText(f"{e}",None)
        )

def setFileOwnership(filePath, user, group):
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"✗ {config.lang.msg['file']} '{filePath}' {config.lang.msg['noExist']}.")

    try:
        subprocess.run(['sudo', 'chown', f'{user}:{group}', filePath], check=True)
        print(
            colorText(f"✓ '{filePath}':", "GREEN"),
            colorText(f"{user}:{group}.", None)
        )
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to change file ownership: {e}", "RED")

def setOwnership(directoryPath, user, group):
    if not os.path.exists(directoryPath):
        raise FileNotFoundError(f"✗ {config.lang.msg['directory']} '{directoryPath}' {config.lang.msg['noExist']}.")

    try:
        subprocess.run(['sudo', 'chown', '-R', f'{user}:{group}', directoryPath], check=True)
        print(
            colorText(f"✓  '{directoryPath}':","GREEN"),
            colorText(f"{user}:{group}.", None)
        )
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to change ownership: {e}", "RED")
        
def setPermissions(directoryPath, permissions):
    if not os.path.exists(directoryPath):
        raise FileNotFoundError(f"{config.lang.msg['directory']} '{directoryPath}' {config.lang.msg['noExist']}.")

    try:
        subprocess.run(['sudo', 'chmod', '-R', permissions, directoryPath], check=True)
        print(
            colorText(f"✓ {directoryPath} -> ", "GREEN"),
            colorText(f" {permissions}.",None)
        )
   
    except subprocess.CalledProcessError as e:
        printColored(f"✗ {config.lang.msg['permFailed']}: {e}","RED")

def setUserOwnership(path, username):
    try:
        import pwd
        import grp
        uid = pwd.getpwnam(username).pw_uid
        gid = grp.getgrnam(username).gr_gid
        os.chown(path, uid, gid)
        for root, dirs, files in os.walk(path):
            for d in dirs:
                os.chown(os.path.join(root, d), uid, gid)
            for f in files:
                os.chown(os.path.join(root, f), uid, gid)
        print(f"Ownership set to user '{username}'")
    except Exception as e:
        print(f"Error setting ownership: {e}", file=sys.stderr)
        raise

def installFromTargz(url, remove_after=False, params=""):
    import tarfile
    from urllib.parse import urlparse
    import requests
    
    step = "lame"
    if utils.stepIsDone(step):
        return
    else:
    
        install_dir = f"{config.SCRIPT_DIR}/temp/lameInstall"
        try:
            Path(install_dir).mkdir(parents=True, exist_ok=True)
            os.chdir(install_dir)
            
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            dirname = filename.replace('.tar.gz', '')
            
            print(f"\n\033[1;34m=== {config.lang.msg['download']} {filename} ===\033[0m")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as file:
                for data in response.iter_content(1024):  # 1 Kibibyte
                    file.write(data)
            
            print(f"\033[92m✓ {config.lang.msg['downloadComplete']}\033[0m")
            
            print(f"\n\033[1;34m=== {config.lang.msg['extracting']} {filename} ===\033[0m")
            with tarfile.open(filename, 'r:gz') as tar:
                tar.extractall()
            print(f"\033[92m✓ {config.lang.msg['extractingDone']}\033[0m")
            
            os.chdir(dirname)
            configure_cmd = ['./configure']
            if params:
                configure_cmd.extend(params.split())

            commands = [
                (configure_cmd, f"{config.lang.msg['configureBuild']}..."),
                (['make'], f"{config.lang.msg['make']}..."), 
                (['sudo', 'make', 'install'], f"{config.lang.msg['installing']}...")
            ]
            
            for cmd, mesg in commands:
                print(f"\n\033[1;34m=== {mesg} ===\033[0m")
                print(f"\033[33m$\033[0m {' '.join(cmd)}")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    print(line.strip())
                
                if process.wait() != 0:
                    print(f"\033[91m✗ {config.lang.msg['faildedAt']}: {mesg}\033[0m")
                    return False
                print(f"\033[92m✓ {mesg.split('...')[0]} complete!\033[0m")
            
            print(f"\n\033[1;32m=== {config.lang.msg['lameComlete']}! ===\033[0m")
            
            if remove_after:
                print("\n\033[1;34m=== Cleaning up ===\033[0m")
                os.chdir(install_dir)
                os.remove(filename)
                print(f"\033[92m✓ Removed {filename}\033[0m")
            
            utils.markDone(step)
            return True
        
        except Exception as e:
            print(f"\n\033[1;31m=== Error occurred ===\033[0m")
            print(f"\033[91m{str(e)}\033[0m")
            return False

def createSystemdOverride(serviceName, overrideContent):
    """
    Crée un fichier override systemd pour un service donné.
    """
    overrideDir = f"/etc/systemd/system/{serviceName}.service.d"
    overrideFile = os.path.join(overrideDir, "override.conf")
    
    os.makedirs(overrideDir, exist_ok=True)
    with open(overrideFile, "w") as f:
        f.write(overrideContent)
    
    print(f"[INFO] Override créé pour {serviceName} dans {overrideFile}")

def reloadRystemd():
    """
    Recharge systemd pour prendre en compte les modifications des unités.
    """
    subprocess.run(["systemctl", "daemon-reexec"], check=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    print("[INFO] systemd rechargé.")

