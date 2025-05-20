#!/usr/bin/env bash
# setup.sh — install all Python dependencies

# Upgrade core build tooling first
pip install --upgrade pip wheel setuptools

# Install packages strictly from pre-built wheels to avoid source builds
pip install --only-binary=:all: -r requirements.txt
