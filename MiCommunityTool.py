#!/usr/bin/python3

versionCode = '500418'
versionName = '5.4.18'

import os
import importlib
import sys
import base64
import hashlib
import json
import time
import getpass
from urllib.parse import urlparse, parse_qs, quote
from datetime import datetime, timedelta, timezone

while True:
    for lib in ['requests', 'ntplib']:
        try:
            importlib.import_module(lib)
        except ModuleNotFoundError:
            os.system(f'pip install {lib}')
            break
    else:
        break

import requests
import ntplib

version = "2.2.0-onlock"

# ===== COLORS =====
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

print(
    f"\n{CYAN}{BOLD}╔══════════════════════════════════════╗{RESET}\n"
    f"{CYAN}{BOLD}║{RESET}    {WHITE}{BOLD}[V{version}] on-lock edition{RESET}      {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}╠══════════════════════════════════════╣{RESET}\n"
    f"{CYAN}{BOLD}║         {RESET} {YELLOW}Made By:{RESET} {GREEN}on-lock{RESET}           {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}╚══════════════════════════════════════╝{RESET}\n"
)

# ===== CONFIG =====
BASE_URL = "https://account.xiaomi.com"
SID = "18n_bbs_global"
USER_AGENT = "okhttp/4.12.0"
api = "https://sgp-api.buy.mi.com/bbs/api/global/"
deviceId = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]

def parse_response(response):
    text = response.text.strip()
    if text.startswith("&&&START&&&"):
        text = text[11:]
    try:
        return json.loads(text)
    except Exception:
        print(f"{YELLOW}[DEBUG] Raw: {text[:300]}{RESET}")
        raise

def handle_2fa(notification_url, cookies, headers_login):
    """Handle identity verification (email / sms) inside Termux."""
    print(f"{YELLOW}[*] 2FA required – handling in Termux...{RESET}")

    # 1) open authStart
    r = requests.get(notification_url, headers=headers_login, cookies=cookies, allow_redirects=True, timeout=20)
    cookies.update(r.cookies.get_dict())

    # extract context & sid from url
    q = parse_qs(urlparse(notification_url).query)
    context = (q.get("context") or [""])[0]
    sid_param = (q.get("sid") or [SID])[0]

    # 2) identity/list
    list_params = {
        "sid": sid_param,
        "supportedMask": "0",
        "_locale": "en_US",
        "context": context,
    }
    rlist = requests.get(f"{BASE_URL}/identity/list", params=list_params, headers=headers_login, cookies=cookies, timeout=15)
    cookies.update(rlist.cookies.get_dict())
    try:
        idata = parse_response(rlist)
    except Exception:
        idata = {}

    flag = idata.get("flag", 8)  # 8=email, 4=phone
    method = "Email" if flag == 8 else "Phone"
    print(f"{CYAN}Verification method: {method}{RESET}")

    # 3) trigger verifyXxx
    requests.get(
        f"{BASE_URL}/identity/auth/verify{method}",
        params={"_flag": str(flag), "_json": "true"},
        headers=headers_login,
        cookies=cookies,
        timeout=15
    )

    # 4) send ticket with proper params
    send_params = {
        "_dc": str(int(time.time() * 1000)),
        "sid": sid_param,
        "context": context,
        "mask": "0",
        "_locale": "en_US",
    }
    send_data = {
        "retry": "0",
        "icode": "",
        "_json": "true",
        "ick": cookies.get("ick", ""),
    }
    send = requests.post(
        f"{BASE_URL}/identity/auth/send{method}Ticket",
        params=send_params,
        data=send_data,
        headers=headers_login,
        cookies=cookies,
        timeout=15
    )
    try:
        sres = parse_response(send)
    except Exception:
        sres = {"raw": send.text[:200]}
    if sres.get("code") == 0:
        print(f"{GREEN}Code sent ({method}){RESET}")
    elif sres.get("code") == 70022:
        print(f"{RED}Too many codes. Wait or try later.{RESET}")
    else:
        print(f"{YELLOW}Send response: {sres}{RESET}")
        print(f"{YELLOW}If code already arrived, just enter it below.{RESET}")

    # 5) verify loop
    while True:
        ticket = input("Enter verification code: ").strip()
        if not ticket:
            continue
        verify_params = {
            "_dc": str(int(time.time() * 1000)),
            "sid": sid_param,
            "context": context,
            "mask": "0",
            "_locale": "en_US",
        }
        verify_data = {
            "_flag": str(flag),
            "ticket": ticket,
            "trust": "true",
            "_json": "true",
            "ick": cookies.get("ick", ""),
        }
        v = requests.post(
            f"{BASE_URL}/identity/auth/verify{method}",
            params=verify_params,
            data=verify_data,
            headers=headers_login,
            cookies=cookies,
            timeout=15
        )
        try:
            vres = parse_response(v)
        except Exception:
            print(f"{RED}Bad verify response{RESET}")
            continue
        if vres.get("code") == 70014:
            print(f"{RED}Wrong code, try again{RESET}")
            continue
        if vres.get("code") == 0:
            if "location" in vres:
                r3 = requests.get(vres["location"], headers=headers_login, cookies=cookies, allow_redirects=True, timeout=15)
                cookies.update(r3.cookies.get_dict())
                for h in r3.history:
                    cookies.update(h.cookies.get_dict())
            cookies.update(v.cookies.get_dict())
            print(f"{GREEN}[+] 2FA passed{RESET}")
            return cookies
        print(f"{YELLOW}Verify response: {vres}{RESET}")
    return cookies

