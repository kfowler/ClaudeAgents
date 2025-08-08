#!/bin/bash
# Phase 3: Gradual Production Rollout Script
# Deploy to production with incremental traffic: 10% → 25% → 50% → 75% → 100%

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"

# Configuration
PHASE="gradual"
NAMESPACE="claude-agents-prod"
ENVIRONMENT="production"
VERSION="${VERSION:-v$(date +%Y%m%d-%H%M%S)}"

# Traffic rollout configuration
declare -a TRAFFIC_STEPS=(10 25 50 75 100)
declare -a MONITOR_DURATIONS=(900 1800 1800 3600 1800)  # Monitor time in seconds for each step

# Logging setup
LOG_FILE="$DEPLOYMENT_DIR/logs/phase3-gradual-$(date +%Y%m%d-%H%M%S).log"
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

# Advanced prerequisite validation
validate_production_prerequisites() {
    log "🔍 Validating production prerequisites..."
    
    # Check required tools
    local required_tools=("kubectl" "helm" "istioctl" "curl" "jq" "bc")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "$tool is required but not installed"
        fi
    done
    
    # Verify Beta deployment success
    if ! kubectl get namespace claude-agents-beta >/dev/null 2>&1; then
        error "Beta deployment not found - run Phase 2 first"
    fi
    
    # Check Beta health status
    local beta_health
    beta_health=$(kubectl get deployment orchestrator -n claude-agents-beta -o jsonpath='{.status.readyReplicas}')
    if [[ "$beta_health" -lt 1 ]]; then
        error "Beta deployment is not healthy"
    fi
    
    # Verify production cluster access
    local current_context
    current_context=$(kubectl config current-context)
    if [[ ! "$current_context" =~ prod ]]; then
        warning "Current context '$current_context' doesn't appear to be production"
        read -p "Continue with production deployment? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check resource availability
    local available_nodes
    available_nodes=$(kubectl get nodes --no-headers | grep -c Ready)
    if [[ "$available_nodes" -lt 3 ]]; then
        warning "Only $available_nodes nodes available - recommend at least 3 for production"
    fi
    
    log "✅ Production prerequisites validated"
}

# Setup production-grade secrets and configuration
setup_production_secrets() {
    log "🔐 Setting up production secrets and configuration..."
    
    # Create namespace with production labels
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply comprehensive labeling
    kubectl label namespace "$NAMESPACE" \
        phase="$PHASE" \
        environment="$ENVIRONMENT" \
        istio-injection=enabled \
        monitoring=enabled \
        backup=enabled \
        security-scan=enabled \
        --overwrite
    
    # Production database credentials with rotation
    kubectl create secret generic postgres-credentials \
        --from-literal=username=claude_prod \
        --from-literal=password="$(openssl rand -base64 32)" \
        --from-literal=database=claude_agents_prod \
        --from-literal=host=postgres-primary.claude-agents-prod.svc.cluster.local \
        --from-literal=port=5432 \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Production Redis credentials
    kubectl create secret generic redis-credentials \
        --from-literal=password="$(openssl rand -base64 64)" \
        --from-literal=host=redis-primary.claude-agents-prod.svc.cluster.local \
        --from-literal=port=6379 \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # JWT secrets with enhanced entropy
    kubectl create secret generic jwt-secrets \
        --from-literal=access-token-secret="$(openssl rand -base64 64)" \
        --from-literal=refresh-token-secret="$(openssl rand -base64 64)" \
        --from-literal=api-key-secret="$(openssl rand -base64 32)" \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Production TLS certificates
    if [[ -f "$DEPLOYMENT_DIR/certs/prod.crt" ]]; then
        kubectl create secret tls claude-agents-prod-tls \
            --cert="$DEPLOYMENT_DIR/certs/prod.crt" \
            --key="$DEPLOYMENT_DIR/certs/prod.key" \
            --namespace="$NAMESPACE" \
            --dry-run=client -o yaml | kubectl apply -f -
    else
        warning "Production TLS certificates not found - generating self-signed"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /tmp/prod.key -out /tmp/prod.crt \
            -subj "/C=US/ST=CA/L=SF/O=Claude/CN=claude-agents.prod"
        kubectl create secret tls claude-agents-prod-tls \
            --cert=/tmp/prod.crt --key=/tmp/prod.key \
            --namespace="$NAMESPACE"
        rm -f /tmp/prod.key /tmp/prod.crt
    fi
    
    log "✅ Production secrets configured"
}

