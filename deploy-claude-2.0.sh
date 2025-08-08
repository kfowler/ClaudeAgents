#!/bin/bash
# Master Deployment Script for Claude Code 2.0 Enhanced Agent System
# Orchestrates all four phases of the rollout with comprehensive validation and monitoring

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$SCRIPT_DIR/deployment"

# Global configuration
VERSION="${VERSION:-$(date +%Y%m%d-%H%M%S)}"
SKIP_VALIDATION="${SKIP_VALIDATION:-false}"
DRY_RUN="${DRY_RUN:-false}"
AUTO_PROCEED="${AUTO_PROCEED:-false}"

# Logging setup
LOG_FILE="$DEPLOYMENT_DIR/logs/master-deployment-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
    exit 1
}

warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" | tee -a "$LOG_FILE"
}

success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1" | tee -a "$LOG_FILE"
}

# Print banner
print_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    Claude Code 2.0 Enhancement System                       ║
║                         Phased Rollout Deployment                           ║
║                                                                              ║
║  🚀 Phase 1: Alpha Deployment (Internal Testing)                            ║
║  📊 Phase 2: Beta Deployment (Limited External Users)                       ║
║  📈 Phase 3: Gradual Production Rollout (10% → 100%)                        ║
║  🏁 Phase 4: Full Production & Optimization                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
}

# Show help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS] [COMMAND]

COMMANDS:
    deploy          Execute full phased rollout (default)
    phase1          Execute Phase 1 (Alpha) only
    phase2          Execute Phase 2 (Beta) only  
    phase3          Execute Phase 3 (Gradual Production) only
    phase4          Execute Phase 4 (Full Production) only
    rollback        Execute rollback procedure
    status          Show deployment status
    validate        Run validation framework only
    monitor         Start monitoring dashboard
    help            Show this help message

OPTIONS:
    --version=VERSION           Set deployment version (default: timestamp)
    --skip-validation           Skip validation steps (not recommended)
    --dry-run                   Show what would be deployed without executing
    --auto-proceed              Automatically proceed between phases
    --phase=PHASE              Start from specific phase (alpha|beta|gradual|full)
    --environment=ENV          Target environment (development|staging|production)
    
ENVIRONMENT VARIABLES:
    VERSION                     Deployment version tag
    SKIP_VALIDATION            Skip validation (true/false)
    DRY_RUN                    Dry run mode (true/false)
    AUTO_PROCEED               Auto proceed mode (true/false)
    KUBECONFIG                 Kubernetes config file path

EXAMPLES:
    # Full deployment with all phases
    $0 deploy
    
    # Deploy specific phase
    $0 phase1
    $0 --phase=beta deploy
    
    # Dry run to see what would be deployed
    $0 --dry-run deploy
    
    # Deploy with custom version
    $0 --version=v2.1.0 deploy
    
    # Auto-proceed without manual confirmations
    $0 --auto-proceed deploy
    
    # Rollback deployment
    $0 rollback
    
    # Check status
    $0 status

For more information, see: https://github.com/company/claude-agents/docs/deployment
EOF
}