def login():
    global headers

    print(f"{YELLOW}[*] Login required{RESET}")
    headers_login = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    while True:
        cookies = {}
        user = input("Xiaomi ID / Email / Phone: ").strip()
        pwd = getpass.getpass("Password: ")

        if not user or not pwd:
            print(f"{RED}Empty credentials{RESET}")
            continue

        hashed = hashlib.md5(pwd.encode()).hexdigest().upper()

        try:
            # Step 1
            r = requests.get(
                f"{BASE_URL}/pass/serviceLogin",
                params={"sid": SID, "_json": "true"},
                headers=headers_login,
                cookies=cookies,
                timeout=15
            )
            cookies.update(r.cookies.get_dict())
            data0 = parse_response(r)

            if "location" not in data0:
                print(f"{RED}No location in serviceLogin: {data0}{RESET}\n")
                continue

            # Step 2
            qs_data = {k: v[0] for k, v in parse_qs(urlparse(data0["location"]).query).items()}
            qs_data.update({"user": user, "hash": hashed, "_json": "true"})

            r = requests.post(
                f"{BASE_URL}/pass/serviceLoginAuth2",
                data=qs_data,
                headers=headers_login,
                cookies=cookies,
                timeout=15
            )
            cookies.update(r.cookies.get_dict())
            res = parse_response(r)

            if res.get("code") == 70016:
                print(f"{RED}invalid user or pwd{RESET}\n")
                continue

            # 2FA
            if "notificationUrl" in res:
                cookies = handle_2fa(res["notificationUrl"], cookies, headers_login)
                # After 2FA, retry Auth2 with same credentials once (session now trusted)
                print(f"{YELLOW}Finishing login after 2FA...{RESET}")
                r = requests.post(
                    f"{BASE_URL}/pass/serviceLoginAuth2",
                    data=qs_data,
                    headers=headers_login,
                    cookies=cookies,
                    timeout=15
                )
                cookies.update(r.cookies.get_dict())
                res = parse_response(r)
                if "notificationUrl" in res:
                    print(f"{RED}2FA still required after verification. Try again later or disable 2FA temporarily.{RESET}\n")
                    continue

            if "ssecurity" not in res or "nonce" not in res or "location" not in res:
                print(f"{RED}Missing fields: {list(res.keys())}{RESET}")
                if res.get("description"):
                    print(res.get("description"))
                print()
                continue

            # Step 3 clientSign
            nonce = res["nonce"]
            ssecurity = res["ssecurity"]
            client_sign = base64.b64encode(
                hashlib.sha1(f"nonce={nonce}&{ssecurity}".encode()).digest()
            ).decode()

            loc = res["location"]
            if "clientSign=" not in loc:
                loc += ("&" if "?" in loc else "?") + f"clientSign={quote(client_sign)}"

            final = requests.get(loc, headers=headers_login, cookies=cookies, timeout=15, allow_redirects=True)
            final_cookies = final.cookies.get_dict()
            final_cookies.update(cookies)
            if final.history:
                for h in final.history:
                    final_cookies.update(h.cookies.get_dict())

            token = (
                final_cookies.get("new_bbs_serviceToken")
                or final_cookies.get("serviceToken")
                or final_cookies.get("passToken")
            )
            if not token:
                for k, v in final_cookies.items():
                    if "token" in k.lower():
                        token = v
                        break

            if not token:
                print(f"{RED}Failed to obtain serviceToken. Cookies: {list(final_cookies.keys())}{RESET}\n")
                continue

            headers = {
                "User-Agent": USER_AGENT,
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json",
                "content-type": "application/json; charset=utf-8",
                "Cookie": f"new_bbs_serviceToken={token};versionCode={versionCode};versionName={versionName};deviceId={deviceId};"
            }

            print(f"{GREEN}[+] Login success{RESET}")
            return True

        except Exception as e:
            print(f"{RED}Login error: {type(e).__name__}: {e}{RESET}\n")
            continue

