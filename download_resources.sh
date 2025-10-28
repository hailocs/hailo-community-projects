#!/bin/bash
set -euo pipefail

# ===========================================================================================
# DEPRECATION NOTICE
# ===========================================================================================
# This script is maintained for backward compatibility only.
# The recommended way to download resources is through the hailo-post-install command
# which is automatically called during installation, or by using hailo-download-resources.
#
# New approach:
#   - Install with: sudo ./install.sh
#   - Or download resources manually: hailo-download-resources [--all|--group <GROUP>]
# ===========================================================================================

echo "⚠️  DEPRECATION NOTICE:"
echo "    This script is deprecated. Please use 'hailo-download-resources' instead."
echo "    This wrapper is provided for backward compatibility only."
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  # Try to find and activate the venv
  VENV_NAME="venv_hailo_rpi_examples"
  VENV_PATH="${SCRIPT_DIR}/${VENV_NAME}"
  
  if [[ -f "${VENV_PATH}/bin/activate" ]]; then
    echo "🔌 Activating virtual environment: ${VENV_NAME}"
    source "${VENV_PATH}/bin/activate"
  else
    echo "❌ Virtual environment not found at ${VENV_PATH}"
    echo "Please run './install.sh' first or activate your virtual environment manually."
    exit 1
  fi
fi

# Check if hailo-download-resources is available
if ! command -v hailo-download-resources >/dev/null 2>&1; then
  echo "❌ hailo-download-resources command not found."
  echo "Please install hailo-apps-infra first:"
  echo "    sudo ./install.sh"
  exit 1
fi

# Parse arguments
DOWNLOAD_FLAG=""
if [[ $# -gt 0 ]]; then
  case "$1" in
    --all)
      DOWNLOAD_FLAG="--all"
      echo "📦 Downloading all resources..."
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--all]"
      echo ""
      echo "Options:"
      echo "  --all    Download all available resources"
      echo "  (none)   Download default resources for your device"
      exit 1
      ;;
  esac
else
  echo "📦 Downloading default resources for your device..."
fi

# Get config file path
CONFIG_FILE="${SCRIPT_DIR}/config/config.yaml"
if [[ ! -f "$CONFIG_FILE" ]]; then
  CONFIG_FILE=""
fi

# Call the new resource downloader
echo ""
echo "🚀 Calling hailo-download-resources..."
if [[ -n "$CONFIG_FILE" ]]; then
  hailo-download-resources ${DOWNLOAD_FLAG} --config "$CONFIG_FILE"
else
  hailo-download-resources ${DOWNLOAD_FLAG}
fi

echo ""
echo "✅ Resources downloaded successfully!"
echo ""
echo "Note: In the future, please use 'hailo-download-resources' directly:"
if [[ -n "$DOWNLOAD_FLAG" ]]; then
  echo "    hailo-download-resources ${DOWNLOAD_FLAG}"
else
  echo "    hailo-download-resources"
fi
echo ""
