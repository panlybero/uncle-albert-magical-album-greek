#!/usr/bin/env bash
# Uncle Albert's Magical Album (Greek Windows Edition) - Desktop Launcher
# Launches Το Μαγικό Άλμπουμ του Θείου Αλβέρτου with patched ScummVM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="$SCRIPT_DIR/bin/scummvm"
GAME_DIR="${1:-$SCRIPT_DIR/game_data}"

if [ ! -f "$BIN_PATH" ]; then
    echo "Error: ScummVM executable not found at $BIN_PATH"
    echo "Please build ScummVM using the patch in patches/ or download the release binary."
    exit 1
fi

if [ ! -d "$GAME_DIR" ]; then
    echo "Error: Game data directory not found at $GAME_DIR"
    echo "Usage: ./run_albert.sh [path/to/extracted/game_data]"
    exit 1
fi

echo "Launching Το Μαγικό Άλμπουμ του Θείου Αλβέρτου (Greek Edition)..."
"$BIN_PATH" \
    --path="$GAME_DIR" \
    --language=el \
    --platform=windows \
    mtropolis:albert1
