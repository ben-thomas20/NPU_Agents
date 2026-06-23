#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
claude -p "Brief me on my next candidate meeting using the brief-founder skill."
