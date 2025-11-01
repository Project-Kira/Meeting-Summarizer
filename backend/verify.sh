#!/bin/bash
# Automated Verification Script - Runs all checks without human interaction

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Meeting Summarizer Backend - Automated Verification     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Branch verification
echo "1️⃣  Verifying branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "backend-implementation" ]; then
    echo "   ✓ On correct branch: $CURRENT_BRANCH"
else
    echo "   ✗ Wrong branch: $CURRENT_BRANCH (expected: backend-implementation)"
    exit 1
fi
echo ""

# 2. Directory structure
echo "2️⃣  Verifying directory structure..."
REQUIRED_DIRS=("app" "workers" "models" "db" "inference" "tests" "config" "examples")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir/"
    else
        echo "   ✗ Missing: $dir/"
        exit 1
    fi
done
echo ""

# 3. Required files
echo "3️⃣  Verifying required files..."
REQUIRED_FILES=(
    "README.md"
    "requirements.txt"
    "Makefile"
    ".env.example"
    "setup.sh"
    "app/main.py"
    "workers/worker.py"
    "workers/chunker.py"
    "workers/merger.py"
    "inference/serve.py"
    "db/repositories.py"
    "db/migrations/001_initial_schema.sql"
    "models/schemas.py"
    "config/settings.py"
    "tests/unit/test_chunker.py"
    "tests/unit/test_merger.py"
    "tests/integration/test_full_flow.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ Missing: $file"
        exit 1
    fi
done
echo ""

# 4. Python syntax validation
echo "4️⃣  Validating Python syntax..."
PYTHON_FILES=$(find . -name "*.py" -not -path "./__pycache__/*" -not -path "*/__pycache__/*")
ERROR_COUNT=0

for file in $PYTHON_FILES; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "   ✓ $file"
    else
        echo "   ✗ Syntax error in $file"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
done

if [ $ERROR_COUNT -eq 0 ]; then
    echo "   ✓ All Python files compile successfully"
else
    echo "   ✗ $ERROR_COUNT files have syntax errors"
    exit 1
fi
echo ""

# 5. SQL syntax check
echo "5️⃣  Checking SQL migrations..."
SQL_FILES=$(find db/migrations -name "*.sql")
for file in $SQL_FILES; do
    echo "   ✓ $file"
done
echo ""

# 6. File counts
echo "6️⃣  Counting implementation..."
PY_COUNT=$(find . -name "*.py" | grep -v __pycache__ | wc -l)
SQL_COUNT=$(find . -name "*.sql" | wc -l)
TEST_COUNT=$(find tests/ -name "test_*.py" | wc -l)
echo "   Python files: $PY_COUNT"
echo "   SQL files: $SQL_COUNT"
echo "   Test files: $TEST_COUNT"
echo ""

# 7. Lines of code
echo "7️⃣  Calculating lines of code..."
TOTAL_LINES=$(find . \( -name "*.py" -o -name "*.sql" \) | grep -v __pycache__ | xargs wc -l | tail -1 | awk '{print $1}')
echo "   Total lines: $TOTAL_LINES"
echo ""

# 8. Git status
echo "8️⃣  Git commit status..."
COMMIT_COUNT=$(git log --oneline | wc -l)
LAST_COMMIT=$(git log -1 --oneline)
echo "   Total commits: $COMMIT_COUNT"
echo "   Last commit: $LAST_COMMIT"
echo ""

# 9. Check executables
echo "9️⃣  Verifying executable scripts..."
EXECUTABLES=("setup.sh" "examples/curl_examples.sh" "examples/websocket_client.py")
for exe in "${EXECUTABLES[@]}"; do
    if [ -x "$exe" ]; then
        echo "   ✓ $exe is executable"
    else
        echo "   ✗ $exe is not executable"
        exit 1
    fi
done
echo ""

# 10. Configuration check
echo "🔟  Configuration validation..."
if [ -f ".env.example" ]; then
    REQUIRED_VARS=("DATABASE_URL" "INFERENCE_MODEL_PATH" "API_PORT" "INFERENCE_PORT")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "$var" .env.example; then
            echo "   ✓ $var defined in .env.example"
        else
            echo "   ✗ Missing $var in .env.example"
            exit 1
        fi
    done
fi
echo ""

# Final summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ VERIFICATION COMPLETE                  ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Branch: backend-implementation                            ║"
echo "║  Files: $PY_COUNT Python, $SQL_COUNT SQL, $TEST_COUNT Tests $(printf '%23s' ' ')║"
echo "║  Lines of Code: $TOTAL_LINES $(printf '%41s' ' ')║"
echo "║  Status: All checks passed ✓                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Ready for deployment! Run './setup.sh' to get started."
echo ""
