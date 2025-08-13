#!/usr/bin/env bash

# Parameters
NOVNC_DIR="${1}"
NOVNC_PROXY="${2}"
NOVNC_HOST="${3}"
NOVNC_PORT="${4}"

# Assure session uses HOME-dir as current working directory
cd "${HOME}"


# Start VNC server (tigerVNC)
"${NOVNC_DIR}/start-vnc-server.sh"

# Start Websockify webserver serving novnc.html
"${NOVNC_PROXY}" --listen "${NOVNC_PORT}" --web "${NOVNC_DIR}" --vnc 127.0.0.1:5900


