#!/usr/python

versionCode = '500418'
versionName = '5.4.18'

import os
import importlib
import getpass

while True:
    for lib in ['requests', 'ntplib']:
        try:
            import importlib.util
            if importlib.util.find_spec(lib) is None:
                raise ModuleNotFoundError
        except ModuleNotFoundError:
            os.system(f'pip install {lib}')
            break
    else:
        break

import requests, json, hashlib, urllib.parse, time, sys, base64, ntplib
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse, quote

version = "2.0 Ultimate Pro"

try:
    os.system('termux-wake-lock > /dev/null 2>&1')
except Exception:
    pass

def send_notification(title, content):
    try:
        os.system(f'termux-notification --title "{title}" --content "{content}" --sound')
    except Exception:
        pass

# ===== Log System (ذخیره تاریخچه در فایل) =====
def write_log(message):
    try:
        with open("on-lock.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception:
        pass

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"
BLUE = "\033[94m"
BOX = "\033[95m"

print(f"""{CYAN}{BOLD}
  ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗
 ██╔═══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝
 ██║   ██║██╔██╗ ██║██║     ██║   ██║██║     █████╔╝ 
 ██║   ██║██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗ 
 ╚██████╔╝██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗
  ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
{RESET}""")

print(
    f"{CYAN}{BOLD}╔══════════════════════════════════════╗{RESET}\n"
    f"{CYAN}{BOLD}║{RESET}    {WHITE}{BOLD}[V{version}] Onlock Bootloader{RESET}     {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}╠══════════════════════════════════════╣{RESET}\n"
    f"{CYAN}{BOLD}║         {RESET} {YELLOW}Made By:{RESET} {GREEN}on-lock{RESET}            {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}║         {RESET} {YELLOW}Telegram:{RESET} {GREEN}@Mrmamadtm{RESET}       {CYAN}{BOLD}║{RESET}\n"
    f"{CYAN}{BOLD}╚══════════════════════════════════════╝{RESET}\n"
)

User = "okhttp/4.12.0"
headers = {"User-Agent": User}

# ===== Config File Management (مدیریت فایل تنظیمات) =====
CONFIG_FILE = "config.json"
default_config = {
    "auto_retry_attempts": 3,
    "retry_delay_seconds": 2,
    "preferred_region": "sgp"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)
    return default_config

config = load_config()

# ===== Multi-account Support (پشتیبانی از چند اکانت و سوییچ) =====
ACCOUNTS_FILE = "accounts.json"

def get_account_data():
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                accounts = json.load(f)
        except Exception:
            pass
            
    if accounts:
        print(f"\n{BLUE}[•] Saved Accounts:{RESET}")
        for idx, acc in enumerate(accounts):
            print(f"  {idx + 1}. User ID: {acc.get('userId')} (Region: {acc.get('region')})")
        print(f"  {len(accounts) + 1}. Add New Account / Login")
        
        choice = input(f"{YELLOW}➤ Choose account (1-{len(accounts)+1}): {RESET}").strip()
        if choice.isdigit():
            c = int(choice)
            if 1 <= c <= len(accounts):
                return accounts[c - 1]
                
    # لاگین جدید و افزودن به لیست
    new_acc = login()
    if new_acc not in accounts:
        accounts.append(new_acc)
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(accounts, f, indent=4)
    return new_acc

def login():
    base_url = "https://account.xiaomi.com"
    sid = "18n_bbs_global"

    print(
        f"\n{CYAN}{BOLD}╔══════════════════════════════════════╗{RESET}"
        f"\n{CYAN}{BOLD}║{RESET}   {WHITE}{BOLD}     Mi Account LOGIN PANEL{RESET}        {CYAN}{BOLD}║{RESET}"
        f"\n{CYAN}{BOLD}╚══════════════════════════════════════╝{RESET}"
    )

    user = input(f"{YELLOW}➤ Enter Mi ID:{RESET} ")
    pwd = getpass.getpass(f"{YELLOW}➤ Enter Mi Pwd :{RESET} ")

    hash_pwd = hashlib.md5(pwd.encode()).hexdigest().upper()
    cookies = {}

    def parse(res):
        return json.loads(res.text[11:])

    r = requests.get(f"{base_url}/pass/serviceLogin", params={'sid': sid, '_json': True}, headers=headers, cookies=cookies)
    cookies.update(r.cookies.get_dict())

    deviceId = cookies["deviceId"]

    data = {k: v[0] for k, v in parse_qs(urlparse(parse(r)['location']).query).items()}
    data.update({'user': user, 'hash': hash_pwd})

    r = requests.post(f"{base_url}/pass/serviceLoginAuth2", data=data, headers=headers, cookies=cookies)
    cookies.update(r.cookies.get_dict())
    res = parse(r)

    if res["code"] == 70016: exit("invalid user or pwd")
    if 'notificationUrl' in res:
        url = res['notificationUrl']
        if any(x in url for x in ['callback','SetEmail','BindAppealOrSafePhone']): exit(url)

        cookies.update({"NativeUserAgent": base64.b64encode(User.encode()).decode()})
        params = parse_qs(urlparse(url).query)
        cookies.update(requests.get(f"{base_url}/identity/list", params=params, headers=headers, cookies=cookies).cookies.get_dict())

        email = parse(requests.get(f"{base_url}/identity/auth/verifyEmail", params={'_json': True}, cookies=cookies, headers=headers))['maskedEmail']
        quota = parse(requests.post(f"{base_url}/identity/pass/sms/userQuota", data={'addressType': 'EM', 'contentType': 160040}, cookies=cookies, headers=headers))['info']
        print(f"Account Authentication\nemail: {email}, Remaining attempts: {quota}")
        input("\nPress Enter to send the verification code")

        code_res = parse(requests.post(f"{base_url}/identity/auth/sendEmailTicket", cookies=cookies, headers=headers))

        if code_res["code"] == 0: print(f"\nVerification code sent to your {email}")
        elif code_res["code"] == 70022: exit("Sent too many codes. Try again tomorrow.")
        else: exit(code_res)

        while True:
            ticket = input("Enter code: ").strip()
            v_res = parse(requests.post(f"{base_url}/identity/auth/verifyEmail", data={'ticket':ticket, 'trust':True}, cookies=cookies, headers=headers))
            if v_res["code"] == 70014: print("Verification code error")
            elif v_res["code"] == 0:
                cookies.update(requests.get(v_res['location'], headers=headers, cookies=cookies).history[1].cookies.get_dict())
                cookies.pop("pass_ua", None)
                break
            else: exit(v_res)

        r = requests.get(f"{base_url}/pass/serviceLogin", params={'_json': "true", 'sid': sid}, cookies=cookies, headers=headers)
        res = parse(r)

    region = json.loads(requests.get(f"https://account.xiaomi.com/pass/user/login/region", headers=headers, cookies=cookies).text[11:])["data"]["region"]    

    nonce, ssecurity = res['nonce'], res['ssecurity']
    res['location'] += f"&clientSign={quote(base64.b64encode(hashlib.sha1(f'nonce={nonce}&{ssecurity}'.encode()).digest()))}"
    serviceToken = requests.get(res['location'], headers=headers, cookies=cookies).cookies.get_dict()

    micdata = {"userId": res['userId'], "new_bbs_serviceToken": serviceToken["new_bbs_serviceToken"], "region": region, "deviceId": deviceId}
    return micdata

micdata = get_account_data()

new_bbs_serviceToken = micdata["new_bbs_serviceToken"]
deviceId = micdata["deviceId"]
region = micdata['region']

# ===== Region Selector (انتخاب دستی ریجن سرور) =====
print(f"\n{BOX}{BOLD}╔══════════════════════════════════════╗{RESET}")
print(f"{BOX}{BOLD}║{RESET}          {WHITE}{BOLD}REGION SELECTOR{RESET}             {BOX}{BOLD}║{RESET}")
print(f"{BOX}{BOLD}╠══════════════════════════════════════╣{RESET}")
print(f"{BOX}{BOLD}║{RESET} Detected Region: {WHITE}{region}{RESET}                  {BOX}{BOLD}║{RESET}")
print(f"{BOX}{BOLD}╚══════════════════════════════════════╝{RESET}\n")

region_choice = input(f"{YELLOW}➤ Use default region ({region}) or change? (d/c): {RESET}").strip().lower()
if region_choice == 'c':
    print("1. Global SGP (sgp-api.buy.mi.com)\n2. India / Other")
    r_sel = input("Select region option (1/2): ").strip()
    if r_sel == '1':
        api_base = "https://sgp-api.buy.mi.com/bbs/api/global/"
    else:
        api_base = "https://sgp-api.buy.mi.com/bbs/api/global/"
else:
    api_base = "https://sgp-api.buy.mi.com/bbs/api/global/"

api = api_base

U_state = api + "user/bl-switch/state"
U_apply = api + "apply/bl-auth"
U_info = api + "user/data"

headers = {
  'User-Agent': User,
  'Accept-Encoding': "gzip",
  'Content-Type': "application/json",
  'content-type': "application/json; charset=utf-8",
  'Cookie': f"new_bbs_serviceToken={new_bbs_serviceToken};versionCode={versionCode};versionName={versionName};deviceId={deviceId};"
}

try:
    info_res = requests.get(U_info, headers=headers).json()
    info = info_res.get('data', {})
    
    print(
        f"\n{CYAN}{BOLD}╔══════════════════════════════════════╗{RESET}\n"
        f"{CYAN}{BOLD}║{RESET}            {WHITE}{BOLD}ACCOUNT INFO{RESET}              {CYAN}{BOLD}║{RESET}\n"
        f"{CYAN}{BOLD}╠══════════════════════════════════════╣{RESET}\n"
        f"{CYAN}{BOLD}║        {RESET} {YELLOW}Days in Community:{RESET} {WHITE}{info.get('registered_day', 'N/A')}{RESET}        {CYAN}{BOLD}║{RESET}\n"
        f"{CYAN}{BOLD}║        {RESET} {YELLOW}Level:{RESET} {WHITE}LV{info.get('level_info', {}).get('level', 'N/A')} {info.get('level_info', {}).get('level_title', '')}{RESET}    {CYAN}{BOLD}║{RESET}\n"
        f"{CYAN}{BOLD}║        {RESET} {YELLOW}Next Level Points:{RESET} {WHITE}{info.get('level_info', {}).get('max_value', 0) - info.get('level_info', {}).get('current_value', 0)}{RESET}      {CYAN}{BOLD}║{RESET}\n"
        f"{CYAN}{BOLD}║        {RESET} {YELLOW}Points:{RESET} {WHITE}{info.get('level_info', {}).get('current_value', 'N/A')}{RESET}                  {CYAN}{BOLD}║{RESET}\n"
        f"{CYAN}{BOLD}╚══════════════════════════════════════╝{RESET}\n"
    )
    write_log(f"Account loaded successfully. ID: {micdata.get('userId')}, Region: {region}")
except Exception as e:
    print(f"{RED}[✗] Failed to fetch account info: {e}{RESET}")

def state_request():
    try:
        state = requests.get(U_state, headers=headers).json().get("data", {})
        is_ = state.get("is_pass")
        deadline_ = state.get("deadline_format", "")
        if is_ == 1:
            send_notification("Onlock Success", f"Unlock access granted till {deadline_}")
            write_log(f"Unlock access granted till {deadline_}")
            exit(f"{GREEN}✔ Unlock access granted till {deadline_} (Beijing time){RESET}\n")
    except Exception:
        pass

state_request()

# ===== Auto Retry Support (تلاش خودکار با تنظیمات تعداد و فاصله) =====
def apply_request():
    print(f"\n{BLUE}[•] Sending unlock request with Auto Retry config...{RESET}")
    max_retries = config.get("auto_retry_attempts", 3)
    retry_delay = config.get("retry_delay_seconds", 2)
    
    for attempt in range(1, max_retries + 1):
        try:
            apply = requests.post(U_apply, data=json.dumps({"is_retry": True}), headers=headers)
            res_json = apply.json()
            if res_json.get("code") != 0:
                print(f"{RED}[✗] Attempt {attempt}/{max_retries} - Server error code: {res_json.get('code')}{RESET}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                return 0
                
            data_ = res_json.get("data", {}) or {}
            apply_ = data_.get("apply_result", 0)
            deadline_ = data_.get("deadline_format", "")
            
            messages = {
                1: "Application Successful!",
                4: f"Account Error. Try again after {deadline_}",
                3: f"Quota limit reached. Try again tomorrow at 00:00 CST",
                5: "Application failed. Try again later",
                6: "Please try again in a minute",
                7: "Please try again later"
            }
            
            msg = messages.get(apply_, f"Result code: {apply_}")
            print(f"{YELLOW}[i] Response: {msg}{RESET}")
            write_log(f"Apply response: {msg}")
            
            if apply_ == 1:
                send_notification("Onlock Success", "Bootloader unlock application successful!")
                state_request()
                return 1
            elif apply_ in [3, 4]:
                send_notification("Onlock Notice", "Quota full. Scheduled for next day 00:00 CST.")
                return 3
            elif apply_ in [5, 6, 7]:
                if attempt < max_retries:
                    print(f"{YELLOW}[•] Retrying in {retry_delay}s (Attempt {attempt}/{max_retries})...{RESET}")
                    time.sleep(retry_delay)
                    continue
                send_notification("Onlock Notice", msg)
                return 0
        except Exception as e:
            print(f"{RED}[✗] Request exception on attempt {attempt}: {e}{RESET}")
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
            return 0
    return 0

def get_ntp_time(servers=["pool.ntp.org", "time.google.com", "time.windows.com"]):
    client = ntplib.NTPClient()
    for server in servers:
        try:
            response = client.request(server, version=3, timeout=3)
            return datetime.fromtimestamp(response.tx_time, timezone.utc)
        except Exception:
            continue
    return datetime.now(timezone.utc)

def get_beijing_time():
    utc_time = get_ntp_time()
    return utc_time.astimezone(timezone(timedelta(hours=8)))

# ===== Countdown Timer (تایمر معکوس زنده پیشرفته) =====
def precise_sleep(target_time, precision=0.0005):
    while True:
        current_beijing = get_beijing_time()
        diff = (target_time - current_beijing).total_seconds()
        
        if diff <= 0:
            print()
            return
            
        hours = int(diff // 3600)
        minutes = int((diff % 3600) // 60)
        seconds = int(diff % 60)
        millis = int((diff - int(diff)) * 1000)
        
        # نمایش تایمر معکوس زنده و دقیق روی ترمینال
        sys.stdout.write(f"\r{YELLOW}[⏳] Countdown to Target: {hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d} (CST)    {RESET}")
        sys.stdout.flush()
        
        sleep_time = max(min(diff - precision/2, 1), precision)
        time.sleep(sleep_time)

def measure_latency(url, samples=5):
    latencies = []
    for _ in range(samples):
        try:
            start = time.perf_counter()
            requests.post(url, headers=headers, data='{}', timeout=2)
            latencies.append((time.perf_counter() - start) * 1000)
        except Exception:
            continue

    if len(latencies) < 3:
        return 150

    latencies.sort()
    trim = int(len(latencies) * 0.2)
    trimmed = latencies[trim:-trim] if trim else latencies
    return sum(trimmed)/len(trimmed)

def main_loop():
    # ۱. اجرای درخواست اولیه و ثبت لاگ
    res = apply_request()
    if res == 1:
        return

    # ۲. تنظیم دقیق زمان هدف روی ساعت ۰۰:۰۰ فردای روز جاری به وقت پکن
    now = get_beijing_time()
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    target = (today_midnight + timedelta(days=1)).replace(microsecond=999000)

    print(f"\n{CYAN}[•] Scheduled target time for next day 00:00 CST: {target.strftime('%Y-%m-%d %H:%M:%S.%f')} CST{RESET}")
    write_log(f"Scheduled next request for: {target.strftime('%Y-%m-%d %H:%M:%S')}")

    # ۳. حلقه انتظار پشت صحنه با تایمر معکوس زنده تا ۱ ثانیه مانده به ۰۰:۰۰ پکن
    while True:
        current_time = get_beijing_time()
        time_to_target = (target - current_time).total_seconds()
        
        if time_to_target <= 1.0:
            print(f"\n{YELLOW}[•] Exactly 1s remaining. Measuring real-time network latency...{RESET}")
            latency = measure_latency(U_apply)
            print(f"{GREEN}[✓] Latency Offset deducted: {latency:.2f} ms{RESET}")
            break
            
        hours = int(time_to_target // 3600)
        minutes = int((time_to_target % 3600) // 60)
        seconds = int(time_to_target % 60)
        
        sys.stdout.write(f"\r{YELLOW}[⏳] Waiting... Time left: {hours:02d}:{minutes:02d}:{seconds:02d}    {RESET}")
        sys.stdout.flush()
        
        time.sleep(0.5)

    execution_time = target - timedelta(milliseconds=latency)
    precise_sleep(execution_time)

    # ۴. ارسال درخواست نهایی و ارسال نوتیفیکیشن نتیجه
    print(f"\n{BLUE}[•] Sending final precise request at next day 00:00 CST...{RESET}")
    result = apply_request()
    if result == 1:
        print(f"{GREEN}[✔] Unlock request successful!{RESET}")
        send_notification("Onlock Success", "Bootloader unlock application successful!")
        write_log("Bootloader unlock application successful!")
    else:
        print(f"{RED}[✗] Request failed or quota full again.{RESET}")
        send_notification("Onlock Failed", "Unlock request failed or quota full.")
        write_log("Unlock request failed or quota full.")

if __name__ == "__main__":
    main_loop()
