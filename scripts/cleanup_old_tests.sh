#!/bin/bash
# Script to clean up old test files that have been reorganized

# Navigate to the project root
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# List of test files to remove
files_to_remove=(
    "$dir/tests/test_api.py"
    "$dir/tests/test_crud.py"
    "$dir/tests/test_database.py"
    "$dir/tests/test_models.py"
)

# Remove files if they exist
for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        echo "Removing $file"
        rm "$file"
    else
        echo "File not found: $file"
    fi
done

echo "Cleanup complete"
