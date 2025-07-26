import json
import os
from pathlib import Path
import sys
from lib_install import config, languages, utils, system, raspiConfig, webConfig, netConfig, envConfig, certificates
from lib_install.colors import printColored, colorText, printLogo

config.SCRIPT_DIR = Path(__file__).parent.resolve()
config.temp = f"{config.SCRIPT_DIR}/temp"
os.makedirs(config.temp, exist_ok=True)

def commons():
    printColored(config.lang.msg['step1'],"BLUE", True)
    system.updateAndUpgrade()
    system.installPackages()
   
    printColored(f"\n{config.lang.msg['step2']}","BLUE",True)
    raspiConfig.firmwareConfig()
    raspiConfig.soundConfig() 
    
    printColored(f"\n{config.lang.msg['step3']}","BLUE",True)
    webConfig.installSite()
    webConfig.setupLighttpd()
    webConfig.setupPhpFpm()
    
    printColored(f"\n{config.lang.msg['step4']}","BLUE",True)
    netConfig.setNetwork()
    
    if config.type != 'relay':
        certificates.createCertificate()
        printColored(f"\n{config.lang.msg['stepEncoder']}","BLUE",True)
        system.installFromTargz("https://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz", True, params="--prefix=/usr --enable-mp3rtp --disable-static")
    
    if config.type != 'single':
        printColored(f"\n{config.lang.msg['step6']}","BLUE",True)
        
    printColored(f"\n{config.lang.msg['step5']}","BLUE",True)
    envConfig.createVirtualEnv()
    envConfig.setupVirtualenv()
    printColored(f"\n{config.lang.msg['step7']}","BLUE",True)
    system.installServices()
    system.enableServices()
    system.updateSudoers()
    system.setUpDefault()
    system.runSysctl(['sudo',  'usermod', '-a', '-G', 'www-data', f"{config.user}"])
    system.runSysctl(['sudo', 'chmod', '775', '/var/www/html/data/stream.json']) 
    
    if config.type == 'master':
        confTemp = f"{config.temp}/djzicConf.json"
        with open(confTemp, "r") as f:
            data = json.load(f) 
        data[str(config.id)]['done'] = True
        with open(confTemp, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        configFile= f"{config.SCRIPT_DIR}/djzic_Install.json"
        utils.copyFile( confTemp, configFile)
        os.chmod(configFile, 0o444)
        
    system.runSysctl(['sudo', 'rfkill', 'unblock', 'wifi'])
    system.runSysctl(['sudo', 'rm', '-R', config.temp])
    
    next = str(int(config.id) +1)
    prefix = "djZic-install-next_"
    
    if config.installConf.get(next) is None:
        print(
            colorText(f"{config.lang.msg['installAllDone']}","RESET",True),
            colorText(f"{config.lang.msg['installNoteC']}: ","RESET",True),
            colorText(f"/home/{config.user}/install/README.md\n\n","GREEN",True)
        )
    else:
        tarName = f"{prefix}{config.installConf[next]['name']}"
    
        if config.type == 'master':
            source_dir = f"/home/{config.user}/install"
            output_tar = f"/home/{config.user}/{tarName}.tar.gz"
            #print(f"next: {next} : {output_tar}")
            import tarfile
            with tarfile.open(output_tar, "w:gz") as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
        else:
            confFile = f"{config.SCRIPT_DIR}/djzic_Install.json"
            with open(confFile, "r") as f:
                data = json.load(f) 
        
            data[str(config.id)]['done'] = True
            with open(confFile, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            installTar = f"/home/{config.user}/{prefix}{config.installConf[config.id]['name']}n"
            utils.replaceInTar(installTar, confFile, arcname=None)
            
            cmd = ['mv', f"{installTar}.tar.gz", f"/home/{config.user}/{prefix}{config.installConf[next]['name']}.tar.gz"]
            #print(", ".join(cmd))
            system.runSysctl(cmd)
    
    system.updateHostname(config.installConf[config.id]['name'])
    
    if config.type != 'single':
        if config.installConf.get(next) is not None:
            print(
                colorText("\n=================================================================\n\n","YELLOW"),
                colorText(f"{config.lang.msg['installDeviceEnd']}","RESET",True),
                colorText(f"{config.lang.msg['installOnNext']} (","RESET",True),
                colorText(f"{config.installConf[next]['name']}","GREEN"),
                colorText(f").\n{config.lang.msg['installMove']} ","RESET",True),
                colorText(f"/home/{config.user}/{tarName}.tar.gz ","BLUE",True),
                colorText(f"{config.lang.msg['installDest']} ","RESET",True),
                colorText(f"/home/{config.user}/ ","BLUE"),
                colorText(f"{config.lang.msg['installDest1']}.\n","RESET",True),
                colorText(f"{config.lang.msg['installInstr']}.\n","RESET",True),
                colorText(f"tar -xvf {tarName}.tar.gz\n","BLUE",True),
                colorText(f"cd install\n","BLUE",True),
                colorText(f"sudo python install.py","BLUE",True),
                colorText("\n-----------------------------------------------------------------\n\n","YELLOW"),
                
                colorText(f"{config.lang.msg['installNoteA']},\n","RESET",True),
                colorText(f"{config.lang.msg['installNoteB']}.\n","RESET",True),
                colorText(f"{config.lang.msg['installNoteC']}: ","RESET",True),
                colorText(f"/home/{config.user}/install/README.md\n\n","GREEN",True)
            )
    
    printColored(f"{config.lang.msg['installReboot']}","RED",True)
    question = config.lang.msg['choices']
    
    while True:
        answer = input(question).strip().lower()
        if answer in config.lang.msg['choicesOptions']['yes']:
            system.runSysctl(['systemctl', 'reboot'])
        elif answer in config.lang.msg['choicesOptions']['no']:
            exit(0)
        else:
            printColored(config.lang.msg['choicesError'],"RED")
    

def getDeviceToInstall(config):
    for key, value in config.items():
        if isinstance(value, dict) and 'done' not in value:
            return key
    return None
  
def main():

    confFile = Path(f"{config.SCRIPT_DIR}/djzic_Install.json")

    if os.geteuid() != 0:
        print(
            colorText(
                "Ce script requiert des privilèges administrateur!\nThis script require admin privilege! \nLancez-le avec / Launch with:",
                "RED",
            ),
            colorText("sudo python install.py", None, True),
        )
        sys.exit(1)
    
    printLogo()
    if not confFile.exists():

        config.user = os.environ.get("SUDO_USER")
        config.langCode = utils.selectLanguage()
        config.lang = languages.Language(config.langCode)

        utils.addToConfig("lang", config.langCode)
        utils.addToConfig("user", config.user)

        if utils.hasUsbSoundCard():
            config.type = "master"
            printColored(f"\n✓ {config.lang.msg['soundCardDetected']}\n", "GREEN")

            channels = [1, 6, 11]
            if utils.askSomething(f"{config.lang.msg['installDevice']}"):
                servers = []
                config.num = utils.selectAmountOfDevice()
                utils.addToConfig("num",config.num)
                
                if config.num >= 1:
                    config.wlan = utils.askForWlan()
                    utils.addToConfig("wlan", config.wlan)
                    
                    for i in range(0, config.num + 1):
                        if i == 0:
                            val = {
                                "ip": f"10.1.{i}.1",
                                "name": "dj-master",
                                "channel": f"{channels[i % len(channels)]}",
                                "type": {
                                    "en": "Streaming Server",
                                    "fr": "Serveur de streaming",
                                },
                            }
                        else:
                            val = {
                                "ip": f"10.1.{i}.1",
                                "name": f"dj-relay-{i}",
                                "channel": f"{channels[i % len(channels)]}",
                                "type": {"en": "relay", "fr": "relais"},
                            }
                        servers.append(f"10.1.{i}.1")
                        
                        utils.addToConfig(f"{i}", val)
                    
                    utils.addToConfig("servers", servers)        
                config.servers = servers
                utils.saveConfig()
                printColored(f"\n{config.lang.msg['overview']}\n","RESET", True)
               
                if config.wlan == "wlan1":
                    printColored("\t\tIBSS-DJzic\tAP: dj.zic", "BLUE", True)
                    printColored("\t\twlan0\t\twlan1", "RESET", True)
                    printColored("____________________________________________")
                    
                    for i in range(0, config.num + 1):
                        relay = f"10.1.{i}.1"
                        wifiUSb = f"10.2.{i}.1"
                        print(
                                colorText(f"{config.installConf[str(i)]['name']}", None, True),
                                colorText(f"\t{relay}", None, True),
                                colorText(f"\t{wifiUSb}", None, True),
                            )
                else:
                    printColored(f"{config.lang.msg['ap']}: dj.zic", "BLUE", True)
                    printColored("(wlan0)", "RESET", True)
                    printColored("____________________________________________")
                    for i in range(0, config.num + 1):
                        relay = f"10.1.{i}.1"
                        print(
                            colorText(
                            f"{config.installConf[str(i)]['name']}", None, True),
                            colorText(f"\t{relay}", None, True),
                        )
            else:
                val = {
                    "ip": f"10.1.0.1",
                    "name": "dj-master",
                    "channel": 6,
                    "type": {
                        "en": "Streaming Server",
                        "fr": "Serveur de streaming",
                    },
                }
                utils.addToConfig("0", val)
                utils.saveConfig()
                config.type = 'single'
                config.id = 0
                config.wlan = "wlan0"
                config.num = 0
                config.curr = config.installConf[str(config.id)]
                printColored(f"{config.lang.msg['solo']}\n","BLUE", True)
        else:
            print(
                colorText(f"✗ '{config.lang.msg['soundCardNotDetected']} !\n", "RED"),
                colorText(f"{config.lang.msg['quitNoSound']}", None),
            )
            sys.exit(1)
        
        if utils.askSomething(f"\n{config.lang.msg['installStart']}"):
                    config.id = getDeviceToInstall(config.installConf)
                    config.type = 'master'
                    config.curr = config.installConf[str(config.id)]
                    commons()

    else:
        config.type = "relay"
        if confFile.exists():
            with open(confFile, 'r') as f:
                data = json.load(f)
        config.installConf = data
        config.id = getDeviceToInstall(data)
        config.curr = data[str(config.id)]
        config.lang = languages.Language(data['lang'])
        config.wlan = data['wlan']
        config.user = data['user']
        config.num = data["num"]
        config.servers = data['servers']
        
        if config.user != os.environ.get('SUDO_USER'):
            if config.lang == 'fr':
                print(
                    colorText(f"\nImpossible de poursuivre l'installation de dj.zic!\n","RED"),
                    colorText(f"L'utilisateur ", None), 
                    colorText(f"{config.user}", "YELLOW", True),
                    colorText("doit être identique sur tous les appareils!", None),
                )
            else:
                print(
                    colorText(f"\nImpossible to carry on the dj.zic installation!\n","RED"),
                    colorText(f"The user ", None), 
                    colorText(f"{config.user}", "YELLOW", True),
                    colorText("must be the same on all devices!", None),
                )                      
            sys.exit(1)

        if config.lang == 'fr':   
            print( 
                  colorText(f"\nPoursuite de l'installation de dj.zic\n", "Blue"), 
                  colorText(f"- {config.curr['name']} : {config.curr['ip']}\n", None),
            )
            if config.wlan == "wlan0":
                print( 
                  colorText(f"  AP dj.zic : {config.wlan}\n", None)
                )
            else:
                print( 
                  colorText(f"  wlan0: IBSS-DJzic\twlan1: AP dj.zic\n", None)
                )
        else:
            print( 
                  colorText(f"\nCarry on dj.zic installation\n", "Blue"), 
                  colorText(f"- {config.curr['name']} : {config.curr['ip']}\n", None),
            )
            if config.wlan == "wlan0":
                print( 
                  colorText(f"- AP dj.zic : {config.wlan}\n", None)
                )
            else:
                print( 
                  colorText(f"- wlan0: IBSS-DJzic\twlan1: AP dj.zic\n", None)
                )
        commons()

if __name__ == "__main__":
    main()
