#!/usr/bin/env bash
set -u
set -o pipefail

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

INPUT_JSON="$(cat)"
if [[ -z "${INPUT_JSON// }" ]]; then
  exit 0
fi

detect_platform() {
  local payload="$1"
  if echo "$payload" | jq -e '.tool_name?' >/dev/null 2>&1; then
    echo "claude"
    return
  fi
  if echo "$payload" | jq -e '.toolName?' >/dev/null 2>&1; then
    echo "copilot"
    return
  fi
  echo "unknown"
}

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR" || exit 0

PLATFORM="$(detect_platform "$INPUT_JSON")"
TOOL_NAME="$(echo "$INPUT_JSON" | jq -r '.tool_name // .toolName // ""')"
TOOL_NAME_LOWER="$(echo "$TOOL_NAME" | tr '[:upper:]' '[:lower:]')"
TOOL_ARGS_JSON="$(echo "$INPUT_JSON" | jq -c 'if .tool_input then .tool_input elif .toolArgs then (.toolArgs | fromjson? // {}) else {} end')"
COMMAND="$(echo "$TOOL_ARGS_JSON" | jq -r '.command // ""')"
RESULT_TYPE="$(echo "$INPUT_JSON" | jq -r '.tool_result.resultType // .toolResult.resultType // "unknown"')"

LOG_DIR="$ROOT_DIR/.agent-hooks"
LOG_FILE="$LOG_DIR/tool-events.jsonl"
mkdir -p "$LOG_DIR"

is_relevant_tool=false
case "$TOOL_NAME_LOWER" in
  bash|edit|write|create|multiedit)
    is_relevant_tool=true
    ;;
esac

declare -a ACTIONS=()

if $is_relevant_tool; then
  declare -a CHANGED_FILES=()
  while IFS= read -r file; do
    CHANGED_FILES+=("$file")
  done < <(
    {
      git diff --name-only --diff-filter=ACMRTUXB
      git diff --cached --name-only --diff-filter=ACMRTUXB
      git ls-files --others --exclude-standard
    } | sort -u
  )

  declare -a PYTHON_FILES=()
  declare -a FRONTEND_TS_FILES=()

  for file in "${CHANGED_FILES[@]}"; do
    [[ -f "$file" ]] || continue

    if [[ "$file" =~ ^backend/.*\.py$ ]]; then
      PYTHON_FILES+=("${file#backend/}")
      continue
    fi

    if [[ "$file" =~ ^frontend/.*\.(ts|tsx)$ ]]; then
      FRONTEND_TS_FILES+=("${file#frontend/}")
    fi
  done

  if [[ ${#PYTHON_FILES[@]} -gt 0 ]]; then
    if command -v uv >/dev/null 2>&1 && (cd backend && uv run ruff format "${PYTHON_FILES[@]}" >/dev/null 2>&1); then
      ACTIONS+=("ruff-format:ok")
    else
      ACTIONS+=("ruff-format:fail")
    fi
  fi

  if [[ ${#FRONTEND_TS_FILES[@]} -gt 0 ]]; then
    if command -v pnpm >/dev/null 2>&1 && (cd frontend && pnpm eslint --fix --no-warn-ignored "${FRONTEND_TS_FILES[@]}" >/dev/null 2>&1); then
      ACTIONS+=("eslint-fix:ok")
    else
      ACTIONS+=("eslint-fix:fail")
    fi
  fi
fi

ACTIONS_JSON='[]'
if [[ ${#ACTIONS[@]} -gt 0 ]]; then
  ACTIONS_JSON="$(printf '%s\n' "${ACTIONS[@]}" | jq -R . | jq -s .)"
fi

jq -nc \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg platform "$PLATFORM" \
  --arg toolName "$TOOL_NAME" \
  --arg command "$COMMAND" \
  --arg resultType "$RESULT_TYPE" \
  --argjson actions "$ACTIONS_JSON" \
  '{
    timestamp: $timestamp,
    platform: $platform,
    event: "postToolUse",
    toolName: $toolName,
    command: $command,
    resultType: $resultType,
    actions: $actions
  }' >> "$LOG_FILE"

exit 0
