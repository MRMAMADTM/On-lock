#!/data/data/com.termux/files/usr/bin/bash

clear

echo -e "\033[1;36m"
echo "╔════════════════════════════════════════════╗"
echo "║           ⚡ Onlock Bootloader ⚡           ║"
echo "║      Xiaomi Unlock Permission Installer    ║"
echo "║              Version 1.0 Final             ║"
echo "╚════════════════════════════════════════════╝"
echo -e "\033[0m"

sleep 0.4
echo -e "\033[1;34m[•] Preparing environment...\033[0m"

pkg update -y > /dev/null 2>&1

echo -e "\033[1;33m[•] Checking / Installing Python...\033[0m"
pkg install python -y > /dev/null 2>&1

echo -e "\033[1;33m[•] Installing pip packages (requests, ntplib)...\033[0m"
pip install requests ntplib -q > /dev/null 2>&1

# Optional: termux-api for better wake-lock (if available)
pkg install termux-api -y > /dev/null 2>&1 || true

mkdir -p $HOME/.on-lock

echo -e "\033[1;34m[•] Downloading core tool...\033[0m"

# Change this URL to your actual raw GitHub / mirror URL when publishing
SCRIPT_URL="https://raw.githubusercontent.com/MRMAMADTM/On-lock/main/on-lock.py"

curl -L --fail --silent --show-error "$SCRIPT_URL" -o $HOME/.on-lock/on-lock.py

if [ ! -f $HOME/.on-lock/on-lock.py ] || [ ! -s $HOME/.on-lock/on-lock.py ]; then
    echo -e "\033[1;31m[✗] Download failed! Check internet or URL.\033[0m"
    exit 1
fi

echo -e "\033[1;34m[•] Creating launcher command...\033[0m"

cat > $PREFIX/bin/on-lock << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Onlock Bootloader launcher
exec python3 $HOME/.on-lock/on-lock.py "$@"
EOF

chmod +x $PREFIX/bin/on-lock
chmod +x $HOME/.on-lock/on-lock.py

echo ""
echo -e "\033[1;32m╔══════════════════════════════════════╗"
echo -e "║          ✅ INSTALL COMPLETE         ║"
echo -e "╚══════════════════════════════════════╝\033[0m"
echo -e "\033[1;37mTool name : \033[1;36mOnlock Bootloader\033[0m"
echo -e "\033[1;37mVersion   : \033[1;33m1.0 Final\033[0m"
echo -e "\033[1;37mTelegram  : \033[1;36mhttps://t.me/unlock_bootloader_xiaomi\033[0m"
echo -e "\033[1;37mOwner     : \033[1;36m@Mrmamadtm\033[0m"
echo ""
echo -e "\033[1;33mRun the tool with:\033[0m  \033[1;32mon-lock\033[0m"
echo ""
