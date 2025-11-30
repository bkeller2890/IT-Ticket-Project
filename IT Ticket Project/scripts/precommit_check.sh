#!/usr/bin/env bash
# Run pre-commit for files inside this project directory only and print diffs
# if it would change files. This avoids scanning the user's full git repo
# (for example when the git top-level is the Desktop folder).
set -euo pipefail

# Determine this project's root (script is in scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

python3 -m pip install -r requirements-dev.txt

# Get repository top-level and the project path relative to it
RTOP=$(git rev-parse --show-toplevel)
REL_PATH=$(python3 - <<PY
import os
project = os.path.abspath("$PROJECT_ROOT")
root = os.path.abspath("$RTOP")
print(os.path.relpath(project, root))
PY
)

# Collect tracked files under the project directory (handles spaces)
files=()
while IFS= read -r file; do
  files+=("$file")
done < <(git ls-files -- "$REL_PATH" || true)

if [ ${#files[@]} -gt 0 ]; then
  pre-commit run --files "${files[@]}" || true
else
  # Fallback: if there are no tracked files under this path, run all-files
  pre-commit run --all-files || true
fi

# Check git status only for the project path
if [ -n "$(git status --porcelain -- "$REL_PATH")" ]; then
  echo "pre-commit would modify tracked files. See the diff below:";
  git --no-pager status --porcelain -- "$REL_PATH"
  git --no-pager diff --no-prefix -- "$REL_PATH"
  exit 1
fi

echo "pre-commit check passed (no unstaged changes)."
