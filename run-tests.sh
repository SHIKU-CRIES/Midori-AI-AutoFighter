#!/bin/bash

status=0
failed_tests=()
timeout_tests=()
ROOT_DIR=$(pwd)

run_test() {
  local cmd="$1"
  local name="$2"

  timeout 15 bash -c "$cmd"
  local result=$?

  if [ $result -eq 124 ]; then
    timeout_tests+=("$name")
    if [ $status -eq 0 ]; then
      status=124
    fi
  elif [ $result -ne 0 ]; then
    failed_tests+=("$name")
    if [ $status -eq 0 ]; then
      status=$result
    fi
  fi
}

# High-level start message
echo "Starting test run"

# Backend tests
cd backend

# Set up Python environment once
uv venv && uv sync

echo "Starting backend tests..."
for file in $(find tests -maxdepth 1 -name "test_*.py" -type f -printf "%f\n" | sort); do
  echo "Running backend test: $file"
  run_test "uv run pytest tests/$file" "backend tests/$file"
done
echo "Finished backend tests"
cd "$ROOT_DIR"

# Frontend tests
cd frontend

# Install Node dependencies
bun install

echo "Starting frontend tests..."
for file in $(find tests -maxdepth 1 -name "*.test.js" -type f -printf "%f\n" | sort); do
  echo "Running frontend test: $file"
  run_test "bun test tests/$file" "frontend tests/$file"
done
echo "Finished frontend tests"
cd "$ROOT_DIR"

# Summary
if [ ${#failed_tests[@]} -eq 0 ] && [ ${#timeout_tests[@]} -eq 0 ]; then
  echo "All tests passed."
else
  if [ ${#failed_tests[@]} -ne 0 ]; then
    echo "Failed tests:"
    for t in "${failed_tests[@]}"; do
      echo "  $t"
    done
  fi
  if [ ${#timeout_tests[@]} -ne 0 ]; then
    echo "Timed out (>15s) tests:"
    for t in "${timeout_tests[@]}"; do
      echo "  $t"
    done
  fi
fi

# Final summary message
if [ $status -eq 0 ]; then
  echo "Test run complete: success"
else
  echo "Test run complete: failure"
fi

exit $status

