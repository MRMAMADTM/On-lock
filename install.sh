#!/data/data/com.termux/files/usr/bin/bash

clear

# Colors
CYAN="\033[96m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
WHITE="\033[97m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${CYAN}${BOLD}"
echo " ██████╗ ███╗   ██╗██╗      ██████╗  ██████╗██╗  ██╗"
echo "██╔═══██╗████╗  ██║██║     ██╔═══██╗██╔════╝██║ ██╔╝"
echo "██║   ██║██╔██╗ ██║██║     ██║   ██║██║     █████╔╝ "
echo "██║   ██║██║╚██╗██║██║     ██║   ██║██║     ██╔═██╗ "
echo "╚██████╔╝██║ ╚████║███████╗╚██████╔╝╚██████╗██║  ██╗"
echo " ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝"
echo -e "${RESET}"
echo -e "${WHITE}${BOLD}        [V2.0.0] Onlock Installer{RESET}"
echo -e "${CYAN}───────────────────────────────────────────────${RESET}"

sleep 0.5
echo -e "${YELLOW}[•] Preparing environment & updating repositories...${RESET}"

pkg update -y > /dev/null 2>&1

echo -e "${YELLOW}[•] Installing Python, Termux-Tools, Termux-API & cURL...${RESET}"
pkg install python termux-tools termux-api curl -y > /dev/null 2>&1

echo -e "${YELLOW}[•] Installing required Python libraries (requests, ntplib)...${RESET}"
pip install --upgrade pip > /dev/null 2>&1
pip install requests ntplib > /dev/null 2>&1

mkdir -p $HOME/.on-lock

echo -e "${CYAN}[•] Downloading Onlock core tool from GitHub...${RESET}"

curl -fsSL https://raw.githubusercontent.com/MRMAMADTM/On-lock/main/on-lock.py -o $HOME/.on-lock/on-lock.py

if [ ! -s $HOME/.on-lock/on-lock.py ]; then
    echo -e "${RED}[✗] Download failed! Please check your internet connection or GitHub repository.${RESET}"
    exit 1
fi

echo -e "${CYAN}[•] Creating global executable launcher...${RESET}"

cat << 'EOF' > $PREFIX/bin/on-lock
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock > /dev/null 2>&1
python $HOME/.on-lock/on-lock.py "$@"
EOF

chmod +x $PREFIX/bin/on-lock

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗"
echo -e "║          ✅ INSTALL COMPLETE         ║"
echo -e "╚══════════════════════════════════════╝${RESET}"
echo -e "${WHITE}Telegram Channel: ${CYAN}https://t.me/unlock_bootloader_xiaomi${RESET}"
echo -e "${WHITE}Developer: ${CYAN}@MRMAMADTM${RESET}"
echo -e "${YELLOW}Run tool using: ${GREEN}on-lock${RESET}"
echo ""
