#!/bin/bash

# ===== COLOR CODES =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

# ===== ASCII ART =====
echo -e "${CYAN}${BOLD}"
echo "   ██████╗ ███╗   ██╗"
echo "  ██╔═══██╗████╗  ██║"
echo "  ██║   ██║██╔██╗ ██║"
echo "  ██║   ██║██║╚██╗██║"
echo "  ╚██████╔╝██║ ╚████║"
echo "   ╚═════╝ ╚═╝  ╚═══╝"
echo -e "${NC}"

echo -e "${CYAN}${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║${NC}    ${WHITE}${BOLD}on-lock Permission Tool${NC}         ${CYAN}${BOLD}║${NC}"
echo -e "${CYAN}${BOLD}╠══════════════════════════════════════╣${NC}"
echo -e "${CYAN}${BOLD}║  ${NC} ${YELLOW}Version:${NC} ${GREEN}2.2.0${NC}                   ${CYAN}${BOLD}║${NC}"
echo -e "${CYAN}${BOLD}║  ${NC} ${YELLOW}Developer:${NC} ${GREEN}on-lock${NC}               ${CYAN}${BOLD}║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════╝${NC}\n"

# ===== CHECK PYTHON =====
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found! Installing...${NC}"
    pkg install python -y 2>/dev/null || pkg install python3 -y 2>/dev/null || apt install python3 -y 2>/dev/null
fi

# ===== CHECK PIP =====
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️ Pip not found! Installing...${NC}"
    python3 -m ensurepip --upgrade 2>/dev/null
fi

# ===== INSTALL REQUIREMENTS =====
echo -e "${GREEN}📦 Installing required packages...${NC}"
pip install requests ntplib -q 2>/dev/null || pip3 install requests ntplib -q 2>/dev/null

# ===== CREATE HIDDEN FOLDER =====
echo -e "${GREEN}📁 Creating hidden folder ~/.onlock...${NC}"
mkdir -p ~/.onlock

# ===== DOWNLOAD MAIN SCRIPT =====
echo -e "${GREEN}📥 Downloading MiCommunityTool.py to ~/.onlock/...${NC}"
curl -sSL "https://raw.githubusercontent.com/MRMAMADTM/On-lock/main/MiCommunityTool.py" -o ~/.onlock/MiCommunityTool.py

# ===== CHECK IF DOWNLOAD SUCCEEDED =====
if [ ! -s ~/.onlock/MiCommunityTool.py ]; then
    echo -e "${RED}❌ Download failed! File is empty.${NC}"
    exit 1
fi

# ===== SET PERMISSIONS =====
chmod +x ~/.onlock/MiCommunityTool.py

# ===== CREATE EXECUTABLE (do NOT auto-run) =====
echo -e "${GREEN}🔧 Installing 'on-lock' command...${NC}"

if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    # Termux
    cat > "$PREFIX/bin/on-lock" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
python3 "$HOME/.onlock/MiCommunityTool.py" "$@"
EOF
    chmod +x "$PREFIX/bin/on-lock"
    echo -e "${GREEN}✅ Installed to Termux bin ($PREFIX/bin/on-lock)${NC}"
elif [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
    cat > /usr/local/bin/on-lock << 'EOF'
#!/bin/bash
python3 "$HOME/.onlock/MiCommunityTool.py" "$@"
EOF
    chmod +x /usr/local/bin/on-lock
    echo -e "${GREEN}✅ Installed to /usr/local/bin/on-lock${NC}"
else
    cat > ~/.onlock/on-lock << 'EOF'
#!/bin/bash
python3 "$HOME/.onlock/MiCommunityTool.py" "$@"
EOF
    chmod +x ~/.onlock/on-lock
    # add to PATH if missing
    if ! echo "$PATH" | grep -q "$HOME/.onlock"; then
        echo 'export PATH="$HOME/.onlock:$PATH"' >> ~/.bashrc 2>/dev/null
        echo 'export PATH="$HOME/.onlock:$PATH"' >> ~/.zshrc 2>/dev/null
    fi
    export PATH="$HOME/.onlock:$PATH"
    echo -e "${GREEN}✅ Installed to ~/.onlock/on-lock (added to PATH)${NC}"
fi

# ===== COMPLETE (no auto-run) =====
echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo -e "${YELLOW}▶️ Type '${GREEN}onlock${YELLOW}' to start the tool.${NC}"
echo ""