# ===== ENDPOINTS =====
U_apply = api + "apply/bl-auth"
U_info = api + "user/data"
U_state = api + "apply/bl-auth/state"

login()

# ===== INFO BOX =====
try:
    info_resp = requests.get(U_info, headers=headers, timeout=15)
    info = info_resp.json()["data"]
except Exception as e:
    exit(f"{RED}Failed to fetch account info: {e}\n{getattr(info_resp,'text','')[:200]}{RESET}")

print(
    f"\n{CYAN}{BOLD}╔══════════════════════════════════════╗{RESET}\n"
    f"{CYAN}{BOLD}║{RESET}            {WHITE}{BOLD}ACCOUNT INFO{RESET}              {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}╠══════════════════════════════════════╣{RESET}\n"
    f"{CYAN}{BOLD}║        {RESET} {YELLOW}Days in Community:{RESET} {WHITE}{info.get('registered_day', '?')}{RESET}         {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}║        {RESET} {YELLOW}Level:{RESET} {WHITE}LV{info.get('level_info', {}).get('level', '?')} {info.get('level_info', {}).get('level_title', '')}{RESET}        {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}║        {RESET} {YELLOW}Next Level Points:{RESET} {WHITE}{info.get('level_info', {}).get('max_value', 0) - info.get('level_info', {}).get('current_value', 0)}{RESET}        {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}║        {RESET} {YELLOW}Points:{RESET} {WHITE}{info.get('level_info', {}).get('current_value', '?')}{RESET}                    {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}╚══════════════════════════════════════╝{RESET}\n"
)


def state_request():
    print(
        f"{GREEN}{BOLD}╔══════════════════════════════════════╗{RESET}\n"
        f"{GREEN}{BOLD}║{RESET}             {WHITE}{BOLD}ACCOUNT STATE{RESET}            {GREEN}{BOLD}║{RESET}\n"
        f"{GREEN}{BOLD}╚══════════════════════════════════════╝{RESET}"
    )
    try:
        state = requests.get(U_state, headers=headers, timeout=15).json().get("data", {})
        is_ = state.get("is_pass")
        button_ = state.get("button_state")
        deadline_ = state.get("deadline_format", "")

        if is_ == 1:
            exit(f"{GREEN}✔ Unlock access granted till {deadline_} (Beijing time){RESET}\n")

        msg = {
            1: f"{YELLOW}➤ Apply for bootloader unlocking{RESET}\n",
            2: f"{RED}✖ Account Error, try again after {deadline_} (mm/dd){RESET}\n",
            3: f"{RED}✖ Account must be registered over 30 days{RESET}\n"
        }
        print(msg.get(button_, f"{YELLOW}Unknown state: {button_}{RESET}\n"))
        if button_ in [2, 3]:
            exit()
    except Exception as e:
        exit(f"{RED}state: {e}{RESET}")


