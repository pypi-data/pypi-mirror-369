#!/bin/bash
set -e

# Set defaults
PUID=${PUID:-1000}
PGID=${PGID:-1000}

# Change user/group IDs if provided
groupmod -o -g "$PGID" appuser
usermod -o -u "$PUID" appuser

# Set ownership
chown -R appuser:appuser /app /tmp/subtitles

# Execute command as appuser
exec gosu appuser "$@"