# Deploy production infrastructure with high availability
deploy_production_infrastructure() {
    log "🏗️ Deploying production infrastructure..."
    
    # Create production Helm values with HA configuration
    cat > "$DEPLOYMENT_DIR/generated/production-values.yaml" << EOF
global:
  environment: production
  imageTag: $VERSION
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
    requests:
      cpu: 500m
      memory: 1Gi

# Orchestrator with high availability
orchestrator:
  replicaCount: 3
  image:
    repository: claude-orchestrator
    tag: $VERSION
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20
    targetCPUUtilizationPercentage: 60
    targetMemoryUtilizationPercentage: 70
  
  service:
    type: ClusterIP
    port: 8080
    annotations:
      prometheus.io/scrape: "true"
      prometheus.io/port: "9090"
  
  ingress:
    enabled: true
    className: nginx
    annotations:
      nginx.ingress.kubernetes.io/rate-limit: "1000"
      nginx.ingress.kubernetes.io/ssl-redirect: "true"
      nginx.ingress.kubernetes.io/proxy-body-size: "10m"
      nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
      nginx.ingress.kubernetes.io/proxy-send-timeout: "30"
      nginx.ingress.kubernetes.io/proxy-read-timeout: "30"
    hosts:
      - host: api.claude-agents.prod
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: claude-agents-prod-tls
        hosts:
          - api.claude-agents.prod

# Agent Recommender with scaling
agentRecommender:
  replicaCount: 3
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 15
    targetCPUUtilizationPercentage: 65

# Learning System with persistent storage
learningSystem:
  replicaCount: 2
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 8
  persistence:
    enabled: true
    size: 50Gi
    storageClass: fast-ssd

# Semantic Agent with vector storage
semanticAgent:
  replicaCount: 2
  resources:
    requests:
      cpu: 300m
      memory: 1Gi
    limits:
      cpu: 1500m
      memory: 3Gi
  persistence:
    enabled: true
    size: 100Gi
    storageClass: fast-ssd

# Analytics service
analytics:
  replicaCount: 2
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi

# Workflows service
workflows:
  replicaCount: 2
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi

# PostgreSQL with high availability
postgresql:
  enabled: true
  architecture: replication
  auth:
    postgresPassword: $(openssl rand -base64 32)
    username: claude_prod
    password: $(openssl rand -base64 32)
    database: claude_agents_prod
  
  primary:
    persistence:
      enabled: true
      size: 200Gi
      storageClass: fast-ssd
    resources:
      requests:
        memory: 2Gi
        cpu: 1000m
      limits:
        memory: 4Gi
        cpu: 2000m
    
  readReplicas:
    replicaCount: 2
    persistence:
      enabled: true
      size: 200Gi
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1000m

# Redis with clustering
redis:
  enabled: true
  architecture: replication
  auth:
    enabled: true
    password: $(openssl rand -base64 32)
  
  master:
    persistence:
      enabled: true
      size: 50Gi
      storageClass: fast-ssd
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1000m
  
  replica:
    replicaCount: 2
    persistence:
      enabled: true
      size: 50Gi
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 500m

# Qdrant with persistence
qdrant:
  enabled: true
  replicaCount: 2
  persistence:
    enabled: true
    size: 100Gi
    storageClass: fast-ssd
  resources:
    requests:
      cpu: 500m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 8Gi

# Enhanced monitoring
monitoring:
  enabled: true
  prometheus:
    enabled: true
    server:
      retention: "30d"
      persistence:
        enabled: true
        size: 100Gi
      resources:
        requests:
          cpu: 500m
          memory: 2Gi
        limits:
          cpu: 2000m
          memory: 8Gi
    
  grafana:
    enabled: true
    adminPassword: $(openssl rand -base64 16)
    persistence:
      enabled: true
      size: 10Gi
    
  alertmanager:
    enabled: true
    persistence:
      enabled: true
      size: 5Gi

# Network policies for security
networkPolicy:
  enabled: true
  ingress:
    enabled: true
    allowExternal: true
  egress:
    enabled: true
    allowExternal: false
    allowSpecific:
      - ports: [443, 80]
        protocols: [TCP]

# Pod disruption budgets
podDisruptionBudget:
  enabled: true
  minAvailable: 2

# Backup configuration
backup:
  enabled: true
  schedule: "0 2 * * *"
  retention: "7d"
  storage:
    size: 500Gi
    storageClass: standard
EOF

    # Deploy using Helm with production settings
    helm upgrade --install claude-agents-prod \
        "$DEPLOYMENT_DIR/helm/claude-agents" \
        --namespace "$NAMESPACE" \
        --values "$DEPLOYMENT_DIR/generated/production-values.yaml" \
        --wait --timeout 15m \
        --atomic
    
    log "✅ Production infrastructure deployed"
}

