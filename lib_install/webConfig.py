import json
from pathlib import Path
import re
import subprocess
from lib_install import config, utils, system
from lib_install.colors import printColored, colorText


def installSite():
    step = 'installSite'
    if utils.stepIsDone(step):
        return
    else:
        syncScript = '/usr/local/bin/sync-uploads.sh'
        utils.copyFile(f"{config.SCRIPT_DIR}/src/config{syncScript}",syncScript)
        utils.replaceInFile( ('USER =XXXXXXX', f"USER='{config.user}'"), syncScript)
        system.changeFilePermissions(syncScript, 0o755)
        
        source = f"{config.SCRIPT_DIR}/src/www"
        utils.recursiveCopy(source,'/var/www/html')

        utils.replaceInFile([
            ("$ICECAST = ['XXXXXX', 'XXXXXX'];", f"$ICECAST = ['{config.ICECAST_ADMIN}', '{config.ICECAST_PASS}'];"),
            ("$WIFI = 'XXXXXX';", f"$WIFI = '{config.WIFI_PASS}';"),
            ("$WEBADMIN = ['XXXXXX', 'XXXXXX'];", f"$WEBADMIN = ['{config.WEB_ADMIN}', '{config.WEB_PASS}'];"),
            ("return 'XXXXXX';", f"return '{config.user}';"),
            ("$wlan = 'XXXXXX';", f"$wlan = '{config.wlan}';")
            ],"/var/www/html/admin/inc/tools.php")

        system.setOwnership('/var/www/html','www-data','www-data')
        system.setPermissions('/var/www/html','755')
        system.changeFilePermissions("/var/www/html/data/stream.json", 0o776)
        system.changeFilePermissions("/var/www/html/data/status.json", 0o776)
        system.runSysctl(['sudo', 'rm',  "/var/www/html/index.lighttpd.html"])
        webAdminConf()
        system.setPermissions("/var/www/html/admin/uploads/","775")

        utils.markDone(step)

def webAdminConf():
    jsonFile = Path("/var/www/html/admin/data/config.json")
    excluded = ["lang", "user", "wlan", "num", "servers"]
    servers = []
    cnt = 0
    try:
        with open(jsonFile, 'r') as f:
            data = json.load(f)
            
        for key,value in config.installConf.items():
            if key in excluded:
                continue
            if isinstance(value, dict):
                server = {
                    "name": value["name"],
                    "ip": value["ip"],
                    "type": value["type"]
                }
                servers.append(server)
                cnt +=1
        
        data["servers"] = servers
        
        with open(jsonFile, 'w') as f:
            json.dump(data, f, indent=4)    
        
        print(
           colorText( f"✓ ","GREEN"),
           colorText(f"{cnt} {config.lang.msg['addedToConf']}",None),
           colorText( f"{jsonFile}",None)
        )
    except Exception as e:
        print(
            colorText(f"✗ {config.lang.msg['errorOccured']}:", "RED"),
            colorText(f"{str(e)}",None)
        )
        return False

def setupPhpFpm():
    step = 'configPhp-fpm'
    if utils.stepIsDone(step):
        return
    else:
        printColored(f"{config.lang.msg['phpFpmConf']}:", "BLUE")
        utils.backupFile("/etc/lighttpd/conf-available/15-fastcgi-php-fpm.conf")
        
        configPath = Path("/etc/lighttpd/conf-available/15-fastcgi-php-fpm.conf")
        enabledPath = Path("/etc/lighttpd/conf-enabled") / configPath.name
        
        try:
            if not configPath.parent.exists():
                raise RuntimeError(f"{config.lang.msg['phpfpmNotFound']}")
            
            content = configPath.read_text()
            
            try:
                php_version = subprocess.check_output(["php", "-v"], stderr=subprocess.STDOUT).decode()
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"{config.lang.msg['phpNotFound']}: {e.output.decode().strip()}")
            
            
            version_match = re.search(r'PHP (\d+\.\d+)\.\d+', php_version)
            if not version_match:
                raise RuntimeError(f"{config.lang.msg['phpVersionParse']}: {php_version.splitlines()[0]}")
            
            php_version_short = version_match.group(1)
            print(
                colorText(f"{config.lang.msg['phpVersion']}: ","BLUE"),
                colorText(f"{php_version_short}",None)
            )
            
            new_socket = f'/run/php/php{php_version_short}-fpm.sock'
            updated_content = re.sub(
                r'"socket"\s*=>\s*".*php.*fpm\.sock"',
                f'"socket" => "{new_socket}"',
                content
            )
            
            if not Path(new_socket).exists():
                print(
                    colorText(f"{new_socket}",None),
                    colorText(f"{config.lang.msg['socketNotFound']}","YELLOW")
                )
            
            configPath.write_text(updated_content)

            
            if not enabledPath.exists():
                try:
                    enabledPath.symlink_to(configPath)
                except OSError as e:
                    raise RuntimeError(f"{config.lang.msg['symlink']}: {e}.")
            
            utils.markDone(step)
            print(
                colorText(f"✓ {config.lang.msg['phpFpmDone']}:","GREEN"),
                colorText(f"{php_version_short}", None)
            )
        
        except Exception as e:
            print(
                colorText(f"✗ {config.lang.msg['phpFpmError']}:", "RED"),
                colorText(f"{e}", None)
            )
            return False
        
        return True

def setupLighttpd():
    step = 'lighttpdConf'
    
    if utils.stepIsDone(step):
        return False
    else:
        filePath="/etc/lighttpd/lighttpd.conf"
        
        printColored(f"{config.lang.msg['lighttpdsetUp']}", "BLUE")
        utils.backupFile(filePath)
        
        if config.type == 'master':
            sourceFile = f"{config.SCRIPT_DIR}/src/config/etc/lighttpd/master-lighttpd.conf"
            if config.num >=1:
            
                balancingConfig = [
                    "# Load balancing",
                    '$HTTP["host"] == "dj.zic" {',
                    '    proxy.balance = "round-robin"',
                    '    proxy.server  = ( "" => (',
                ]
                try:
                    content = Path(sourceFile).read_text()
                    
                    for i in range (1, config.num +1):
                        balancingConfig.append(f'        ( "host" => "10.1.{i}.1", "port" => 80 ),')
                            
                    balancingConfig.extend(['    ))', '}'])
                    new_content = content + "\n" + "\n".join(balancingConfig)
                    Path(filePath).write_text(new_content)
                    
                    printColored( f"✓ {config.lang.msg['lighttpdConfOk']}","GREEN")
                    utils.markDone(step)
                    
                except FileNotFoundError:
                    printColored( f"✗ {sourceFile} {config.lang.msg['notFound']}","RED")
                except PermissionError:
                    printColored( f"✗ {config.lang.msg['noPermission']}", "RED")
                except Exception as e:
                    printColored(f"✗ {config.lang.msg['errorOccured']} {e}","RED") 
                
        else:
            sourceFile = f"{config.SCRIPT_DIR}/src/config/etc/lighttpd/relay-lighttpd.conf"
            utils.copyFile(sourceFile , "/etc/lighttpd/lighttpd.conf")
            printColored( f"✓ {config.lang.msg['lighttpdConfOk']}","GREEN")