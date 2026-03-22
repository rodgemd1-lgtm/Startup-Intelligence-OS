#!/bin/zsh
export BIND=0.0.0.0
export PORT=7842
cd /Users/mikerodgers/Startup-Intelligence-OS
exec /opt/homebrew/bin/node bin/claw-bridge-server.js