# Setup advanced traffic management with Istio
setup_production_traffic_management() {
    log "🌐 Setting up advanced traffic management..."
    
    # Create Istio Gateway
    cat > "$DEPLOYMENT_DIR/generated/production-gateway.yaml" << EOF
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: claude-agents-gateway
  namespace: $NAMESPACE
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: claude-agents-prod-tls
    hosts:
    - "api.claude-agents.prod"
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "api.claude-agents.prod"
    tls:
      httpsRedirect: true
EOF

    # Create initial VirtualService with 0% new version traffic
    cat > "$DEPLOYMENT_DIR/generated/production-virtualservice.yaml" << EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: claude-agents-routing
  namespace: $NAMESPACE
spec:
  hosts:
  - "api.claude-agents.prod"
  gateways:
  - claude-agents-gateway
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: orchestrator
        subset: new
  - route:
    - destination:
        host: orchestrator
        subset: stable
      weight: 100
    - destination:
        host: orchestrator
        subset: new
      weight: 0
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: claude-agents-destination
  namespace: $NAMESPACE
spec:
  host: orchestrator
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 10
    circuitBreaker:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: stable
    labels:
      version: stable
  - name: new
    labels:
      version: new
EOF

    kubectl apply -f "$DEPLOYMENT_DIR/generated/production-gateway.yaml"
    kubectl apply -f "$DEPLOYMENT_DIR/generated/production-virtualservice.yaml"
    
    log "✅ Traffic management configured"
}

# Deploy new version as canary
deploy_canary_version() {
    log "🐤 Deploying canary version..."
    
    # Create canary deployment
    kubectl patch deployment orchestrator -n "$NAMESPACE" -p '{
        "spec": {
            "template": {
                "metadata": {
                    "labels": {
                        "version": "stable"
                    }
                }
            }
        }
    }'
    
    # Create new deployment for canary
    kubectl create deployment orchestrator-new \
        --image="claude-orchestrator:$VERSION" \
        --replicas=1 \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | \
        kubectl apply -f -
    
    # Label canary deployment
    kubectl patch deployment orchestrator-new -n "$NAMESPACE" -p '{
        "spec": {
            "template": {
                "metadata": {
                    "labels": {
                        "app": "orchestrator",
                        "version": "new"
                    }
                }
            }
        }
    }'
    
    # Wait for canary to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/orchestrator-new -n "$NAMESPACE"
    
    log "✅ Canary version deployed"
}

