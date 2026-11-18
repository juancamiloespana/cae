#!/bin/bash
# Usage: ./sync_from_win.sh [folder] [--delete]
# Syncs Windows -> WSL. Defaults to full project root.

SRC="/mnt/d/cod/CAE1_win"
DST="/home/personal/cod_lin/CAE_lin/CAE1_lin"

FOLDER="${1:-}"
DELETE_FLAG=""

for arg in "$@"; do
    if [ "$arg" = "--delete" ]; then
        DELETE_FLAG="--delete"
    fi
done

if [ -n "$FOLDER" ] && [ "$FOLDER" != "--delete" ]; then
    SRC="$SRC/$FOLDER"
    DST="$DST/$FOLDER"
fi

echo "Windows -> WSL"
echo "  From: $SRC"
echo "  To:   $DST"
[ -n "$DELETE_FLAG" ] && echo "  Mode: --delete enabled"
echo ""

rsync -av $DELETE_FLAG "$SRC/" "$DST/"
