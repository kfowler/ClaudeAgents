#!/bin/bash

# PostgreSQL Backup Script for Claude Agents
# This script creates compressed backups with rotation

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
DB_NAME="${POSTGRES_DB:-claude_agents}"
DB_USER="${POSTGRES_USER:-claude}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_backup_${TIMESTAMP}.sql.gz"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to perform backup
perform_backup() {
    log "Starting backup of database: $DB_NAME"
    
    # Set password from file if available
    if [ -f "/run/secrets/postgres_password" ]; then
        export PGPASSWORD=$(cat /run/secrets/postgres_password)
    fi
    
    # Create backup
    pg_dump \
        --host=postgres \
        --port=5432 \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=plain \
        | gzip > "$BACKUP_FILE"
    
    # Verify backup was created
    if [ -f "$BACKUP_FILE" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log "Backup completed successfully: $BACKUP_FILE (Size: $BACKUP_SIZE)"
    else
        log "ERROR: Backup file was not created!"
        exit 1
    fi
}

# Function to clean old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days"
    
    find "$BACKUP_DIR" -name "${DB_NAME}_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "${DB_NAME}_backup_*.sql.gz" -type f | wc -l)
    log "Cleanup completed. Remaining backups: $REMAINING_BACKUPS"
}

# Function to validate database connection
validate_connection() {
    log "Validating database connection..."
    
    if [ -f "/run/secrets/postgres_password" ]; then
        export PGPASSWORD=$(cat /run/secrets/postgres_password)
    fi
    
    if ! pg_isready --host=postgres --port=5432 --username="$DB_USER" --dbname="$DB_NAME"; then
        log "ERROR: Cannot connect to database!"
        exit 1
    fi
    
    log "Database connection validated"
}

# Function to check disk space
check_disk_space() {
    AVAILABLE_SPACE=$(df "$BACKUP_DIR" | tail -1 | awk '{print $4}')
    REQUIRED_SPACE=1048576  # 1GB in KB
    
    if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
        log "WARNING: Low disk space in backup directory (Available: ${AVAILABLE_SPACE}KB)"
    else
        log "Sufficient disk space available for backup"
    fi
}

# Function to send backup metrics (if monitoring is available)
send_metrics() {
    local status=$1
    local backup_size=$2
    
    # Send metrics to monitoring system if available
    # This would typically integrate with your monitoring stack
    log "Backup metrics - Status: $status, Size: $backup_size"
}

# Function to test backup integrity
test_backup_integrity() {
    log "Testing backup integrity..."
    
    # Test if the backup can be read
    if gzip -t "$BACKUP_FILE"; then
        log "Backup integrity test passed"
        return 0
    else
        log "ERROR: Backup integrity test failed!"
        return 1
    fi
}

# Main execution
main() {
    log "=== Starting PostgreSQL Backup Process ==="
    
    # Pre-flight checks
    validate_connection
    check_disk_space
    
    # Perform backup
    if perform_backup; then
        # Test backup integrity
        if test_backup_integrity; then
            BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            send_metrics "success" "$BACKUP_SIZE"
            log "Backup process completed successfully"
        else
            send_metrics "failed" "0"
            exit 1
        fi
    else
        send_metrics "failed" "0"
        log "ERROR: Backup process failed!"
        exit 1
    fi
    
    # Cleanup old backups
    cleanup_old_backups
    
    log "=== Backup Process Finished ==="
}

# Handle signals for graceful shutdown
trap 'log "Backup process interrupted"; exit 1' INT TERM

# Run main function
main "$@"