state_request()


def apply_request():
    print("\n[APPLY]:")
    try:
        apply = requests.post(U_apply, data=json.dumps({"is_retry": True}), headers=headers, timeout=15)
        print(f"Server response time: {apply.headers.get('Date', 'N/A')}")
        if apply.json().get("code") != 0:
            exit(apply.json())
        data_ = apply.json().get("data", {}) or {}
        apply_ = data_.get("apply_result", 0)
        deadline_ = data_.get("deadline_format", "")
        messages = {
            1: f"{GREEN}Application Successful{RESET}",
            4: f"\n{RED}Account Error Please try again after {deadline_} (mm/dd){RESET}\n",
            3: f"\n{YELLOW}Application quota limit reached, please try again after {deadline_.split()[0] if deadline_ else '?'} (mm/dd) {deadline_.split()[1] if len(deadline_.split())>1 else ''} (GMT+8){RESET}\n",
            5: f"\n{RED}Application failed. Please try again later{RESET}\n",
            6: f"\n{YELLOW}Please try again in a minute{RESET}\n",
            7: f"\n{YELLOW}Please try again later{RESET}\n"
        }
        print(messages.get(apply_, f"Result code: {apply_}"))
        if apply_ == 1:
            state_request()
        elif apply_ in [4, 5, 6, 7]:
            exit()
        elif apply_ == 3:
            return 1
    except Exception as e:
        exit(f"apply: {e}")


def get_ntp_time(servers=["pool.ntp.org", "time.google.com", "time.windows.com"]):
    client = ntplib.NTPClient()
    for server in servers:
        try:
            response = client.request(server, version=3, timeout=5)
            return datetime.fromtimestamp(response.tx_time, timezone.utc)
        except Exception:
            continue
    return datetime.now(timezone.utc)


def get_beijing_time():
    return get_ntp_time().astimezone(timezone(timedelta(hours=8)))


def precise_sleep(target_time, precision=0.01):
    while True:
        diff = (target_time - datetime.now(target_time.tzinfo)).total_seconds()
        if diff <= 0:
            return
        time.sleep(max(min(diff - precision/2, 1), precision))


def measure_latency(url, samples=5):
    latencies = []
    for _ in range(samples):
        try:
            start = time.perf_counter()
            requests.post(url, headers=headers, data="{}", timeout=2)
            latencies.append((time.perf_counter() - start) * 1000)
        except Exception:
            continue
    if len(latencies) < 3:
        return 200
    latencies.sort()
    trim = int(len(latencies) * 0.2)
    trimmed = latencies[trim:-trim] if trim else latencies
    return sum(trimmed)/len(trimmed) * 1.3


def schedule_daily_task():
    beijing_tz = timezone(timedelta(hours=8))
    while True:
        now = get_beijing_time()
        target = now.replace(hour=23, minute=57, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        print(f"\nNext execution at: {target.strftime('%Y-%m-%d %H:%M:%S.%f')} CST")
        while datetime.now(beijing_tz) < target:
            if (target - datetime.now(beijing_tz)).total_seconds() > 300:
                time.sleep(60)
            else:
                precise_sleep(target)
        latency = measure_latency(U_apply)
        execution_time = target + timedelta(minutes=3) - timedelta(milliseconds=latency)
        print(f"Adjusted execution time: {execution_time.strftime('%H:%M:%S.%f')}")
        precise_sleep(execution_time)
        result = apply_request()
        if result == 1:
            return 1


print(f"{CYAN}[*] Starting scheduled apply loop (daily ~00:00 CST){RESET}")
while True:
    result = schedule_daily_task()
    if result != 1:
        break
