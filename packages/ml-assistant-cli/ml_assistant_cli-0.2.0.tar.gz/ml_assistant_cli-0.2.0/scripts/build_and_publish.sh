#!/bin/bash
# Build and publish ML Assistant CLI to PyPI

set -e

echo "🚀 Building and Publishing ML Assistant CLI"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pip setuptools wheel twine build

# Build the package
echo "🔨 Building package..."
python -m build

# Check the package
echo "🔍 Checking package..."
twine check dist/*

# Upload to TestPyPI first (optional)
echo "🧪 Upload to TestPyPI? (y/n)"
read -r upload_test
if [[ $upload_test == "y" ]]; then
    echo "📤 Uploading to TestPyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Uploaded to TestPyPI: https://test.pypi.org/project/mlcli/"
    echo "Test install with: pip install --index-url https://test.pypi.org/simple/ mlcli"
fi

# Upload to PyPI
echo "🌍 Upload to PyPI? (y/n)"
read -r upload_prod
if [[ $upload_prod == "y" ]]; then
    echo "📤 Uploading to PyPI..."
    twine upload dist/*
    echo "✅ Published to PyPI: https://pypi.org/project/mlcli/"
    echo "Install with: pip install mlcli"
fi

echo "🎉 Build and publish complete!"