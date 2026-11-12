#!/data/data/com.termux/files/usr/bin/bash

# Colors
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
WHITE='\033[1;37m'
RESET='\033[0m'

clear

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════╗"
echo "║          ⚡ on-lock Bootloader ⚡           ║"
echo "║        Unlock Permission Installer         ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${RESET}"


sleep 0.5
echo -e "${BLUE}[•] Preparing environment...${RESET}"

# Update packages
pkg update -y > /dev/null 2>&1

# Install python
echo -e "${YELLOW}[•] Checking Python...${RESET}"
pkg install python -y > /dev/null 2>&1

# Create hidden folder
mkdir -p $HOME/.onlock

echo -e "${BLUE}[•] Installing core tool...${RESET}"

# Copy main script (local install mode - place MiCommunityTool.py next to this script or use curl if you host it)
if [ -f "./MiCommunityTool.py" ]; then
    cp ./MiCommunityTool.py $HOME/.onlock/MiCommunityTool.py
else
    echo -e "${YELLOW}[!] MiCommunityTool.py not found in current dir.${RESET}"
    echo -e "${YELLOW}    Place the script next to install.sh or edit the download URL.${RESET}"
    exit 1
fi

# Check
if [ ! -f "$HOME/.onlock/MiCommunityTool.py" ]; then
    echo -e "${RED}[✗] Install failed!${RESET}"
    exit 1
fi

echo -e "${BLUE}[•] Creating launcher...${RESET}"

# Launcher command
cat > $PREFIX/bin/on-lock << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
python $HOME/.onlock/MiCommunityTool.py "$@"
EOF

chmod +x $PREFIX/bin/on-lock

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗"
echo -e "║          ✅ INSTALL COMPLETE         ║"
echo -e "╚══════════════════════════════════════╝${RESET}"
echo -e "${WHITE}Made By: ${CYAN}on-lock${RESET}"
echo -e "${YELLOW}Run tool using:${RESET} ${GREEN}on-lock${RESET}"
echo ""