# Validate prerequisites
validate_prerequisites() {
    log "🔍 Validating deployment prerequisites..."
    
    # Check required tools
    local required_tools=("kubectl" "helm" "docker" "python3" "curl" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "$tool is required but not installed"
        fi
    done
    
    # Check Kubernetes access
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error "Cannot access Kubernetes cluster"
    fi
    
    # Check Python dependencies
    if ! python3 -c "import psutil, git" 2>/dev/null; then
        warning "Some Python dependencies missing - installing..."
        pip3 install psutil gitpython 2>/dev/null || error "Failed to install Python dependencies"
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        error "Docker daemon not accessible"
    fi
    
    # Validate deployment scripts exist
    local scripts=(
        "$DEPLOYMENT_DIR/scripts/phase1-alpha-deploy.sh"
        "$DEPLOYMENT_DIR/scripts/phase2-beta-deploy.sh"
        "$DEPLOYMENT_DIR/scripts/phase3-gradual-production.sh"
        "$DEPLOYMENT_DIR/scripts/phase4-full-production.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ ! -x "$script" ]]; then
            error "Deployment script not found or not executable: $script"
        fi
    done
    
    # Check validation framework
    if [[ -f "$SCRIPT_DIR/rollout_validation.py" ]] && [[ "$SKIP_VALIDATION" != "true" ]]; then
        if ! python3 "$SCRIPT_DIR/rollout_validation.py" --phase pre-deployment --dry-run >/dev/null 2>&1; then
            warning "Validation framework check failed"
        fi
    fi
    
    success "Prerequisites validation completed"
}

# Get user confirmation
get_confirmation() {
    local message="$1"
    local default="${2:-n}"
    
    if [[ "$AUTO_PROCEED" == "true" ]]; then
        log "Auto-proceeding: $message"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would prompt: $message"
        return 0
    fi
    
    read -p "$message (y/n) [default: $default]: " -n 1 -r
    echo
    if [[ -z "$REPLY" ]]; then
        REPLY="$default"
    fi
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Execute phase with error handling and validation
execute_phase() {
    local phase_number="$1"
    local phase_name="$2"  
    local script_path="$3"
    local validation_timeout="${4:-600}"
    
    log "🚀 Starting $phase_name"
    log "=================================================="
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would execute $script_path"
        return 0
    fi
    
    local start_time=$(date +%s)
    local phase_success=false
    
    # Pre-phase validation
    if [[ "$SKIP_VALIDATION" != "true" ]]; then
        log "🔍 Running pre-phase validation..."
        if ! python3 "$SCRIPT_DIR/rollout_validation.py" --phase pre-deployment; then
            error "Pre-phase validation failed for $phase_name"
        fi
    fi
    
    # Execute deployment script
    log "📦 Executing deployment script..."
    if "$script_path"; then
        phase_success=true
        log "✅ $phase_name deployment completed"
    else
        error "$phase_name deployment failed"
    fi
    
    # Post-phase validation
    if [[ "$phase_success" == "true" ]] && [[ "$SKIP_VALIDATION" != "true" ]]; then
        log "🔍 Running post-phase validation..."
        if ! timeout "$validation_timeout" python3 "$SCRIPT_DIR/rollout_validation.py" --phase post-deployment; then
            warning "Post-phase validation failed or timed out for $phase_name"
            
            if get_confirmation "Continue despite validation issues?"; then
                log "Proceeding despite validation warnings"
            else
                log "🔄 Initiating rollback due to validation failure..."
                execute_rollback "$phase_number"
                error "$phase_name failed validation"
            fi
        fi
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    success "$phase_name completed successfully in ${duration}s"
    
    # Ask for permission to continue to next phase
    if [[ "$AUTO_PROCEED" != "true" ]]; then
        if ! get_confirmation "Proceed to next phase?"; then
            log "Deployment paused by user"
            return 1
        fi
    fi
    
    return 0
}

# Execute Phase 1: Alpha Deployment
execute_phase1() {
    execute_phase 1 "Phase 1: Alpha Deployment (Internal Testing)" \
        "$DEPLOYMENT_DIR/scripts/phase1-alpha-deploy.sh" 600
}

# Execute Phase 2: Beta Deployment  
execute_phase2() {
    execute_phase 2 "Phase 2: Beta Deployment (Limited External Users)" \
        "$DEPLOYMENT_DIR/scripts/phase2-beta-deploy.sh" 900
}

# Execute Phase 3: Gradual Production Rollout
execute_phase3() {
    execute_phase 3 "Phase 3: Gradual Production Rollout" \
        "$DEPLOYMENT_DIR/scripts/phase3-gradual-production.sh" 1800
}

# Execute Phase 4: Full Production
execute_phase4() {
    execute_phase 4 "Phase 4: Full Production & Optimization" \
        "$DEPLOYMENT_DIR/scripts/phase4-full-production.sh" 1200
}

# Execute rollback
execute_rollback() {
    local failed_phase="${1:-unknown}"
    
    log "🚨 Executing rollback procedure..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would execute rollback"
        return 0
    fi
    
    # Determine rollback strategy based on failed phase
    case "$failed_phase" in
        1)
            log "Rolling back Phase 1..."
            "$DEPLOYMENT_DIR/scripts/phase1-alpha-deploy.sh" rollback
            ;;
        2)
            log "Rolling back Phase 2..."
            "$DEPLOYMENT_DIR/scripts/phase2-beta-deploy.sh" rollback
            ;;
        3|4)
            log "Rolling back Production deployment..."
            "$DEPLOYMENT_DIR/scripts/phase3-gradual-production.sh" rollback
            ;;
        *)
            log "Executing comprehensive rollback..."
            python3 "$SCRIPT_DIR/rollback/rollback_manager.py" --execute --type full
            ;;
    esac
    
    success "Rollback procedure completed"
}

