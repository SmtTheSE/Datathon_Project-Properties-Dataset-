#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip to ensure latest features
pip install --upgrade pip

# Install build dependencies first and separately
pip install setuptools wheel numpy==1.24.3 --no-cache-dir

# Install remaining requirements
pip install -r requirements.txt --no-cache-dir --only-binary :all: || pip install -r requirements.txt
