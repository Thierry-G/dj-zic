import json
import os
from pathlib import Path
import subprocess
import sys
import venv
from lib_install.colors import printColored,colorText
from lib_install import config, utils, system

def createVirtualEnv():
    targetPath='/opt/djZic/venv'
    
    step = "createVenv" 
    if utils.stepIsDone(step):
        return
    else:
        dest = "/opt/djZic"
        dst = Path(dest)
        dst.mkdir(parents=True, exist_ok=True)
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/soundMonitor.py",f"{dest}/soundMonitor.py")
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/silenceDetector.py",f"{dest}/silenceDetector.py")
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/loggerConfig.py",f"{dest}/loggerConfig.py")
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/checkServices.py",f"{dest}/checkServices.py")
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/icecastMonitor.py",f"{dest}/icecastMonitor.py")
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/wiFiDistanceMonitor.py",f"{dest}/wiFiDistanceMonitor.py")
        utils.replaceInFile(("SERVERS = XXXXXXXXXXX", f"SERVERS = {repr(config.servers)}"),f"{dest}/icecastMonitor.py")
        setlibWifi()
        
        model = utils.getRaspberryModel()
        
        if config.type != 'relay':
            if "Raspberry Pi 5" in model:
                if "USB Audio" in utils.getSoundCards():
                    utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/masterPi5/streamServer.py",f"{dest}/streamServer.py")
                else:
                    utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/relay/streamPlayer.py",f"{dest}/streamPlayer.py")
            
            elif "Raspberry Pi 4" or "Raspberry Pi 3" in model:
                utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/master/streamServer.py",f"{dest}/streamServer.py")
        else:
            utils.copyFile(f"{config.SCRIPT_DIR}/src/config/opt/djzic/relay/streamPlayer.py",f"{dest}/streamPlayer.py")
            
                            
        system.setFileOwnership(f"{dest}/icecastMonitor.py","www-data","www-data")
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config/etc/systemd/system/icecast-monitor.service","/etc/systemd/system/icecast-monitor.service")
       
        
        try:
            currentUser = os.environ.get('SUDO_USER')
            
            path = Path(targetPath).absolute()
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create the virtual environment
            builder = venv.EnvBuilder(with_pip=True)
            builder.create(str(path))
            
            # Set appropriate ownership/permissions
            system.setUserOwnership(str(path), currentUser)
                        
            utils.markDone(step)

        except PermissionError as e:
            printColored(f"✗ {config.lang.msg['permDenied']}: {e}, {sys.stderr}", "RED")
           
            raise
        except Exception as e:
            printColored(f"✗ Error creating virtual environment: {e}, {sys.stderr}", "RED")
            raise

def setlibWifi():

    excluded = ["lang", "user", "wlan", "num", "servers"]
    known_devices = {}
    cnt =0
    try:    
        for key,value in config.installConf.items():
            if key in excluded:
                continue
            if isinstance(value, dict):
                known_devices[value["ip"]] = {
                    "hostname": value["name"],
                    "type": value["type"][config.installConf['lang']],
                }
                cnt +=1

        with open('/opt/djZic/libDistance.py', 'w') as f:
            f.write('known_devices =')
            json.dump(known_devices, f, indent=4)
        
        print(
           colorText( f"✓ ","GREEN"),
           colorText(f"{cnt} {config.lang.msg['libDistance']}",None),
        )
    except Exception as e:
        print(
            colorText(f"✗ {config.lang.msg['errorOccured']}:", "RED"),
            colorText(f"{str(e)}",None)
        )
        return False


def setupVirtualenv():
    venvPath="/opt/djZic/venv"
    step = "setUpVenv" 
    if utils.stepIsDone(step):
        return
    else: 
        try:
            activate_script = Path(venvPath) / 'bin' / 'activate'
            pip_executable = Path(venvPath) / 'bin' / 'pip'
            python_executable = Path(venvPath) / 'bin' / 'python'
                
            commands = [
                f'source "{activate_script}"',
                'python -m pip install --upgrade pip',
                'pip install numpy'
            ]

            # Update pip
            printColored(f"{config.lang.msg['venvPip']}","BLUE")
            subprocess.run([str(python_executable), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
            
            # Install numpy (required)
            printColored(f"{config.lang.msg['venvNumpy']}","BLUE")
            subprocess.run([str(pip_executable), 'install', 'numpy'], check=True)
            
            # Install requests (required)
            printColored(f"{config.lang.msg['venvRequests']}","BLUE")
            subprocess.run([str(pip_executable), 'install', 'requests'], check=True)

            printColored(f"✓ {config.lang.msg['venvDone']}","GREEN")
            utils.markDone(step)
            
        except subprocess.CalledProcessError as e:
            print(
                colorText(f"✗ {config.lang.msg['venvModuleError']}","RED"),
                colorText(f"{e}{sys.stderr}", None)
            )
            raise
        except Exception as e:
            print(
                colorText(f"✗ {config.lang.msg['errorOccured']}","RED"),
                colorText(f"{e} {sys.stderr}", None)
            )
            raise
