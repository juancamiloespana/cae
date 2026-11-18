#!/bin/bash
# Usage: ./sync_to_win.sh [folder] [--delete]
# Syncs WSL -> Windows. Defaults to full project root.

SRC="/home/personal/cod_lin/CAE_lin/CAE1_lin"
DST="/mnt/d/cod/CAE1_win"

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

echo "WSL -> Windows"
echo "  From: $SRC"
echo "  To:   $DST"
[ -n "$DELETE_FLAG" ] && echo "  Mode: --delete enabled"
echo ""

rsync -av $DELETE_FLAG "$SRC/" "$DST/"
