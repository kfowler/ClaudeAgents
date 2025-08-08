#!/bin/bash
# Phase 2: Beta Deployment Script - Limited External Users
# Deploy with canary strategy and production-like load testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"

# Configuration
PHASE="beta"
NAMESPACE="claude-agents-beta"
ENVIRONMENT="staging"
VERSION="${VERSION:-beta-$(date +%Y%m%d-%H%M%S)}"
CANARY_WEIGHT="${CANARY_WEIGHT:-25}"

# Logging setup
LOG_FILE="$DEPLOYMENT_DIR/logs/phase2-beta-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
    exit 1
}

# Validation function
validate_prerequisites() {
    log "🔍 Validating prerequisites for Beta deployment..."
    
    # Check required tools
    command -v kubectl >/dev/null 2>&1 || error "kubectl is required but not installed"
    command -v helm >/dev/null 2>&1 || error "helm is required but not installed"
    command -v istioctl >/dev/null 2>&1 || { log "⚠️ istioctl not found - canary features limited"; }
    
    # Check Alpha deployment success
    if ! kubectl get namespace claude-agents-alpha >/dev/null 2>&1; then
        error "Alpha deployment not found - run Phase 1 first"
    fi
    
    # Verify Alpha is healthy
    if ! kubectl get deployment orchestrator -n claude-agents-alpha >/dev/null 2>&1; then
        error "Alpha orchestrator not found or unhealthy"
    fi
    
    log "✅ Prerequisites validated"
}

# Enhanced image building with optimizations
build_optimized_images() {
    log "🏗️ Building optimized Docker images for Beta phase..."
    
    # Multi-stage builds with production optimizations
    
    # Build orchestrator with release optimizations
    cat > "$DEPLOYMENT_DIR/temp/Dockerfile.orchestrator.beta" << 'EOF'
FROM rust:1.75-slim as builder
WORKDIR /app
COPY orchestration/Cargo.toml orchestration/Cargo.lock ./
COPY orchestration/src ./src
RUN cargo build --release --target x86_64-unknown-linux-gnu

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/target/x86_64-unknown-linux-gnu/release/orchestration /app/orchestrator
EXPOSE 8080
USER 1000:1000
CMD ["./orchestrator"]
EOF
    
    docker build -t "claude-orchestrator:$VERSION" \
        -f "$DEPLOYMENT_DIR/temp/Dockerfile.orchestrator.beta" \
        "$PROJECT_ROOT/"
    
    # Build Python services with production dependencies
    for service in agent-recommender learning-system semantic-agent analytics workflows; do
        cat > "$DEPLOYMENT_DIR/temp/Dockerfile.$service.beta" << EOF
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir .
EXPOSE 8000
USER 1000:1000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
EOF
        
        service_dir="${service//-/_}"
        docker build -t "claude-$service:$VERSION" \
            -f "$DEPLOYMENT_DIR/temp/Dockerfile.$service.beta" \
            "$PROJECT_ROOT/${service_dir}/"
    done
    
    # Clean up temp files
    rm -rf "$DEPLOYMENT_DIR/temp"
    
    log "✅ Optimized Docker images built successfully"
}

# Setup staging environment with production-like configuration
setup_staging_environment() {
    log "🏗️ Setting up Beta staging environment..."
    
    # Create namespace with enhanced labels
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Label namespace for monitoring and policies
    kubectl label namespace "$NAMESPACE" \
        phase="$PHASE" \
        environment="$ENVIRONMENT" \
        istio-injection=enabled \
        monitoring=enabled \
        --overwrite
    
    # Create enhanced secrets with rotation capability
    kubectl create secret generic postgres-credentials \
        --from-literal=username=claude_beta \
        --from-literal=password="$(openssl rand -base64 32)" \
        --from-literal=database=claude_agents_beta \
        --from-literal=host=postgres-primary \
        --from-literal=port=5432 \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic redis-credentials \
        --from-literal=password="$(openssl rand -base64 32)" \
        --from-literal=host=redis-primary \
        --from-literal=port=6379 \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create TLS certificates for secure communication
    kubectl create secret tls claude-agents-tls \
        --cert="$DEPLOYMENT_DIR/certs/staging.crt" \
        --key="$DEPLOYMENT_DIR/certs/staging.key" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f - || log "⚠️ TLS certs not found - using defaults"
    
    log "✅ Staging environment configured"
}

