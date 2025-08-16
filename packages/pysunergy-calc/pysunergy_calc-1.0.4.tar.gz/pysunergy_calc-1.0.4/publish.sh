#!/bin/bash

set -e

# Remove old build files
echo "Removing old dist/ directory..."
rm -rf dist

# Build new distribution
echo "Building package with hatchling..."
uv run python -m hatchling build

# Publish to PyPI
echo "Uploading to PyPI..."
uv run twine upload dist/*

echo "Build and publish complete!"
