#!/data/data/com.termux/files/usr/bin/bash

clear

echo -e "\033[1;36m"
echo "╔════════════════════════════════════════════╗"
echo "║     ⚡ Onlock Bootloader Ultimate ⚡       ║"
echo "║        Unlock Permission Installer         ║"
echo "╚════════════════════════════════════════════╝"
echo -e "\033[0m"

sleep 0.5
echo -e "\033[1;34m[•] Preparing environment & updating repositories...\033[0m"

pkg update -y > /dev/null 2>&1

echo -e "\033[1;33m[•] Installing Python, Termux-Tools, Termux-API & cURL...\033[0m"
pkg install python termux-tools termux-api curl -y > /dev/null 2>&1

echo -e "\033[1;33m[•] Installing required Python libraries (requests, ntplib)...\033[0m"
pip install --upgrade pip > /dev/null 2>&1
pip install requests ntplib > /dev/null 2>&1

mkdir -p $HOME/.on-lock

echo -e "\033[1;34m[•] Downloading core tool from GitHub...\033[0m"

curl -fsSL https://raw.githubusercontent.com/MRMAMADTM/On-lock/main/on-lock.py -o $HOME/.on-lock/on-lock.py

if [ ! -s $HOME/.on-lock/on-lock.py ]; then
    echo -e "\033[1;31m[✗] Download failed! Please check your internet connection or GitHub repository.\033[0m"
    exit 1
fi

echo -e "\033[1;34m[•] Creating global executable launcher...\033[0m"

cat << 'EOF' > $PREFIX/bin/on-lock
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock > /dev/null 2>&1
python $HOME/.on-lock/on-lock.py "$@"
EOF

chmod +x $PREFIX/bin/on-lock

echo ""
echo -e "\033[1;32m╔══════════════════════════════════════╗"
echo -e "║          ✅ INSTALL COMPLETE         ║"
echo -e "╚══════════════════════════════════════╝\033[0m"
echo -e "\033[1;37mTelegram Channel: \033[1;36mhttps://t.me/unlock_bootloader_xiaomi\033[0m"
echo -e "\033[1;37mOwner: \033[1;36m@Mrmamadtm\033[0m"
echo -e "\033[1;33mRun tool using: \033[1;32mon-lock\033[0m"
echo ""