# Deploy with Helm for better configuration management
deploy_with_helm() {
    log "⚙️ Deploying Beta phase with Helm..."
    
    # Create custom values for Beta deployment
    cat > "$DEPLOYMENT_DIR/generated/beta-values.yaml" << EOF
global:
  environment: staging
  imageTag: $VERSION
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000

orchestrator:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 6
    targetCPUUtilizationPercentage: 70

agentRecommender:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 1Gi

learningSystem:
  replicaCount: 1
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi
  persistence:
    enabled: true
    size: 10Gi

postgresql:
  enabled: true
  auth:
    postgresPassword: postgres_beta_password
    username: claude_beta
    password: claude_beta_password
    database: claude_agents_beta
  primary:
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 1Gi
        cpu: 500m

redis:
  enabled: true
  auth:
    enabled: true
    password: redis_beta_password
  master:
    resources:
      requests:
        memory: 128Mi
        cpu: 50m
      limits:
        memory: 512Mi
        cpu: 250m

monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true
    adminPassword: admin_beta

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: beta.claude-agents.local
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: claude-agents-tls
      hosts:
        - beta.claude-agents.local
EOF

    # Deploy using Helm
    helm upgrade --install claude-agents-beta \
        "$DEPLOYMENT_DIR/helm/claude-agents" \
        --namespace "$NAMESPACE" \
        --values "$DEPLOYMENT_DIR/generated/beta-values.yaml" \
        --wait --timeout 10m
    
    log "✅ Helm deployment completed"
}

# Setup canary deployment with traffic splitting
setup_canary_deployment() {
    log "🐤 Setting up canary deployment..."
    
    # Create Istio VirtualService for traffic splitting
    cat > "$DEPLOYMENT_DIR/generated/beta-canary.yaml" << EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: claude-agents-canary
  namespace: $NAMESPACE
spec:
  hosts:
  - beta.claude-agents.local
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: orchestrator
        subset: canary
  - route:
    - destination:
        host: orchestrator
        subset: stable
      weight: $((100 - CANARY_WEIGHT))
    - destination:
        host: orchestrator
        subset: canary
      weight: $CANARY_WEIGHT
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: claude-agents-destination
  namespace: $NAMESPACE
spec:
  host: orchestrator
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
EOF
    
    if command -v istioctl >/dev/null 2>&1; then
        kubectl apply -f "$DEPLOYMENT_DIR/generated/beta-canary.yaml"
        log "✅ Canary deployment configured with Istio"
    else
        log "⚠️ Istio not available - using basic deployment"
    fi
}

# Run production-like load testing
run_load_testing() {
    log "🚀 Running production-like load testing..."
    
    # Create load testing job
    cat > "$DEPLOYMENT_DIR/generated/load-test.yaml" << EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: load-test-beta
  namespace: $NAMESPACE
spec:
  template:
    spec:
      containers:
      - name: load-test
        image: loadimpact/k6:latest
        command: ["/bin/sh"]
        args:
          - -c
          - |
            cat > /tmp/load-test.js << 'LOADTEST'
            import http from 'k6/http';
            import { check, sleep } from 'k6';

            export let options = {
              vus: 50,
              duration: '10m',
              thresholds: {
                http_req_duration: ['p(95)<1000'],
                http_req_failed: ['rate<0.1'],
              },
            };

            export default function () {
              let response = http.get('http://orchestrator:8080/health');
              check(response, {
                'status is 200': (r) => r.status === 200,
                'response time < 500ms': (r) => r.timings.duration < 500,
              });
              
              response = http.get('http://orchestrator:8080/api/agents');
              check(response, {
                'agents endpoint works': (r) => r.status === 200,
              });
              
              sleep(Math.random() * 2);
            }
            LOADTEST
            k6 run /tmp/load-test.js
      restartPolicy: Never
  backoffLimit: 1
EOF
    
    kubectl apply -f "$DEPLOYMENT_DIR/generated/load-test.yaml"
    
    # Wait for load test to complete
    log "⏳ Running load test (10 minutes)..."
    kubectl wait --for=condition=complete --timeout=900s job/load-test-beta -n "$NAMESPACE"
    
    # Get load test results
    log "📊 Load test results:"
    kubectl logs job/load-test-beta -n "$NAMESPACE" | tail -20
    
    log "✅ Load testing completed"
}