# Show deployment status across all environments
show_deployment_status() {
    log "📋 Claude Code 2.0 Deployment Status"
    log "===================================="
    
    echo ""
    echo "=== Alpha Environment ==="
    if kubectl get namespace claude-agents-alpha >/dev/null 2>&1; then
        echo "✅ Alpha environment exists"
        kubectl get deployments -n claude-agents-alpha --no-headers 2>/dev/null | wc -l | xargs echo "Deployments:"
        kubectl get pods -n claude-agents-alpha --no-headers 2>/dev/null | grep -c Running | xargs echo "Running pods:"
    else
        echo "❌ Alpha environment not found"
    fi
    
    echo ""
    echo "=== Beta Environment ==="
    if kubectl get namespace claude-agents-beta >/dev/null 2>&1; then
        echo "✅ Beta environment exists"
        kubectl get deployments -n claude-agents-beta --no-headers 2>/dev/null | wc -l | xargs echo "Deployments:"
        kubectl get pods -n claude-agents-beta --no-headers 2>/dev/null | grep -c Running | xargs echo "Running pods:"
    else
        echo "❌ Beta environment not found"
    fi
    
    echo ""
    echo "=== Production Environment ==="
    if kubectl get namespace claude-agents-prod >/dev/null 2>&1; then
        echo "✅ Production environment exists"
        kubectl get deployments -n claude-agents-prod --no-headers 2>/dev/null | wc -l | xargs echo "Deployments:"
        kubectl get pods -n claude-agents-prod --no-headers 2>/dev/null | grep -c Running | xargs echo "Running pods:"
        
        # Check traffic distribution
        if kubectl get virtualservice claude-agents-routing -n claude-agents-prod >/dev/null 2>&1; then
            echo "Traffic routing configured"
        fi
    else
        echo "❌ Production environment not found"
    fi
    
    echo ""
    echo "=== Overall Status ==="
    local total_namespaces=0
    local healthy_namespaces=0
    
    for ns in claude-agents-alpha claude-agents-beta claude-agents-prod; do
        total_namespaces=$((total_namespaces + 1))
        if kubectl get namespace "$ns" >/dev/null 2>&1; then
            local running_pods
            running_pods=$(kubectl get pods -n "$ns" --no-headers 2>/dev/null | grep -c Running || echo "0")
            if [[ "$running_pods" -gt 0 ]]; then
                healthy_namespaces=$((healthy_namespaces + 1))
            fi
        fi
    done
    
    echo "Healthy environments: $healthy_namespaces/$total_namespaces"
    
    if [[ "$healthy_namespaces" -eq 3 ]]; then
        echo "🎉 All environments are healthy"
    elif [[ "$healthy_namespaces" -gt 0 ]]; then
        echo "⚠️ Partial deployment detected"
    else
        echo "❌ No environments are healthy"
    fi
}

# Run validation framework only
run_validation_only() {
    log "🔍 Running comprehensive validation framework..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would run validation framework"
        return 0
    fi
    
    cd "$SCRIPT_DIR"
    python3 rollout_validation.py --phase full-validation
}

# Start monitoring dashboard
start_monitoring() {
    log "📊 Starting monitoring dashboard..."
    
    # Check if Grafana is available
    for ns in claude-agents-alpha claude-agents-beta claude-agents-prod; do
        if kubectl get service grafana -n "$ns" >/dev/null 2>&1; then
            log "Found Grafana in namespace $ns"
            echo "Starting port-forward to Grafana dashboard..."
            echo "Dashboard will be available at: http://localhost:3000"
            echo "Default credentials: admin/admin"
            
            kubectl port-forward -n "$ns" service/grafana 3000:3000
            return 0
        fi
    done
    
    warning "Grafana not found in any namespace"
    echo "To access monitoring, deploy one of the phases first"
}

