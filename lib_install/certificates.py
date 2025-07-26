import os
import pwd
import grp
import subprocess

from lib_install import config, utils
from lib_install.colors import printColored, colorText

def createCertificate(comment='pi-cluster'):
    step = "installCert"
    
    if utils.stepIsDone(step):
        return
    else:
        keyPath = f"{config.SCRIPT_DIR}/id_rsa_djzic"
        
        uid = pwd.getpwnam(config.user).pw_uid
        gid = grp.getgrnam(config.user).gr_gid
        
        if config.type == 'master':
            try:
                subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-C', comment, '-f', keyPath, '-N', ''], check=True)
                os.chmod(f"{keyPath}.pub", 0o666)
                os.chown(f"{keyPath}.pub", uid, gid)
                os.chmod(f"{keyPath}", 0o666)
                
            except subprocess.CalledProcessError as e:
                print(
                    colorText(f"✗ {config.lang.msg['errorOccured']}  SSH key:", "RED"),
                    colorText(f"{e}", None)
                )
        
        with open(f"{keyPath}.pub", "r") as pubkeyFile:
            pubkey = pubkeyFile.read().rstrip('\n')
        
        authorizedKeys = f"/home/{config.user}/.ssh/authorized_keys"
        with open(authorizedKeys, "r+") as authFile:
            authFile.seek(0)
            existingKeys = authFile.read()
            if not any(pubkey == key.rstrip('/n') for key in existingKeys):
                authFile.write(f"{pubkey}\n")
        
        os.chmod(authorizedKeys, 0o600)
        os.chown(keyPath, uid, gid)
        
        utils.copyFile(keyPath, f"/home/{config.user}/.ssh/id_rsa_djzic")
        os.chmod(f"/home/{config.user}/.ssh/id_rsa_djzic", 0o600)
        os.chown(f"/home/{config.user}/.ssh/id_rsa_djzic", uid, gid)
        
        printColored(f"✓ {config.lang.msg['sshAdded']}")
        
        utils.markDone(step)