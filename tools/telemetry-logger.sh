#!/bin/bash

# Growth Command Telemetry Logger
# Privacy-preserving usage tracking for growth command validation
#
# Usage:
#   source tools/telemetry-logger.sh
#   log_command_start "growth:conversion-audit"
#   log_command_complete "growth:conversion-audit" 4 24
#   log_command_failed "growth:conversion-audit" "error message"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TELEMETRY_DIR="${PROJECT_ROOT}/.claude-telemetry/growth"

# Ensure telemetry directory exists
mkdir -p "${TELEMETRY_DIR}"

# Generate privacy-preserving session ID (hashed)
get_session_id() {
    # Use user + process ID + timestamp, then hash
    echo "${USER}-$$-$(date +%s)" | shasum -a 256 | cut -d' ' -f1
}

# Get current timestamp in ISO-8601 format
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Log command start
log_command_start() {
    local command_name="$1"
    local log_file="${TELEMETRY_DIR}/${command_name#growth:}.log"
    local session_id=$(get_session_id)

    # Store session ID for later use
    export GROWTH_TELEMETRY_SESSION_ID="${session_id}"
    export GROWTH_TELEMETRY_START_TIME=$(date +%s)

    local log_entry=$(cat <<EOF
{"timestamp":"$(get_timestamp)","command":"${command_name}","session_id":"${session_id}","status":"started"}
EOF
)

    echo "${log_entry}" >> "${log_file}"
}

# Log command completion
log_command_complete() {
    local command_name="$1"
    local phases_completed="${2:-0}"
    local execution_time_minutes="${3:-0}"
    local log_file="${TELEMETRY_DIR}/${command_name#growth:}.log"
    local session_id="${GROWTH_TELEMETRY_SESSION_ID:-$(get_session_id)}"

    # Calculate execution time if not provided
    if [ "${execution_time_minutes}" -eq 0 ] && [ -n "${GROWTH_TELEMETRY_START_TIME}" ]; then
        local end_time=$(date +%s)
        local duration_seconds=$((end_time - GROWTH_TELEMETRY_START_TIME))
        execution_time_minutes=$((duration_seconds / 60))
    fi

    local log_entry=$(cat <<EOF
{"timestamp":"$(get_timestamp)","command":"${command_name}","session_id":"${session_id}","status":"completed","execution_time_minutes":${execution_time_minutes},"phases_completed":${phases_completed}}
EOF
)

    echo "${log_entry}" >> "${log_file}"

    # Clean up environment variables
    unset GROWTH_TELEMETRY_SESSION_ID
    unset GROWTH_TELEMETRY_START_TIME
}

# Log command failure
log_command_failed() {
    local command_name="$1"
    local error_type="${2:-unknown}"
    local log_file="${TELEMETRY_DIR}/${command_name#growth:}.log"
    local session_id="${GROWTH_TELEMETRY_SESSION_ID:-$(get_session_id)}"

    # Calculate execution time
    local execution_time_minutes=0
    if [ -n "${GROWTH_TELEMETRY_START_TIME}" ]; then
        local end_time=$(date +%s)
        local duration_seconds=$((end_time - GROWTH_TELEMETRY_START_TIME))
        execution_time_minutes=$((duration_seconds / 60))
    fi

    local log_entry=$(cat <<EOF
{"timestamp":"$(get_timestamp)","command":"${command_name}","session_id":"${session_id}","status":"failed","execution_time_minutes":${execution_time_minutes},"error_type":"${error_type}"}
EOF
)

    echo "${log_entry}" >> "${log_file}"

    # Clean up environment variables
    unset GROWTH_TELEMETRY_SESSION_ID
    unset GROWTH_TELEMETRY_START_TIME
}

# Log partial completion (user abandoned mid-execution)
log_command_partial() {
    local command_name="$1"
    local phases_completed="${2:-0}"
    local log_file="${TELEMETRY_DIR}/${command_name#growth:}.log"
    local session_id="${GROWTH_TELEMETRY_SESSION_ID:-$(get_session_id)}"

    # Calculate execution time
    local execution_time_minutes=0
    if [ -n "${GROWTH_TELEMETRY_START_TIME}" ]; then
        local end_time=$(date +%s)
        local duration_seconds=$((end_time - GROWTH_TELEMETRY_START_TIME))
        execution_time_minutes=$((duration_seconds / 60))
    fi

    local log_entry=$(cat <<EOF
{"timestamp":"$(get_timestamp)","command":"${command_name}","session_id":"${session_id}","status":"partial","execution_time_minutes":${execution_time_minutes},"phases_completed":${phases_completed}}
EOF
)

    echo "${log_entry}" >> "${log_file}"

    # Clean up environment variables
    unset GROWTH_TELEMETRY_SESSION_ID
    unset GROWTH_TELEMETRY_START_TIME
}

# Generate usage report (for validation analysis)
generate_usage_report() {
    local report_file="${TELEMETRY_DIR}/usage-report-$(date +%Y%m%d).txt"

    echo "Growth Commands Usage Report - $(date +%Y-%m-%d)" > "${report_file}"
    echo "=======================================" >> "${report_file}"
    echo "" >> "${report_file}"

    for log_file in "${TELEMETRY_DIR}"/*.log; do
        if [ -f "${log_file}" ]; then
            local command_name=$(basename "${log_file}" .log)
            local total_invocations=$(wc -l < "${log_file}" | tr -d ' ')
            local completed=$(grep -c '"status":"completed"' "${log_file}" || echo "0")
            local failed=$(grep -c '"status":"failed"' "${log_file}" || echo "0")
            local partial=$(grep -c '"status":"partial"' "${log_file}" || echo "0")
            local started=$(grep -c '"status":"started"' "${log_file}" || echo "0")

            # Calculate unique sessions
            local unique_sessions=$(grep -o '"session_id":"[^"]*"' "${log_file}" | sort -u | wc -l | tr -d ' ')

            echo "Command: growth:${command_name}" >> "${report_file}"
            echo "  Total Log Entries: ${total_invocations}" >> "${report_file}"
            echo "  Started: ${started}" >> "${report_file}"
            echo "  Completed: ${completed}" >> "${report_file}"
            echo "  Failed: ${failed}" >> "${report_file}"
            echo "  Partial: ${partial}" >> "${report_file}"
            echo "  Unique Sessions: ${unique_sessions}" >> "${report_file}"

            # Calculate completion rate
            if [ "${started}" -gt 0 ]; then
                local completion_rate=$((completed * 100 / started))
                echo "  Completion Rate: ${completion_rate}%" >> "${report_file}"
            fi

            # Calculate average execution time
            local avg_time=$(grep '"execution_time_minutes":' "${log_file}" | grep -o '[0-9]\+' | awk '{sum+=$1; count++} END {if(count>0) print int(sum/count); else print 0}')
            echo "  Avg Execution Time: ${avg_time} minutes" >> "${report_file}"
            echo "" >> "${report_file}"
        fi
    done

    echo "Report generated: ${report_file}"
    cat "${report_file}"
}

# Export functions for use in other scripts
export -f get_session_id
export -f get_timestamp
export -f log_command_start
export -f log_command_complete
export -f log_command_failed
export -f log_command_partial
export -f generate_usage_report
