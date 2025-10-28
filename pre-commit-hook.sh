#!/bin/bash
# Pre-commit hook to ensure basic functionality works before committing

echo "🔍 Running pre-commit checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if required containers are running
echo "📋 Checking container status..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep telega2go

# Run the registration flow test
echo "🧪 Running registration flow test..."
if python3 test_registration_flow.py; then
    echo "✅ All tests passed! Proceeding with commit."
    exit 0
else
    echo "❌ Tests failed! Please fix the issues before committing."
    echo "💡 Run 'python3 test_registration_flow.py' to see detailed error messages."
    exit 1
fi
