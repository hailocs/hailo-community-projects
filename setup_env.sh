#!/bin/bash
#
# Hailo Community Projects — Environment Setup
#
# Sets up PYTHONPATH, activates the virtual environment, and loads .env.
#
# Usage: source setup_env.sh
#

VENV_NAME="venv_hailo_apps"

# --- Must be sourced, not executed ---
is_sourced() {
    if [ -n "$ZSH_VERSION" ]; then
        [[ -o sourced ]]
    elif [ -n "$BASH_VERSION" ]; then
        [[ "${BASH_SOURCE[0]}" != "$0" ]]
    else
        echo "Unsupported shell. Please use bash or zsh."
        return 1
    fi
}

if ! is_sourced; then
    echo "This script should be sourced, not executed directly."
    exit 1
fi

# --- Kernel version check (Raspberry Pi) ---
check_kernel_version() {
    if uname -a | grep -q "Linux raspberrypi"; then
        INVALID_KERNELS=("6.12.21" "6.12.22" "6.12.23" "6.12.24" "6.12.25")
        CURRENT_VERSION=$(uname -r | cut -d '+' -f 1)
        if [[ " ${INVALID_KERNELS[@]} " =~ " ${CURRENT_VERSION} " ]]; then
            echo "Error: Kernel version $CURRENT_VERSION detected. This version is incompatible."
            echo "Please refer to: https://community.hailo.ai/t/raspberry-pi-kernel-compatibility-issue-temporary-fix/15322"
            return 1
        fi
    fi
}

echo "Setting up the environment..."
echo "Checking kernel version..."
check_kernel_version || {
    echo "Exiting due to incompatible kernel version."
    return 1
}

# --- Project root ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- PYTHONPATH: project root + hailo-apps-infra ---
export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_ROOT}/hailo-apps-infra:${PYTHONPATH:-}"
echo "PYTHONPATH set:"
echo "  ${PROJECT_ROOT}"
echo "  ${PROJECT_ROOT}/hailo-apps-infra"

# --- Activate virtual environment ---
if [ -d "${PROJECT_ROOT}/${VENV_NAME}" ] || [ -L "${PROJECT_ROOT}/${VENV_NAME}" ]; then
    source "${PROJECT_ROOT}/${VENV_NAME}/bin/activate"
    echo "Virtual environment '${VENV_NAME}' activated."
else
    echo "Warning: Virtual environment '${VENV_NAME}' not found."
    echo "Run ./install.sh first to set it up."
    return 1
fi

# --- Load .env ---
ENV_FILE="/usr/local/hailo/resources/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
    echo "Loaded environment from ${ENV_FILE}"
else
    echo "Note: ${ENV_FILE} not found (run install.sh to generate it)."
fi

echo "Environment ready."