# Gradual traffic shifting with comprehensive monitoring
execute_gradual_rollout() {
    log "📈 Executing gradual production rollout..."
    
    local step_count=${#TRAFFIC_STEPS[@]}
    
    for ((i=0; i<step_count; i++)); do
        local traffic_weight=${TRAFFIC_STEPS[i]}
        local monitor_duration=${MONITOR_DURATIONS[i]}
        local stable_weight=$((100 - traffic_weight))
        
        log "🔄 Shifting traffic to $traffic_weight% new version"
        
        # Update VirtualService with new traffic split
        kubectl patch virtualservice claude-agents-routing -n "$NAMESPACE" --type='merge' -p="{
            \"spec\": {
                \"http\": [{
                    \"match\": [{
                        \"headers\": {
                            \"x-canary\": {
                                \"exact\": \"true\"
                            }
                        }
                    }],
                    \"route\": [{
                        \"destination\": {
                            \"host\": \"orchestrator\",
                            \"subset\": \"new\"
                        }
                    }]
                }, {
                    \"route\": [{
                        \"destination\": {
                            \"host\": \"orchestrator\",
                            \"subset\": \"stable\"
                        },
                        \"weight\": $stable_weight
                    }, {
                        \"destination\": {
                            \"host\": \"orchestrator\",
                            \"subset\": \"new\"
                        },
                        \"weight\": $traffic_weight
                    }],
                    \"timeout\": \"30s\",
                    \"retries\": {
                        \"attempts\": 3,
                        \"perTryTimeout\": \"10s\"
                    }
                }]
            }
        }"
        
        # Scale new deployment based on traffic
        local new_replicas=$(( (traffic_weight * 3) / 100 + 1 ))
        kubectl scale deployment orchestrator-new --replicas=$new_replicas -n "$NAMESPACE"
        
        # Monitor this traffic level
        if ! monitor_traffic_level "$traffic_weight" "$monitor_duration"; then
            log "❌ Traffic level $traffic_weight% failed health checks"
            execute_automated_rollback
            return 1
        fi
        
        log "✅ Traffic level $traffic_weight% is stable"
        
        # Run validation at key milestones
        if [[ "$traffic_weight" -eq 25 ]] || [[ "$traffic_weight" -eq 50 ]] || [[ "$traffic_weight" -eq 100 ]]; then
            run_production_validation "$traffic_weight"
        fi
    done
    
    log "🎉 Gradual rollout completed successfully!"
}

# Monitor traffic level with comprehensive health checks
monitor_traffic_level() {
    local traffic_weight=$1
    local duration=$2
    
    log "📊 Monitoring $traffic_weight% traffic for $duration seconds..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + duration))
    local check_interval=30
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check system health
        if ! check_system_health; then
            error "System health check failed at $traffic_weight% traffic"
        fi
        
        # Check error rates
        if ! check_error_rates; then
            error "Error rate check failed at $traffic_weight% traffic"
        fi
        
        # Check response times
        if ! check_response_times; then
            error "Response time check failed at $traffic_weight% traffic"
        fi
        
        # Check resource utilization
        if ! check_resource_utilization; then
            warning "High resource utilization at $traffic_weight% traffic"
        fi
        
        sleep $check_interval
    done
    
    return 0
}

# System health checks
check_system_health() {
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE" -l app=orchestrator --field-selector=status.phase=Running -o json | jq '.items | length')
    
    if [[ "$ready_pods" -lt 2 ]]; then
        log "❌ Insufficient ready pods: $ready_pods"
        return 1
    fi
    
    # Check service endpoints
    local endpoint_count
    endpoint_count=$(kubectl get endpoints orchestrator -n "$NAMESPACE" -o json | jq '.subsets[0].addresses | length')
    
    if [[ "$endpoint_count" -lt 2 ]]; then
        log "❌ Insufficient service endpoints: $endpoint_count"
        return 1
    fi
    
    return 0
}

# Error rate monitoring
check_error_rates() {
    local error_rate
    # Query Prometheus for error rate (simulated here)
    error_rate=$(kubectl exec -n "$NAMESPACE" deployment/orchestrator -- curl -s http://localhost:9090/metrics | \
        grep 'http_requests_total.*5[0-9][0-9]' | \
        awk '{sum+=$2} END {print sum}')
    
    local total_requests
    total_requests=$(kubectl exec -n "$NAMESPACE" deployment/orchestrator -- curl -s http://localhost:9090/metrics | \
        grep 'http_requests_total' | \
        awk '{sum+=$2} END {print sum}')
    
    if [[ "$total_requests" -gt 100 ]]; then
        local error_percentage
        error_percentage=$(echo "scale=4; $error_rate * 100 / $total_requests" | bc)
        
        if (( $(echo "$error_percentage > 5.0" | bc -l) )); then
            log "❌ Error rate too high: ${error_percentage}%"
            return 1
        fi
    fi
    
    return 0
}

