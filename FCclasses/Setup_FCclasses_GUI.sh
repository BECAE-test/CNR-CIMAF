#!/usr/bin/env bash
set -euo pipefail

# ==================== CONFIG ====================
APP_NAME="${APP_NAME:-FCclasses}"                   # venv name (default: FCclasses)
FC_VENVS_DEFAULT="${HOME}/.local/share/virtualenvs"
FC_VENVS="${FC_VENVS:-$FC_VENVS_DEFAULT}"           # override: FC_VENVS=/custom/path ./install_fcclasses_env.sh
VENV_PATH="${FC_VENVS}/${APP_NAME}"

# variable pointing to bin/activate (default: MY_VENV)
VENV_ACTIVATE_VAR="${VENV_ACTIVATE_VAR:-MY_VENV}"

# ==================== UTILS =====================
need() { command -v "$1" >/dev/null 2>&1; }
as_root() {
  if [ "$(id -u)" -eq 0 ]; then "$@"
  elif need sudo; then sudo "$@"
  else echo "!! Root privileges are required to install system packages"; exit 1; fi
}
append_once() {
  local file="$1" line="$2"
  grep -qxF "$line" "$file" 2>/dev/null || echo "$line" >> "$file"
}

# ==================== PKG MGR DETECTION =========
PKG=""; ID=""; LIKE=""
if [ -f /etc/os-release ]; then . /etc/os-release; ID="${ID:-}"; LIKE="${ID_LIKE:-}"; fi
if   need apt-get || [[ "${ID}${LIKE}" =~ (debian|ubuntu|mint|pop|zorin|elementary) ]]; then PKG="apt"
elif need dnf     || [[ "${ID}${LIKE}" =~ (fedora|rhel) ]]; then PKG="dnf"
elif need yum;   then PKG="yum"
elif need pacman || [[ "${ID}${LIKE}" =~ arch ]]; then PKG="pacman"
elif need zypper || [[ "${ID}${LIKE}" =~ suse ]]; then PKG="zypper"
elif need apk    || [[ "${ID}${LIKE}" =~ alpine ]]; then PKG="apk"
else echo "!! Unsupported package manager"; exit 1; fi
echo "-- Package manager detected: $PKG"

# ==================== 1) Install python3/pip/tk ==
case "$PKG" in
  apt)
    as_root apt-get update -y
    as_root apt-get install -y python3 python3-pip python3-venv python3-tk
    ;;
  dnf)    as_root dnf    install -y python3 python3-pip python3-virtualenv python3-tkinter tk ;;
  yum)    as_root yum    install -y python3 python3-pip python3-tkinter tk ;;
  pacman) as_root pacman -Sy --noconfirm python python-pip tk ;;
  zypper)
    as_root zypper refresh
    as_root zypper install -y python3 python3-pip python3-virtualenv python3-tk
    ;;
  apk)
    as_root apk add --no-cache python3 py3-pip py3-virtualenv tcl tk
    python3 -m ensurepip || true
    ;;
esac
need python3 || { echo "!! python3 not found after installation"; exit 1; }

# ==================== 2) Environment variable ===
mkdir -p "$FC_VENVS"

BASHRC="$HOME/.bashrc"
ZSHRC="$HOME/.zshrc"

for rc in "$BASHRC" "$ZSHRC"; do
  [ -f "$rc" ] || continue
  append_once "$rc" ""
  append_once "$rc" "# --- FCclasses env ---"
  append_once "$rc" "export FC_VENVS=\"$FC_VENVS\""
  append_once "$rc" "export $VENV_ACTIVATE_VAR=\"$VENV_PATH/bin/activate\""
  append_once "$rc" "alias FCCLASS='source \"\$$VENV_ACTIVATE_VAR\"'"
  append_once "$rc" "# --- end FCclasses env ---"
done

export FC_VENVS

# ==================== 3) Virtualenv creation ====
python3 -m venv "$VENV_PATH" --prompt "$APP_NAME" 2>/dev/null || true

echo
echo "Installation completed."
echo "   Please reload your shell configuration run the following command: source ~/.bashrc"
