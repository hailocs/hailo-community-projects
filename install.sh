#!/bin/bash
set -euo pipefail

#===============================================================================
# Hailo Community Projects — Installation Script
# Delegates heavy lifting to hailo-apps/install.sh
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="${SCRIPT_DIR}/hailo-apps"

# Detect the invoking user (works whether run with sudo or not)
if [[ -n "${SUDO_USER:-}" ]]; then
    REAL_USER="$SUDO_USER"
    REAL_GROUP="$(id -gn "$SUDO_USER")"
else
    REAL_USER="$(whoami)"
    REAL_GROUP="$(id -gn)"
fi

# Safety net: always fix ownership on exit (normal, error, or interrupt)
# Prevents root-owned files from being left in the repo if install is interrupted
trap_exit() {
    local exit_code=$?
    if [[ "${REAL_USER}" != "root" && -d "${INFRA_DIR}" ]]; then
        echo ">>> Fixing ownership of hailo-apps/ (ensuring no root-owned files)..."
        chown -R "${REAL_USER}:${REAL_GROUP}" "${INFRA_DIR}" 2>/dev/null || true
    fi
    exit "${exit_code}"
}
trap 'trap_exit' EXIT

echo "=== Hailo Community Projects Installer ==="

# 1. Initialize submodule (as the real user, not root)
echo ">>> Initializing hailo-apps submodule..."
if [[ -n "${SUDO_USER:-}" ]]; then
    sudo -u "$SUDO_USER" git -C "$SCRIPT_DIR" submodule update --init --recursive
else
    git -C "$SCRIPT_DIR" submodule update --init --recursive
fi

# 2. Run hailo-apps installer (needs sudo)
if [[ ! -f "${INFRA_DIR}/install.sh" ]]; then
    echo "ERROR: hailo-apps/install.sh not found."
    echo "       Make sure the submodule was initialized correctly."
    exit 1
fi

echo ">>> Running hailo-apps installer (requires sudo)..."
if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
    # Already running as root (e.g., user ran: sudo ./install.sh)
    "${INFRA_DIR}/install.sh" "$@"
else
    sudo "${INFRA_DIR}/install.sh" "$@"
fi

# 3. Symlink venv for convenience
VENV_SOURCE="${INFRA_DIR}/venv_hailo_apps"
VENV_LINK="${SCRIPT_DIR}/venv_hailo_apps"

if [[ -d "$VENV_SOURCE" ]] && [[ ! -e "$VENV_LINK" ]]; then
    echo ">>> Creating venv symlink: venv_hailo_apps -> hailo-apps/venv_hailo_apps"
    ln -s "hailo-apps/venv_hailo_apps" "$VENV_LINK"
elif [[ -L "$VENV_LINK" ]]; then
    echo ">>> venv symlink already exists."
elif [[ -d "$VENV_LINK" ]]; then
    echo ">>> venv_hailo_apps directory already exists (not a symlink), skipping."
else
    echo ">>> Warning: ${VENV_SOURCE} not found. Run install from hailo-apps first."
fi

# 4. Install community-specific dependencies
if [[ -f "${SCRIPT_DIR}/requirements.txt" ]]; then
    echo ">>> Installing community-specific Python dependencies..."
    source "${VENV_LINK}/bin/activate" 2>/dev/null || source "${VENV_SOURCE}/bin/activate"
    pip install -r "${SCRIPT_DIR}/requirements.txt"
fi

cat <<'EOF'

=== Installation Complete ===

To set up your environment:
    source setup_env.sh

EOF
