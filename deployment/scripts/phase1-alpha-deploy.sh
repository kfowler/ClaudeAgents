#!/bin/bash
# Phase 1: Alpha Deployment Script - Internal Testing
# Deploy Claude Code 2.0 enhancements to development environment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"

# Configuration
PHASE="alpha"
NAMESPACE="claude-agents-alpha"
ENVIRONMENT="development"
VERSION="${VERSION:-alpha-$(date +%Y%m%d-%H%M%S)}"

# Logging setup
LOG_FILE="$DEPLOYMENT_DIR/logs/phase1-alpha-$(date +%Y%m%d-%H%M%S).log"
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
    log "🔍 Validating prerequisites for Alpha deployment..."
    
    # Check required tools
    command -v kubectl >/dev/null 2>&1 || error "kubectl is required but not installed"
    command -v docker >/dev/null 2>&1 || error "docker is required but not installed"
    command -v python3 >/dev/null 2>&1 || error "python3 is required but not installed"
    
    # Check Kubernetes context
    if ! kubectl config current-context >/dev/null 2>&1; then
        error "No Kubernetes context configured"
    fi
    
    log "✅ Prerequisites validated"
}

# Pre-deployment validation
run_pre_deployment_validation() {
    log "🧪 Running pre-deployment validation..."
    
    cd "$PROJECT_ROOT"
    
    if ! python3 rollout_validation.py --phase pre-deployment; then
        error "Pre-deployment validation failed"
    fi
    
    log "✅ Pre-deployment validation passed"
}

# Build and tag Docker images
build_images() {
    log "🏗️ Building Docker images for Alpha phase..."
    
    # Build orchestrator image
    docker build -t "claude-orchestrator:$VERSION" \
        -f "$DEPLOYMENT_DIR/dockerfiles/Dockerfile.orchestrator" \
        "$PROJECT_ROOT/orchestration/"
    
    # Build agent recommender image
    docker build -t "claude-agent-recommender:$VERSION" \
        -f "$DEPLOYMENT_DIR/dockerfiles/Dockerfile.analysis" \
        "$PROJECT_ROOT/analysis/"
    
    # Build learning system image
    docker build -t "claude-learning-system:$VERSION" \
        -f "$DEPLOYMENT_DIR/dockerfiles/Dockerfile.learning" \
        "$PROJECT_ROOT/learning_system/"
    
    # Build semantic agent image
    docker build -t "claude-semantic-agent:$VERSION" \
        -f "$DEPLOYMENT_DIR/dockerfiles/Dockerfile.semantic" \
        "$PROJECT_ROOT/semantic_agent_selection/"
    
    # Build analytics image
    docker build -t "claude-analytics:$VERSION" \
        -f "$DEPLOYMENT_DIR/dockerfiles/Dockerfile.analytics" \
        "$PROJECT_ROOT/analytics/"
    
    # Build workflows image
    docker build -t "claude-workflows:$VERSION" \
        -f "$DEPLOYMENT_DIR/dockerfiles/Dockerfile.workflows" \
        "$PROJECT_ROOT/workflows/"
    
    log "✅ Docker images built successfully"
}

# Create namespace and secrets
setup_namespace() {
    log "🏗️ Setting up Alpha namespace and secrets..."
    
    # Create namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Label namespace
    kubectl label namespace "$NAMESPACE" phase="$PHASE" environment="$ENVIRONMENT" --overwrite
    
    # Create secrets
    kubectl create secret generic postgres-credentials \
        --from-literal=username=claude_alpha \
        --from-literal=password="$(openssl rand -base64 32)" \
        --from-literal=database=claude_agents_alpha \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic redis-credentials \
        --from-literal=password="$(openssl rand -base64 32)" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic jwt-secret \
        --from-literal=key="$(openssl rand -base64 64)" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log "✅ Namespace and secrets configured"
}

# Generate deployment manifests
generate_manifests() {
    log "📝 Generating Alpha deployment manifests..."
    
    MANIFEST_DIR="$DEPLOYMENT_DIR/generated/$PHASE"
    mkdir -p "$MANIFEST_DIR"
    
    # PostgreSQL deployment
    cat > "$MANIFEST_DIR/postgres.yaml" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: $NAMESPACE
  labels:
    app: postgres
    phase: $PHASE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
        phase: $PHASE
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: database
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        resources:
          limits:
            cpu: 500m
            memory: 1Gi
          requests:
            cpu: 100m
            memory: 256Mi
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: postgres
EOF

    # Redis deployment
    cat > "$MANIFEST_DIR/redis.yaml" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: $NAMESPACE
  labels:
    app: redis
    phase: $PHASE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
        phase: $PHASE
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--requirepass", "\$(REDIS_PASSWORD)"]
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: password
        resources:
          limits:
            cpu: 250m
            memory: 512Mi
          requests:
            cpu: 50m
            memory: 128Mi
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: $NAMESPACE
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
EOF

    # Qdrant deployment
    cat > "$MANIFEST_DIR/qdrant.yaml" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
  namespace: $NAMESPACE
  labels:
    app: qdrant
    phase: $PHASE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
        phase: $PHASE
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:v1.8.4
        resources:
          limits:
            cpu: 500m
            memory: 1Gi
          requests:
            cpu: 100m
            memory: 256Mi
        ports:
        - containerPort: 6333
        - containerPort: 6334
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant
  namespace: $NAMESPACE
spec:
  ports:
  - name: http
    port: 6333
    targetPort: 6333
  - name: grpc
    port: 6334
    targetPort: 6334
  selector:
    app: qdrant
EOF

    # Orchestrator deployment
    cat > "$MANIFEST_DIR/orchestrator.yaml" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator
  namespace: $NAMESPACE
  labels:
    app: orchestrator
    phase: $PHASE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: orchestrator
  template:
    metadata:
      labels:
        app: orchestrator
        phase: $PHASE
    spec:
      containers:
      - name: orchestrator
        image: claude-orchestrator:$VERSION
        env:
        - name: RUST_ENV
          value: development
        - name: DATABASE_URL
          value: postgresql://\$(POSTGRES_USER):\$(POSTGRES_PASSWORD)@postgres:5432/\$(POSTGRES_DB)
        - name: REDIS_URL
          value: redis://:\$(REDIS_PASSWORD)@redis:6379
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: database
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: password
        resources:
          limits:
            cpu: 250m
            memory: 512Mi
          requests:
            cpu: 50m
            memory: 128Mi
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: orchestrator
  namespace: $NAMESPACE
spec:
  ports:
  - port: 8080
    targetPort: 8080
  selector:
    app: orchestrator
EOF

    log "✅ Deployment manifests generated"
}

