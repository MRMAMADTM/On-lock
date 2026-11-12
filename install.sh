#!/data/data/com.termux/files/usr/bin/bash

clear

echo -e "\033[1;36m"
echo "╔════════════════════════════════════════════╗"
echo "║           ⚡ on-lock Tool ⚡                ║"
echo "║        Unlock Permission Installer         ║"
echo "╚════════════════════════════════════════════╝"
echo -e "\033[0m"

sleep 0.5
echo -e "\033[1;34m[•] Preparing environment...\033[0m"

pkg update -y > /dev/null 2>&1

echo -e "\033[1;33m[•] Checking Python...\033[0m"
pkg install python -y > /dev/null 2>&1

mkdir -p $HOME/.on-lock

echo -e "\033[1;34m[•] Downloading core tool...\033[0m"

curl -L https://raw.githubusercontent.com/MRMAMADTM/On-lock/main/on-lock.py -o $HOME/.on-lock/on-lock.py

if [ ! -f $HOME/.on-lock/on-lock.py ]; then
    echo -e "\033[1;31m[✗] Download failed!\033[0m"
    exit 1
fi

echo -e "\033[1;34m[•] Creating launcher...\033[0m"

echo '#!/data/data/com.termux/files/usr/bin/bash' > $PREFIX/bin/on-lock
echo "python $HOME/.on-lock/on-lock.py \"\$@\"" >> $PREFIX/bin/on-lock
chmod +x $PREFIX/bin/on-lock

echo ""
echo -e "\033[1;32m╔══════════════════════════════════════╗"
echo -e "║          ✅ INSTALL COMPLETE         ║"
echo -e "╚══════════════════════════════════════╝\033[0m"
echo -e "\033[1;37mMade By: \033[1;36mon-lock\033[0m"
echo -e "\033[1;33mRun tool using: \033[1;32mon-lock\033[0m"
echo ""