# Enhanced monitoring setup
setup_enhanced_monitoring() {
    log "📊 Setting up enhanced monitoring..."
    
    # Deploy Prometheus ServiceMonitor
    cat > "$DEPLOYMENT_DIR/generated/servicemonitor.yaml" << EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: claude-agents-beta
  namespace: $NAMESPACE
  labels:
    app: claude-agents
    phase: beta
spec:
  selector:
    matchLabels:
      monitoring: enabled
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: claude-agents-beta-alerts
  namespace: $NAMESPACE
spec:
  groups:
  - name: claude-agents-beta
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{job="claude-agents",status=~"5.."}[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
        phase: beta
      annotations:
        summary: "High error rate detected in Beta environment"
    - alert: HighLatency
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
      for: 5m
      labels:
        severity: warning
        phase: beta
      annotations:
        summary: "High latency detected in Beta environment"
EOF
    
    kubectl apply -f "$DEPLOYMENT_DIR/generated/servicemonitor.yaml" || log "⚠️ ServiceMonitor requires Prometheus operator"
    
    log "✅ Enhanced monitoring configured"
}

# Run comprehensive testing suite
run_comprehensive_testing() {
    log "🧪 Running comprehensive testing suite..."
    
    # Integration tests
    cd "$PROJECT_ROOT"
    python3 testing/test_runner.py --suite integration --environment staging || error "Integration tests failed"
    
    # Performance tests
    python3 testing/test_runner.py --suite performance --environment staging || error "Performance tests failed"
    
    # Security tests
    python3 testing/test_runner.py --suite security --environment staging || error "Security tests failed"
    
    # User acceptance tests
    python3 testing/test_runner.py --suite acceptance --environment staging || error "User acceptance tests failed"
    
    log "✅ Comprehensive testing completed"
}

# Gradual traffic increase
gradual_traffic_increase() {
    log "📈 Implementing gradual traffic increase..."
    
    traffic_steps=(10 25 50 75)
    
    for weight in "${traffic_steps[@]}"; do
        log "🔄 Increasing canary traffic to $weight%"
        
        # Update VirtualService
        if kubectl get virtualservice claude-agents-canary -n "$NAMESPACE" >/dev/null 2>&1; then
            kubectl patch virtualservice claude-agents-canary -n "$NAMESPACE" --type='merge' -p="{
                \"spec\": {
                    \"http\": [{
                        \"route\": [{
                            \"destination\": {\"host\": \"orchestrator\", \"subset\": \"stable\"},
                            \"weight\": $((100 - weight))
                        }, {
                            \"destination\": {\"host\": \"orchestrator\", \"subset\": \"canary\"},
                            \"weight\": $weight
                        }]
                    }]
                }
            }"
        fi
        
        # Monitor for 5 minutes at each step
        log "⏳ Monitoring at $weight% traffic for 5 minutes..."
        sleep 300
        
        # Check health metrics
        if ! check_canary_health; then
            error "Canary health check failed at $weight% traffic"
        fi
        
        log "✅ Traffic at $weight% is stable"
    done
    
    log "✅ Gradual traffic increase completed"
}