# Deploy to Alpha environment
deploy_alpha() {
    log "🚀 Deploying to Alpha environment..."
    
    MANIFEST_DIR="$DEPLOYMENT_DIR/generated/$PHASE"
    
    # Deploy in order: databases first, then services
    kubectl apply -f "$MANIFEST_DIR/postgres.yaml"
    kubectl apply -f "$MANIFEST_DIR/redis.yaml"
    kubectl apply -f "$MANIFEST_DIR/qdrant.yaml"
    
    # Wait for databases to be ready
    log "⏳ Waiting for databases to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/postgres -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/redis -n "$NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/qdrant -n "$NAMESPACE"
    
    # Deploy application services
    kubectl apply -f "$MANIFEST_DIR/orchestrator.yaml"
    
    # Wait for application to be ready
    log "⏳ Waiting for orchestrator to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/orchestrator -n "$NAMESPACE"
    
    log "✅ Alpha deployment completed"
}

# Run smoke tests
run_smoke_tests() {
    log "🧪 Running smoke tests..."
    
    # Port forward to orchestrator for testing
    kubectl port-forward -n "$NAMESPACE" service/orchestrator 8080:8080 &
    PORT_FORWARD_PID=$!
    
    # Wait for port forward to be ready
    sleep 5
    
    # Run basic health check
    if curl -f http://localhost:8080/health >/dev/null 2>&1; then
        log "✅ Health check passed"
    else
        kill $PORT_FORWARD_PID 2>/dev/null || true
        error "Health check failed"
    fi
    
    # Test basic API endpoints
    if curl -f http://localhost:8080/api/agents >/dev/null 2>&1; then
        log "✅ API endpoints accessible"
    else
        kill $PORT_FORWARD_PID 2>/dev/null || true
        error "API endpoints not accessible"
    fi
    
    # Clean up port forward
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    log "✅ Smoke tests passed"
}

# Monitor Alpha deployment
monitor_deployment() {
    log "📊 Monitoring Alpha deployment..."
    
    # Start monitoring script in background
    cd "$PROJECT_ROOT"
    python3 monitoring/monitor_runner.py --start --interval 30 &
    MONITOR_PID=$!
    
    # Monitor for 5 minutes
    log "⏳ Monitoring system for 5 minutes..."
    sleep 300
    
    # Stop monitoring
    kill $MONITOR_PID 2>/dev/null || true
    
    log "✅ Initial monitoring completed"
}

# Run post-deployment validation
run_post_deployment_validation() {
    log "🔍 Running post-deployment validation..."
    
    cd "$PROJECT_ROOT"
    
    if ! python3 rollout_validation.py --phase post-deployment; then
        error "Post-deployment validation failed"
    fi
    
    log "✅ Post-deployment validation passed"
}

# Show deployment status
show_deployment_status() {
    log "📋 Alpha Deployment Status:"
    log "Namespace: $NAMESPACE"
    log "Version: $VERSION"
    log "Environment: $ENVIRONMENT"
    
    echo ""
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    echo ""
    echo "Services:"
    kubectl get services -n "$NAMESPACE"
    
    echo ""
    echo "To access the orchestrator:"
    echo "kubectl port-forward -n $NAMESPACE service/orchestrator 8080:8080"
    echo "Then visit: http://localhost:8080"
}

# Rollback function
rollback_deployment() {
    log "🔄 Rolling back Alpha deployment..."
    
    # Delete all resources in namespace
    kubectl delete all --all -n "$NAMESPACE"
    
    # Optionally delete namespace
    read -p "Delete namespace $NAMESPACE? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE"
    fi
    
    log "✅ Rollback completed"
}

# Main execution
main() {
    log "🚀 Starting Phase 1: Alpha Deployment"
    log "======================================"
    
    # Handle rollback command
    if [[ "${1:-}" == "rollback" ]]; then
        rollback_deployment
        exit 0
    fi
    
    # Validate prerequisites
    validate_prerequisites
    
    # Run pre-deployment validation
    run_pre_deployment_validation
    
    # Build images
    build_images
    
    # Setup namespace and secrets
    setup_namespace
    
    # Generate manifests
    generate_manifests
    
    # Deploy to Alpha
    deploy_alpha
    
    # Run smoke tests
    run_smoke_tests
    
    # Monitor deployment
    monitor_deployment
    
    # Run post-deployment validation
    run_post_deployment_validation
    
    # Show status
    show_deployment_status
    
    log "🎉 Phase 1: Alpha Deployment completed successfully!"
    log "Next step: Run Phase 2 Beta deployment when ready"
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