#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Onlock Bootloader - Xiaomi Bootloader Unlock Permission Tool
Version: 1.0 Final
Telegram Channel: https://t.me/unlock_bootloader_xiaomi
Owner: @Mrmamadtm
"""

import os
import sys
import signal
import importlib
import time
import json
import hashlib
import base64
import urllib.parse
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse, quote

# ===== Auto-install dependencies =====
def ensure_deps():
    for lib in ['requests', 'ntplib']:
        try:
            importlib.import_module(lib)
        except ModuleNotFoundError:
            print(f"[*] Installing {lib} ...")
            os.system(f"{sys.executable} -m pip install {lib} -q")
    # getpass is stdlib

ensure_deps()

import requests
import ntplib
from getpass import getpass

# ===== Constants =====
VERSION = "1.0 Final"
VERSION_CODE = "500418"
VERSION_NAME = "5.4.18"
USER_AGENT = "okhttp/4.12.0"
TELEGRAM_CHANNEL = "https://t.me/unlock_bootloader_xiaomi"
OWNER = "@Mrmamadtm"

# ===== Colors =====
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
WHITE  = "\033[97m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"
DIM    = "\033[2m"

# ===== Signal handling (prevent Termux close on SIGHUP) =====
def ignore_sighup(signum, frame):
    pass

try:
    signal.signal(signal.SIGHUP, ignore_sighup)
except Exception:
    pass

# ===== Termux wake-lock =====
def acquire_wake_lock():
    try:
        # termux-wake-lock keeps CPU awake
        os.system("termux-wake-lock >/dev/null 2>&1")
        return True
    except Exception:
        return False

def release_wake_lock():
    try:
        os.system("termux-wake-unlock >/dev/null 2>&1")
    except Exception:
        pass

# ===== Banner =====
def print_banner():
    os.system("clear" if os.name != "nt" else "cls")
    banner = f"""
{CYAN}{BOLD}
   ██████╗ ███╗   ██╗
  ██╔═══██╗████╗  ██║
  ██║   ██║██╔██╗ ██║
  ██║   ██║██║╚██╗██║
  ╚██████╔╝██║ ╚████║
   ╚═════╝ ╚═╝  ╚═══╝
{RESET}
{WHITE}{BOLD}     Onlock Bootloader{RESET}
{DIM}     Xiaomi Unlock Permission Tool{RESET}
{YELLOW}     Version {VERSION}{RESET}

{MAGENTA}┌────────────────────────────────────────┐
│  Telegram : {TELEGRAM_CHANNEL}
│  Owner    : {OWNER}
└────────────────────────────────────────┘{RESET}
"""
    print(banner)

# ===== Helpers =====
def parse_mi_response(res):
    """Xiaomi account responses start with &&&START&&&"""
    text = res.text
    if text.startswith("&&&START&&&"):
        text = text[11:]
    return json.loads(text)

def box(title, lines, color=CYAN):
    width = 42
    print(f"\n{color}{BOLD}╔{'═' * width}╗{RESET}")
    print(f"{color}{BOLD}║{RESET}  {WHITE}{BOLD}{title.center(width-2)}{RESET}  {color}{BOLD}║{RESET}")
    print(f"{color}{BOLD}╠{'═' * width}╣{RESET}")
    for line in lines:
        # simple padding
        content = f"  {line}"
        print(f"{color}{BOLD}║{RESET}{content.ljust(width)}{color}{BOLD}║{RESET}")
    print(f"{color}{BOLD}╚{'═' * width}╝{RESET}\n")

# ===== Login =====
def login():
    base_url = "https://account.xiaomi.com"
    sid = "18n_bbs_global"
    headers = {"User-Agent": USER_AGENT}
    cookies = {}

    box("Mi Account LOGIN", [
        "Enter your Xiaomi account credentials",
        "Password will be hidden"
    ], YELLOW)

    user = input(f"{YELLOW}➤ Mi ID / Email / Phone : {RESET}").strip()
    pwd  = getpass(f"{YELLOW}➤ Password (hidden)     : {RESET}")

    if not user or not pwd:
        print(f"{RED}[✗] Empty credentials{RESET}")
        sys.exit(1)

    hash_pwd = hashlib.md5(pwd.encode()).hexdigest().upper()

    # Step 1
    r = requests.get(
        
... 