# Response time monitoring
check_response_times() {
    local response_time
    response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:8080/health" 2>/dev/null || echo "999")
    
    if (( $(echo "$response_time > 2.0" | bc -l) )); then
        log "❌ Response time too high: ${response_time}s"
        return 1
    fi
    
    return 0
}

# Resource utilization monitoring
check_resource_utilization() {
    local cpu_usage
    cpu_usage=$(kubectl top pods -n "$NAMESPACE" --selector=app=orchestrator --no-headers | \
        awk '{sum+=$2} END {print sum}' | sed 's/m//')
    
    local memory_usage
    memory_usage=$(kubectl top pods -n "$NAMESPACE" --selector=app=orchestrator --no-headers | \
        awk '{sum+=$3} END {print sum}' | sed 's/Mi//')
    
    if [[ "$cpu_usage" -gt 1500 ]] || [[ "$memory_usage" -gt 3000 ]]; then
        log "⚠️ High resource usage - CPU: ${cpu_usage}m, Memory: ${memory_usage}Mi"
        return 1
    fi
    
    return 0
}

# Production validation at key milestones
run_production_validation() {
    local traffic_weight=$1
    
    log "🔍 Running production validation at $traffic_weight% traffic..."
    
    cd "$PROJECT_ROOT"
    
    # Run comprehensive validation
    if ! python3 rollout_validation.py --phase production --output-dir "validation_reports/prod_${traffic_weight}"; then
        error "Production validation failed at $traffic_weight%"
    fi
    
    # Run performance tests
    if ! python3 testing/test_runner.py --suite performance --environment production; then
        warning "Performance tests showed issues at $traffic_weight%"
    fi
    
    log "✅ Production validation passed at $traffic_weight%"
}

# Automated rollback procedure
execute_automated_rollback() {
    log "🚨 Executing automated rollback..."
    
    # Immediately shift all traffic back to stable
    kubectl patch virtualservice claude-agents-routing -n "$NAMESPACE" --type='merge' -p='{
        "spec": {
            "http": [{
                "route": [{
                    "destination": {
                        "host": "orchestrator",
                        "subset": "stable"
                    },
                    "weight": 100
                }]
            }]
        }
    }'
    
    # Scale down canary deployment
    kubectl scale deployment orchestrator-new --replicas=0 -n "$NAMESPACE"
    
    # Run rollback validation
    cd "$PROJECT_ROOT"
    python3 rollback/rollback_manager.py --execute --type partial
    
    log "🔄 Automated rollback completed"
}

# Final production cutover
execute_final_cutover() {
    log "🏁 Executing final production cutover..."
    
    # Replace stable deployment with new version
    kubectl patch deployment orchestrator -n "$NAMESPACE" -p "{
        \"spec\": {
            \"template\": {
                \"spec\": {
                    \"containers\": [{
                        \"name\": \"orchestrator\",
                        \"image\": \"claude-orchestrator:$VERSION\"
                    }]
                },
                \"metadata\": {
                    \"labels\": {
                        \"version\": \"stable\"
                    }
                }
            }
        }
    }"
    
    # Wait for rollout to complete
    kubectl rollout status deployment/orchestrator -n "$NAMESPACE" --timeout=600s
    
    # Remove canary deployment
    kubectl delete deployment orchestrator-new -n "$NAMESPACE"
    
    # Update VirtualService to route to stable only
    kubectl patch virtualservice claude-agents-routing -n "$NAMESPACE" --type='merge' -p='{
        "spec": {
            "http": [{
                "route": [{
                    "destination": {
                        "host": "orchestrator",
                        "subset": "stable"
                    },
                    "weight": 100
                }],
                "timeout": "30s",
                "retries": {
                    "attempts": 3,
                    "perTryTimeout": "10s"
                }
            }]
        }
    }'
    
    log "✅ Final cutover completed"
}

