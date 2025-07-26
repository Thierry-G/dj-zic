#!/bin/bash

# Configuration
USER =XXXXXXX
LOCK_FILE="/var/lock/sync-uploads.lock"
DEST_IP="$1"
MODE="$2"
SSH_KEY="/home/thierry/.ssh/id_rsa_djzic"
RSYNC="/usr/bin/rsync"

# Usage check
if [ -z "$DEST_IP" ] || [ -z "$MODE" ]; then
  echo "Usage: $0 <destination_ip> <mode>"
  echo "Modes:"
  echo "  0 - Sync only stream.json (skip uploads)"
  echo "  1 - Sync both uploads and stream.json"
  exit 1
fi

# Locking mechanism
exec 200>"$LOCK_FILE"
flock -n 200 || {
  echo "Error: Script is already running (lock file exists at $LOCK_FILE)"
  exit 1
}
echo $$ >&200

# Cleanup on exit
trap 'rm -f "$LOCK_FILE"; exit' INT TERM EXIT

# Sync functions
sync_uploads() {
  echo "Syncing uploads directory (with --delete)..."
  $RSYNC -av --delete --no-times --rsync-path="sudo rsync" \
    -e "ssh -i $SSH_KEY" \
    "/var/www/html/admin/uploads/" \
    "${USER}@${DEST_IP}:/var/www/html/admin/uploads/"
  return $?
}

sync_stream() {
  echo "Syncing stream.json (with checksums)..."
  $RSYNC -avc --rsync-path="sudo rsync" \
    -e "ssh -i $SSH_KEY" \
    "/var/www/html/data/stream.json" \
    "${USER}@${DEST_IP}:/var/www/html/data/"
  return $?
}

# Main execution
case "$MODE" in
  0)
    sync_stream
    RESULT=$?
    ;;
  1)
    sync_uploads
    sync_stream
    RESULT=$?
    ;;
  *)
    echo "Error: Invalid mode '$MODE'. Use 0 or 1."
    RESULT=1
    ;;
esac

exit $RESULT