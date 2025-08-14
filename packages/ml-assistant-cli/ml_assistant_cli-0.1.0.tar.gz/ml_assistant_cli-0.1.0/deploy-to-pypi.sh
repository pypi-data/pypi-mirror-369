#!/bin/bash
# Deploy ML Assistant CLI to PyPI

set -e

echo "🚀 Deploying ML Assistant CLI to PyPI"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pip setuptools wheel twine build

# Build the package
echo "🔨 Building package..."
python -m build

# Check the package
echo "🔍 Checking package..."
twine check dist/*

# Show package info
echo "📋 Package contents:"
ls -la dist/

echo "📤 Ready to upload to PyPI!"
echo "Run: twine upload dist/*"
echo "Or for TestPyPI: twine upload --repository testpypi dist/*"

# Optional: Upload to TestPyPI first
read -p "Upload to TestPyPI first? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to TestPyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Uploaded to TestPyPI: https://test.pypi.org/project/mlcli/"
    echo "Test install with: pip install --index-url https://test.pypi.org/simple/ mlcli"
fi

# Upload to production PyPI
read -p "Upload to production PyPI? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to PyPI..."
    twine upload dist/*
    echo "✅ Published to PyPI: https://pypi.org/project/mlcli/"
    echo "🎉 Users can now install with: pip install mlcli"
fi