# Setup production monitoring and alerting
setup_production_monitoring() {
    log "📊 Setting up production monitoring and alerting..."
    
    # Create comprehensive ServiceMonitor
    cat > "$DEPLOYMENT_DIR/generated/production-monitoring.yaml" << EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: claude-agents-production
  namespace: $NAMESPACE
  labels:
    app: claude-agents
    environment: production
spec:
  selector:
    matchLabels:
      app: orchestrator
  endpoints:
  - port: metrics
    path: /metrics
    interval: 15s
    scrapeTimeout: 10s
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: claude-agents-production-alerts
  namespace: $NAMESPACE
  labels:
    app: claude-agents
    environment: production
spec:
  groups:
  - name: claude-agents-production
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{job="claude-agents",status=~"5.."}[5m]) > 0.05
      for: 2m
      labels:
        severity: critical
        environment: production
      annotations:
        summary: "High error rate in production"
        description: "Error rate is {{ \$value | humanizePercentage }}"
        
    - alert: HighLatency
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
      for: 5m
      labels:
        severity: warning
        environment: production
      annotations:
        summary: "High latency in production"
        description: "95th percentile latency is {{ \$value }}s"
        
    - alert: ServiceDown
      expr: up{job="claude-agents"} == 0
      for: 1m
      labels:
        severity: critical
        environment: production
      annotations:
        summary: "Service is down"
        description: "Claude Agents service is not responding"
        
    - alert: HighCPUUsage
      expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
      for: 10m
      labels:
        severity: warning
        environment: production
      annotations:
        summary: "High CPU usage"
        description: "CPU usage is above 80%"
        
    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: critical
        environment: production
      annotations:
        summary: "High memory usage"
        description: "Memory usage is above 90%"
EOF
    
    kubectl apply -f "$DEPLOYMENT_DIR/generated/production-monitoring.yaml"
    
    log "✅ Production monitoring configured"
}

# Show production deployment status
show_production_status() {
    log "📋 Production Deployment Status:"
    log "Namespace: $NAMESPACE"
    log "Version: $VERSION"
    log "Environment: $ENVIRONMENT"
    
    echo ""
    echo "Deployments:"
    kubectl get deployments -n "$NAMESPACE" -o wide
    
    echo ""
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    echo ""
    echo "Services:"
    kubectl get services -n "$NAMESPACE"
    
    echo ""
    echo "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    
    echo ""
    echo "Istio Configuration:"
    kubectl get gateway,virtualservice,destinationrule -n "$NAMESPACE"
    
    echo ""
    echo "Monitoring:"
    kubectl get servicemonitor,prometheusrule -n "$NAMESPACE"
    
    echo ""
    echo "Production Access:"
    echo "External URL: https://api.claude-agents.prod"
    echo "Internal Access: kubectl port-forward -n $NAMESPACE service/orchestrator 8080:8080"
    echo "Monitoring: kubectl port-forward -n $NAMESPACE service/grafana 3000:3000"
}

# Main execution
main() {
    log "🚀 Starting Phase 3: Gradual Production Rollout"
    log "==============================================="
    
    # Handle rollback command
    if [[ "${1:-}" == "rollback" ]]; then
        execute_automated_rollback
        exit 0
    fi
    
    # Validate production prerequisites
    validate_production_prerequisites
    
    # Setup production secrets
    setup_production_secrets
    
    # Deploy production infrastructure
    deploy_production_infrastructure
    
    # Setup traffic management
    setup_production_traffic_management
    
    # Deploy canary version
    deploy_canary_version
    
    # Setup production monitoring
    setup_production_monitoring
    
    # Execute gradual rollout
    execute_gradual_rollout
    
    # Execute final cutover
    execute_final_cutover
    
    # Show production status
    show_production_status
    
    log "🎉 Phase 3: Gradual Production Rollout completed successfully!"
    log "System is now running at 100% production traffic"
    log "Next step: Run Phase 4 Full Production optimization"
}

# Trap for cleanup
cleanup() {
    log "🧹 Cleaning up..."
    jobs -p | xargs -r kill 2>/dev/null || true
}

trap cleanup EXIT

# Run main function
main "$@"