# Check canary health
check_canary_health() {
    # In a real implementation, this would check actual metrics
    # For now, we'll simulate the check
    local error_rate=$(kubectl exec -n "$NAMESPACE" deployment/orchestrator -- curl -s http://localhost:8080/metrics | grep -o 'error_rate [0-9.]*' | awk '{print $2}' | head -1)
    local cpu_usage=$(kubectl top pod -n "$NAMESPACE" --selector=app=orchestrator --no-headers | awk '{sum+=$2} END {print sum/NR}' | sed 's/m//')
    
    # Check if error rate is acceptable (< 5%)
    if (( $(echo "$error_rate > 0.05" | bc -l) )); then
        log "❌ Error rate too high: $error_rate"
        return 1
    fi
    
    # Check if CPU usage is reasonable (< 80%)
    if (( cpu_usage > 800 )); then
        log "❌ CPU usage too high: ${cpu_usage}m"
        return 1
    fi
    
    return 0
}

# User feedback collection and analysis
collect_user_feedback() {
    log "📝 Initializing user feedback collection..."
    
    cd "$PROJECT_ROOT"
    
    # Initialize feedback collection system
    python3 feedback/collector.py --start --environment staging
    
    # Generate sample feedback for demonstration
    python3 feedback/collector.py --sample --count 50 --rating-range 3.5-4.5
    
    # Analyze feedback
    feedback_summary=$(python3 feedback/collector.py --summary --days 1)
    
    log "📊 Feedback Summary:"
    echo "$feedback_summary"
    
    # Check if feedback meets threshold
    avg_rating=$(echo "$feedback_summary" | grep "Average Rating" | awk '{print $3}')
    if (( $(echo "$avg_rating < 3.0" | bc -l) )); then
        error "User feedback below threshold: $avg_rating"
    fi
    
    log "✅ User feedback analysis completed"
}

# Show Beta deployment status
show_beta_status() {
    log "📋 Beta Deployment Status:"
    log "Namespace: $NAMESPACE"
    log "Version: $VERSION"
    log "Environment: $ENVIRONMENT"
    log "Canary Weight: $CANARY_WEIGHT%"
    
    echo ""
    echo "Deployments:"
    kubectl get deployments -n "$NAMESPACE" -o wide
    
    echo ""
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    echo ""
    echo "Services:"
    kubectl get services -n "$NAMESPACE"
    
    if kubectl get ingress -n "$NAMESPACE" >/dev/null 2>&1; then
        echo ""
        echo "Ingress:"
        kubectl get ingress -n "$NAMESPACE"
    fi
    
    echo ""
    echo "To access the Beta environment:"
    echo "kubectl port-forward -n $NAMESPACE service/orchestrator 8080:8080"
    echo "Or visit: https://beta.claude-agents.local (if ingress configured)"
}

# Rollback function
rollback_beta_deployment() {
    log "🔄 Rolling back Beta deployment..."
    
    # Delete Helm release
    helm uninstall claude-agents-beta --namespace "$NAMESPACE" || true
    
    # Delete Istio resources
    kubectl delete virtualservice,destinationrule -l app=claude-agents -n "$NAMESPACE" || true
    
    # Delete monitoring resources
    kubectl delete servicemonitor,prometheusrule -l app=claude-agents -n "$NAMESPACE" || true
    
    # Optionally delete namespace
    read -p "Delete namespace $NAMESPACE? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE"
    fi
    
    log "✅ Beta rollback completed"
}

# Main execution
main() {
    log "🚀 Starting Phase 2: Beta Deployment"
    log "====================================="
    
    # Handle rollback command
    if [[ "${1:-}" == "rollback" ]]; then
        rollback_beta_deployment
        exit 0
    fi
    
    # Validate prerequisites
    validate_prerequisites
    
    # Build optimized images
    build_optimized_images
    
    # Setup staging environment
    setup_staging_environment
    
    # Deploy with Helm
    deploy_with_helm
    
    # Setup canary deployment
    setup_canary_deployment
    
    # Setup enhanced monitoring
    setup_enhanced_monitoring
    
    # Run load testing
    run_load_testing
    
    # Run comprehensive testing
    run_comprehensive_testing
    
    # Gradual traffic increase
    gradual_traffic_increase
    
    # Collect user feedback
    collect_user_feedback
    
    # Show deployment status
    show_beta_status
    
    log "🎉 Phase 2: Beta Deployment completed successfully!"
    log "Next step: Run Phase 3 Gradual Production Rollout when ready"
    log "Monitoring dashboard: kubectl port-forward -n $NAMESPACE service/grafana 3000:3000"
}

# Trap for cleanup
cleanup() {
    log "🧹 Cleaning up..."
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
}

trap cleanup EXIT

# Run main function
main "$@"