#!/bin/bash
# Pre-commit hook to ensure basic functionality works before committing

echo "🔍 Running basic pre-commit checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if required containers are running
echo "📋 Checking container status..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep telega2go

# Run basic functionality test
echo "🧪 Running basic functionality test..."
if ! python3 test_basic_functionality.py; then
    echo "❌ Basic functionality test failed! Please fix the issues before committing."
    echo "💡 Run 'python3 test_basic_functionality.py' to see detailed error messages."
    exit 1
fi

echo "✅ All basic tests passed! Proceeding with commit."
exit 0
