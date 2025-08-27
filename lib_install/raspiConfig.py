import re
import subprocess
from lib_install import config, utils
from lib_install.colors import printColored, colorText

def soundConfig():
    step = "configSound"
    if utils.stepIsDone(step):
        return
    else:
        printColored(f"{config.lang.msg['raspiConfigSound']}: ","BLUE")
        model = utils.getRaspberryModel()
        if "Raspberry Pi 5" in model:
            
            if "USB Audio" in utils.getSoundCards():
                print(
                    colorText( f"{config.lang.msg['piSnd']}:", None),
                    colorText( f" {model}","YELLOW"),
                    colorText( f"{config.lang.msg['piSndCard']}",None) 
                )
                utils.copyFile(f"{config.SCRIPT_DIR}/src/config/etc/asound-pi5.conf", "/etc/asound.conf")
                createAlsaCustom()
            else:
                print(
                    colorText( f"{config.lang.msg['piSnd']}:", None),
                    colorText( f" {model}","YELLOW"),
                    colorText( f"{config.lang.msg['piSndVirtual']}",None) 
                )
                utils.copyFile(f"{config.SCRIPT_DIR}/src/config/etc/asound-pi5-noAudio.conf", "/etc/asound.conf")
        
            
        elif "Raspberry Pi 4" or "Raspberry Pi 3" in model:
            print(f"{config.lang.msg['piSnd']}: {model}")
            utils.copyFile(f"{config.SCRIPT_DIR}/src/config/etc/asound.conf", "/etc/asound.conf")
            modifyAliasesFile()
            
        printColored(f"{config.lang.msg['raspiConfigSoundModule']}: ","BLUE")
        utils.backupFile('/etc/modules')
        utils.appendLineToFile('/etc/modules',"snd-aloop")
        
        printColored(f"\n✓ {config.lang.msg['raspiConfigDone']}", "GREEN")
        utils.markDone(step)

def createAlsaCustom():
    # Pi 5 with sound card
    sourceFile = "/etc/modprobe.d/alsa-custom.conf"
    with open(sourceFile,'w') as f:
        f.write("options snd_usb_audio index=0\n")
        f.write("options snd_aloop index=1\n")

def modifyAliasesFile():
    # Pi 3, 4 with sound card
    sourceFile = "/etc/modprobe.d/alsa-custom.conf"
    with open(sourceFile,'w') as f:
        f.write("options snd_bcm2835 index=0\n")
        f.write("options snd_aloop index=1\n")
        f.write("options snd_usb_audio index=2\n")
        f.write("options snd slots=snd_bcm2835,snd_aloop,snd_usb_audio\n")

def firmwareConfig():
    step = "firmwareconf"
    
    if utils.stepIsDone(step):
        return
    else:
        configPath = "/boot/firmware/config.txt"
        requiredSettings = {
            'audio_pwm_mode': '2',
            'camera_auto_detect': '0',
            'display_auto_detect': '0',
            'hdmi_auto_detect': '0',
            'dtoverlay': 'vc4-kms-v3d,noaudio'
        }
    
        utils.backupFile(configPath)
        print(
            colorText(f"{config.lang.msg['raspiConfigFirmware']}: ","BLUE"),
            colorText(f"{configPath}","RESET"),
        )
        
        try:
            with open(configPath, 'r') as f:
                lines = f.readlines()

            modified = False
            new_lines = []
            found_settings = set()

            for line in lines:
                stripped_line = line.strip()
                key = stripped_line.split('=')[0] if '=' in stripped_line else None
                
                if key in requiredSettings:
                    new_lines.append(f"{key}={requiredSettings[key]}\n")
                    found_settings.add(key)
                    modified = True
                else:
                    new_lines.append(line)

            for key, value in requiredSettings.items():
                if key not in found_settings:
                    new_lines.append(f"{key}={value}\n")

            if modified:
                with open(configPath, 'w') as f:
                    f.writelines(new_lines)
                printColored(f"✓ {config.lang.msg['firmwareUpdated']}","GREEN")
            else:
                print(f"{config.lang.msg['firmwareNotUpdated']}")

            utils.markDone(step)
            
        except Exception as e:
            printColored(f"✗ {config.lang.msg['errorOccured']} {configPath}: {e}", "RED")
