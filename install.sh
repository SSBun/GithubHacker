#!/bin/bash
# GitHub Hacker Installer
# Usage: curl -sL https://raw.githubusercontent.com/YOUR_USERNAME/GithubHacker/main/install.sh | bash

set -e

REPO="YOUR_USERNAME/GithubHacker"
INSTALL_DIR="${HOME}/.github-hacker"
BIN_DIR="${HOME}/.local/bin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Installing GitHub Hacker...${NC}"

# Get latest release info
echo "Fetching latest version..."
LATEST=$(curl -sL "https://api.github.com/repos/${REPO}/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST" ]; then
    echo -e "${YELLOW}Could not fetch latest release, installing from main branch...${NC}"
    REPO_URL="https://github.com/${REPO}.git"
else
    echo "Latest version: $LATEST"
    REPO_URL="https://github.com/${REPO}/archive/refs/tags/${LATEST}.tar.gz"
fi

# Create installation directory
mkdir -p "${INSTALL_DIR}"
cd "${INSTALL_DIR}"

# Download and extract
echo "Downloading..."
if [ -z "$LATEST" ]; then
    git clone --depth 1 "$REPO_URL" . 2>/dev/null || {
        echo -e "${RED}Failed to clone repository${NC}"
        exit 1
    }
else
    curl -sL "${REPO_URL}" | tar xz --strip-components=1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate and install
echo "Installing dependencies..."
source venv/bin/pip install -e . --quiet

# Create launcher script
mkdir -p "${BIN_DIR}"
cat > "${BIN_DIR}/github-hacker" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${HOME}/.github-hacker/venv/bin/python" -m githubhacker.cli "$@"
EOF
chmod +x "${BIN_DIR}/github-hacker"

# Add to PATH if not already
SHELL_RC="${HOME}/.bashrc"
if [ -f "${HOME}/.zshrc" ]; then
    SHELL_RC="${HOME}/.zshrc"
fi

if ! grep -q ".local/bin" "${SHELL_RC}"; then
    echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> "${SHELL_RC}"
fi

echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo "Please run:"
echo "  source ~/.bashrc  # or ~/.zshrc"
echo "  github-hacker --help"
echo ""
echo "Or use directly:"
echo "  ${BIN_DIR}/github-hacker --help"
