#!/bin/bash
set -euo pipefail

#===============================================================================
# Hailo Community Projects — Installation Script
# Delegates heavy lifting to hailo-apps-infra/install.sh
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="${SCRIPT_DIR}/hailo-apps-infra"

echo "=== Hailo Community Projects Installer ==="

# 1. Initialize submodule
echo ">>> Initializing hailo-apps-infra submodule..."
git -C "$SCRIPT_DIR" submodule update --init --recursive

# 2. Run hailo-apps-infra installer (needs sudo)
if [[ ! -f "${INFRA_DIR}/install.sh" ]]; then
    echo "ERROR: hailo-apps-infra/install.sh not found."
    echo "       Make sure the submodule was initialized correctly."
    exit 1
fi

echo ">>> Running hailo-apps-infra installer (requires sudo)..."
sudo "${INFRA_DIR}/install.sh" "$@"

# 3. Symlink venv for convenience
VENV_SOURCE="${INFRA_DIR}/venv_hailo_apps"
VENV_LINK="${SCRIPT_DIR}/venv_hailo_apps"

if [[ -d "$VENV_SOURCE" ]] && [[ ! -e "$VENV_LINK" ]]; then
    echo ">>> Creating venv symlink: venv_hailo_apps -> hailo-apps-infra/venv_hailo_apps"
    ln -s "hailo-apps-infra/venv_hailo_apps" "$VENV_LINK"
elif [[ -L "$VENV_LINK" ]]; then
    echo ">>> venv symlink already exists."
elif [[ -d "$VENV_LINK" ]]; then
    echo ">>> venv_hailo_apps directory already exists (not a symlink), skipping."
else
    echo ">>> Warning: ${VENV_SOURCE} not found. Run install from hailo-apps-infra first."
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
