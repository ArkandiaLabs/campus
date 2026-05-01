#!/usr/bin/env bash
set -euo pipefail

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

is_sensitive_path() {
  local path="$1"
  local normalized="${path#./}"

  case "$normalized" in
    .env.example|*.env.example|.env.sample|*.env.sample|.env.template|*.env.template)
      return 1
      ;;
  esac

  if [[ "$normalized" =~ (^|/)\.env($|[.].+) ]]; then
    return 0
  fi
  if [[ "$normalized" =~ \.(pem|key)$ ]]; then
    return 0
  fi
  if [[ "$normalized" =~ (^|/)(id_rsa|id_ed25519)$ ]]; then
    return 0
  fi

  return 1
}

contains_sensitive_token() {
  local value="$1"

  if [[ -z "${value}" ]]; then
    return 1
  fi

  if echo "$value" | grep -Eq '(^|[^[:alnum:]_./-])\.env([.][[:alnum:]_.-]+)?([^[:alnum:]_.-]|$)'; then
    if ! echo "$value" | grep -Eq '(^|[^[:alnum:]_./-])\.env\.(example|sample|template)([^[:alnum:]_.-]|$)'; then
      return 0
    fi
  fi

  if echo "$value" | grep -Eqi '(^|[^[:alnum:]_./-])[[:alnum:]_./-]+\.(pem|key)([^[:alnum:]_.-]|$)'; then
    return 0
  fi

  if echo "$value" | grep -Eq '(^|[^[:alnum:]_./-])(id_rsa|id_ed25519)([^[:alnum:]_.-]|$)'; then
    return 0
  fi

  return 1
}

emit_deny() {
  local platform="$1"
  local reason="$2"

  if [[ "$platform" == "claude" ]]; then
    jq -nc --arg reason "$reason" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: $reason
      }
    }'
    return
  fi

  jq -nc --arg reason "$reason" '{
    permissionDecision: "deny",
    permissionDecisionReason: $reason
  }'
}

PLATFORM="$(detect_platform "$INPUT_JSON")"
TOOL_NAME="$(echo "$INPUT_JSON" | jq -r '.tool_name // .toolName // ""' | tr '[:upper:]' '[:lower:]')"
TOOL_ARGS_JSON="$(echo "$INPUT_JSON" | jq -c 'if .tool_input then .tool_input elif .toolArgs then (.toolArgs | fromjson? // {}) else {} end')"
COMMAND="$(echo "$TOOL_ARGS_JSON" | jq -r '.command // ""')"

if [[ "$TOOL_NAME" == "bash" ]] && contains_sensitive_token "$COMMAND"; then
  emit_deny "$PLATFORM" "Blocked by workshop policy: reading secrets (.env, key, pem) is not allowed."
  exit 0
fi

if [[ "$TOOL_NAME" == "read" || "$TOOL_NAME" == "view" ]]; then
  while IFS= read -r candidate; do
    if is_sensitive_path "$candidate"; then
      emit_deny "$PLATFORM" "Blocked by workshop policy: reading secrets (.env, key, pem) is not allowed."
      exit 0
    fi
  done < <(echo "$TOOL_ARGS_JSON" | jq -r '.file_path?, .path?, .target_file?, .old_path?, .new_path?, (.paths[]? // empty)' | sed '/^null$/d;/^$/d')
fi

exit 0