# Full deployment orchestration
execute_full_deployment() {
    local start_phase="${1:-1}"
    
    log "🚀 Starting Claude Code 2.0 Full Deployment"
    log "Version: $VERSION"
    log "Start Phase: $start_phase"
    log "Auto Proceed: $AUTO_PROCEED"
    log "Skip Validation: $SKIP_VALIDATION"
    log "Dry Run: $DRY_RUN"
    log "============================================="
    
    local deployment_start_time=$(date +%s)
    
    # Execute phases based on start phase
    case "$start_phase" in
        1)
            execute_phase1 && \
            execute_phase2 && \
            execute_phase3 && \
            execute_phase4
            ;;
        2)
            execute_phase2 && \
            execute_phase3 && \
            execute_phase4
            ;;
        3)
            execute_phase3 && \
            execute_phase4
            ;;
        4)
            execute_phase4
            ;;
        *)
            error "Invalid start phase: $start_phase"
            ;;
    esac
    
    local deployment_success=$?
    local deployment_end_time=$(date +%s)
    local total_duration=$((deployment_end_time - deployment_start_time))
    
    if [[ $deployment_success -eq 0 ]]; then
        success "🎉 Claude Code 2.0 deployment completed successfully!"
        log "Total deployment time: ${total_duration}s"
        log "All phases executed successfully"
        
        # Show final status
        show_deployment_status
        
        # Display access information
        echo ""
        echo "=== Access Information ==="
        echo "Alpha Environment: kubectl port-forward -n claude-agents-alpha service/orchestrator 8080:8080"
        echo "Beta Environment: kubectl port-forward -n claude-agents-beta service/orchestrator 8081:8080" 
        echo "Production: https://api.claude-agents.prod"
        echo "Monitoring: kubectl port-forward -n claude-agents-prod service/grafana 3000:3000"
        echo ""
        echo "📚 Documentation: $SCRIPT_DIR/docs/"
        echo "🔍 Logs: $LOG_FILE"
        
    else
        error "❌ Deployment failed after ${total_duration}s"
    fi
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version=*)
                VERSION="${1#*=}"
                shift
                ;;
            --skip-validation)
                SKIP_VALIDATION="true"
                shift
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --auto-proceed)
                AUTO_PROCEED="true"
                shift
                ;;
            --phase=*)
                START_PHASE="${1#*=}"
                shift
                ;;
            --environment=*)
                TARGET_ENV="${1#*=}"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            deploy)
                COMMAND="deploy"
                shift
                ;;
            phase1)
                COMMAND="phase1"
                shift
                ;;
            phase2)
                COMMAND="phase2"
                shift
                ;;
            phase3)
                COMMAND="phase3"
                shift
                ;;
            phase4)
                COMMAND="phase4"
                shift
                ;;
            rollback)
                COMMAND="rollback"
                shift
                ;;
            status)
                COMMAND="status"
                shift
                ;;
            validate)
                COMMAND="validate"
                shift
                ;;
            monitor)
                COMMAND="monitor"
                shift
                ;;
            help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown argument: $1"
                ;;
        esac
    done
}

# Main execution function
main() {
    # Set defaults
    local COMMAND="${COMMAND:-deploy}"
    local START_PHASE="${START_PHASE:-1}"
    local TARGET_ENV="${TARGET_ENV:-}"
    
    # Parse command line arguments
    parse_args "$@"
    
    # Print banner
    print_banner
    
    # Validate prerequisites
    validate_prerequisites
    
    # Execute command
    case "$COMMAND" in
        deploy)
            case "$START_PHASE" in
                alpha|1) execute_full_deployment 1 ;;
                beta|2) execute_full_deployment 2 ;;
                gradual|3) execute_full_deployment 3 ;;
                full|4) execute_full_deployment 4 ;;
                *) execute_full_deployment 1 ;;
            esac
            ;;
        phase1)
            execute_phase1
            ;;
        phase2)
            execute_phase2
            ;;
        phase3)
            execute_phase3
            ;;
        phase4)
            execute_phase4
            ;;
        rollback)
            execute_rollback
            ;;
        status)
            show_deployment_status
            ;;
        validate)
            run_validation_only
            ;;
        monitor)
            start_monitoring
            ;;
        *)
            error "Unknown command: $COMMAND"
            ;;
    esac
}

# Trap for cleanup
cleanup() {
    log "🧹 Performing cleanup..."
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
}

trap cleanup EXIT

# Execute main function
main "$@"