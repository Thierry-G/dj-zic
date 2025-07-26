import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from lib_install import config
from lib_install.colors import printColored, colorText

def getSoundCards():
    result = subprocess.run(["aplay", "-l"], capture_output=True, text=True)
    return result.stdout

def getRaspberryModel():
    with open('/proc/device-tree/model', 'r') as f:
        return f.read().strip()

def replaceInTar(tar_path, file_path, arcname=None):
    temp_tar_path = tar_path + ".tmp"
    extract_dir = tar_path + "_extract"

    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(extract_dir)

    target_name = arcname or os.path.basename(file_path)
    
    replaced = False
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file == target_name:
                target_path = os.path.join(root, file)
                os.remove(target_path)
                shutil.copy(file_path, target_path)
                replaced = True
    
    if not replaced:
        print(f"Warning: File '{target_name}' not found in the archive, adding it instead.")
        shutil.copy(file_path, os.path.join(extract_dir, target_name))

    with tarfile.open(temp_tar_path, "w:gz") as tar:
        for root, _, files in os.walk(extract_dir):
            for file in files:
                full_path = os.path.join(root, file)
                tar.add(full_path, arcname=os.path.relpath(full_path, extract_dir))

    os.replace(temp_tar_path, tar_path)
    shutil.rmtree(extract_dir)

def askForWlan():
    print(
        colorText(f"{config.lang.msg['installWlan']}",None,True)
    )
    question = config.lang.msg['choices']
    
    while True:
        answer = input(question).strip().lower()
        if answer in config.lang.msg['choicesOptions']['yes']:
            return "wlan1"
        elif answer in config.lang.msg['choicesOptions']['no']:
            return "wlan0"
        printColored(config.lang.msg['choicesError'],"RED") 

def selectAmountOfDevice():
    max = 10
    while True:
        try:
            print(
                colorText(f"{config.lang.msg['howManyRelay']}", None, True)
            )
            num = int(input(f"1-{max}: "))
            if 1 <= num <= max:
                return num
                break
        except ValueError:
            printColored(f"✗ {config.lang.msg['installInvalid']}", "RED", True)

def askSomething(something):
    print(f"{something}")
    question = config.lang.msg['choices']
    
    while True:
        answer = input(question).strip().lower()
        if answer in config.lang.msg['choicesOptions']['yes']:
            return True
        elif answer in config.lang.msg['choicesOptions']['no']:
            return False
        else:
            printColored(config.lang.msg['choicesError'],"RED")    

def selectLanguage():
    printColored("Choose your language / Choisissez votre langue:", "", True)
    print("1. English")
    print("2. Français")
    choice = input("1 or/ou 2: ").strip()

    if choice == "1":
        return "en"
    elif choice == "2":
        return "fr"
    else:
        printColored("Invalid choice. / Choix invalide.","RED",True)
        sys.exit(1)

def hasUsbSoundCard():
    try:
        output = subprocess.check_output(['aplay', '-l'], text=True)
        for line in output.splitlines():
            if 'USB' in line:
                return True
        return False
    except Exception as e:
        print(f"Error checking sound cards: {e}")
        return False

def addToConfig(key,value):
    config.installConf[key] = value
    
def saveConfig():
    configFile = f"{config.temp}/djzicConf.json"
    try:
        with open(configFile, 'w') as f:
            json.dump(config.installConf, f, indent=4)

    except Exception as e:
        colorText( f"{config.lang.msg['errorOccured']} {configFile}: {e}", "RED")
        return False

def markDone(step):
    file = f"{config.temp}/.{step}"
    (Path(file)).touch()

def getNumOfDevice():
    excluded = ["lang", "user", "wlan", "num", "servers"]
    n = 0
    for i in range(len(config.installConf) - len(excluded)):
        n +=1
    return n

def recursiveCopy(source, dest):
    src = Path(source)
    dst = Path(dest)
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)

def replaceInFile(replacements, file_path):
    """
    Replace strings in a file in-place.

    Args:
        replacements (list or tuple): A list of tuples or a single tuple where each tuple is (old_string, new_string).
        file_path (str): Path to the file where replacements should be made.
    
    Example usage:
    Single replacement
    replace_in_file(('hddd-vv=XXXX', 'hddd-vv=5DSDSDS'), 'path/to/your/file.txt')
    
    Multiple replacements
    replace_in_file([('hddd-vv=XXXX', 'hddd-vv=5DSDSDS'), ('bla=0', 'bla=1')], 'path/to/your/file.txt')
    """
    if isinstance(replacements, tuple):
        # Convert single tuple to a list of one tuple for uniform processing
        replacements = [replacements]

    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Perform replacements
        for old_string, new_string in replacements:
            content = content.replace(old_string, new_string)

        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(
            colorText(f"✗ {config.lang.msg['errorOccured']}:","RED"),
            colorText(f"{file_path}.", None)
        )
    except Exception as e:
        print(
            colorText(f"✗ {config.lang.msg['errorOccured']}: ", "RED"),
            colorText(f"{e}",None)
        )

def stepIsDone(step):
    path = f"{config.temp}/.{step}"
    if (Path(path)).exists():
        printColored(config.lang.msg[step], "YELLOW")
        return True

def copyFile(src, dst):
    try:
        shutil.copy2(src, dst)
        printColored(f"✓ {config.lang.msg['copy']}: {src} -> {dst}","GREEN")
    except Exception as e:
        printColored(f"✗ {config.lang.msg['copyFailed']} {src} -> {dst}: {e}")

def backupFile(source):
    file = os.path.splitext(os.path.basename(source))[0]
    prefix = os.path.dirname(source)
    
    shutil.copy2(source, f"{prefix}/{file}.backup")
    print( 
          colorText("✓", "GREEN"), 
          colorText(f"{source} -> {prefix}/{file}.backup", None)
    )

def appendLineToFile(filePath, stringToAdd):
    try:
        with open(filePath, 'r') as file:
            content = file.read()

        if stringToAdd not in content:
            with open(filePath, 'a') as file:
                file.write(stringToAdd + "\n") 
            return True
        return False

    except FileNotFoundError:
        # If file doesn't exist, create it and add the string
        with open(filePath, 'w') as file:
            file.write(stringToAdd + "\n")
        return True

