---
name: performance-audit
description: Comprehensive performance review combining multiple specialized agents to identify bottlenecks, optimize resource usage, and improve system responsiveness across all layers of the application stack.
---

# Performance Audit Command

## Overview

This command orchestrates a comprehensive performance assessment by deploying multiple specialized agents to analyze different aspects of your application's performance characteristics. The audit covers everything from code-level optimizations to infrastructure scalability.

## Agent Orchestration Strategy

### **Phase 1: Systems Analysis**
Deploy `systems-engineer` to analyze:
- Memory allocation patterns and potential leaks
- CPU utilization and computational complexity
- Concurrency bottlenecks and race conditions  
- I/O operations and blocking calls
- Algorithm efficiency and data structure choices

### **Phase 2: Architecture Assessment**
Engage `code-architect` to evaluate:
- Architectural patterns impacting performance
- Database query patterns and N+1 problems
- API design efficiency and data transfer
- Caching strategies and cache hit rates
- Service boundaries and network overhead

### **Phase 3: Infrastructure Review**
Use `devops-engineer` to assess:
- Deployment configuration and resource limits
- Load balancing and auto-scaling configuration
- Database connection pooling and optimization
- CDN utilization and static asset delivery
- Monitoring and observability setup

### **Phase 4: Data Layer Optimization**
Deploy `data-engineer` to analyze:
- Database schema efficiency and indexing
- Query optimization and execution plans  
- Data pipeline performance and throughput
- Analytics query performance
- Data storage and retrieval patterns

### **Phase 5: Quality Validation**
Engage `qa-test-engineer` to verify:
- Performance testing strategies and coverage
- Load testing scenarios and realistic traffic patterns
- Performance regression testing in CI/CD
- Synthetic monitoring and alerting
- User experience performance metrics

## Comprehensive Performance Checklist

### **Code-Level Performance**
- [ ] Algorithmic complexity analysis (Big O evaluation)
- [ ] Memory allocation patterns and garbage collection impact
- [ ] Hot path identification and optimization
- [ ] Expensive operations in loops or frequent calls
- [ ] String concatenation and object creation efficiency
- [ ] Regular expression performance and caching
- [ ] File I/O operations and buffering strategies
- [ ] Network calls batching and async processing

### **Database Performance**
- [ ] Query execution plan analysis
- [ ] Index usage and effectiveness review
- [ ] Database connection pooling configuration
- [ ] Transaction isolation level optimization
- [ ] Database schema normalization vs denormalization
- [ ] Bulk operations vs individual queries
- [ ] Database statistics and maintenance routines
- [ ] Read replica utilization and data freshness

### **Frontend Performance**
- [ ] Bundle size analysis and code splitting
- [ ] Critical path rendering optimization
- [ ] Image optimization and lazy loading
- [ ] JavaScript execution performance
- [ ] CSS selector efficiency and paint triggers
- [ ] Service worker caching strategies
- [ ] Web font loading optimization
- [ ] Third-party script impact assessment

### **Infrastructure Performance**
- [ ] Server resource utilization (CPU, Memory, Disk, Network)
- [ ] Auto-scaling policies and thresholds
- [ ] Load balancer configuration and health checks
- [ ] CDN cache hit ratios and edge performance
- [ ] DNS resolution times and configuration
- [ ] SSL/TLS handshake optimization
- [ ] Container resource limits and requests
- [ ] Kubernetes resource management and scheduling

### **API Performance**
- [ ] Response time analysis across endpoints
- [ ] Payload size optimization (request/response)
- [ ] API rate limiting and throttling impact
- [ ] Authentication and authorization overhead
- [ ] Serialization/deserialization performance
- [ ] API versioning and backward compatibility overhead
- [ ] GraphQL query complexity and N+1 resolution
- [ ] REST API design efficiency and RESTfulness

## Performance Metrics and Benchmarks

### **Response Time Targets**
- **Critical User Actions**: <100ms (page interactions)
- **Page Load Time**: <2 seconds (complete page load)
- **API Response Time**: <200ms (95th percentile)
- **Database Query Time**: <50ms (average query)
- **Background Processing**: <5 minutes (batch operations)

### **Throughput Targets**  
- **Requests Per Second**: Define based on traffic patterns
- **Database Transactions**: Monitor peak and sustained rates
- **Message Processing**: Queue processing rates and backlog
- **Data Pipeline Throughput**: MB/s for data processing

### **Resource Utilization Targets**
- **CPU Utilization**: <70% average, <90% peak
- **Memory Usage**: <80% of available memory
- **Disk I/O**: Monitor queue depth and response times
- **Network Bandwidth**: Monitor peak usage vs capacity

## Deliverables

### **Performance Assessment Report**
1. **Executive Summary**: Key findings and impact prioritization
2. **Performance Bottlenecks**: Identified issues with severity ranking
3. **Optimization Recommendations**: Specific actions with effort estimates
4. **Performance Metrics Baseline**: Current state measurements
5. **Improvement Roadmap**: Phased approach to optimization

### **Technical Implementation Plan**
1. **Quick Wins**: Low-effort, high-impact optimizations
2. **Medium-term Improvements**: Architectural and infrastructure changes
3. **Long-term Optimizations**: Major refactoring and redesign efforts
4. **Testing Strategy**: Performance validation approach
5. **Monitoring Setup**: Ongoing performance tracking implementation

### **Performance Monitoring Setup**
1. **Key Metrics Dashboard**: Real-time performance indicators
2. **Alerting Configuration**: Proactive performance issue detection
3. **Performance Budgets**: Automated performance regression prevention
4. **Synthetic Monitoring**: Continuous user experience validation
5. **Regular Review Process**: Ongoing performance governance

## Common Performance Anti-Patterns

### **Code-Level Anti-Patterns**
- **Premature Optimization**: Optimizing without measuring first
- **Micro-Optimizations**: Focus on insignificant performance gains
- **Memory Leaks**: Unreleased resources and circular references
- **Blocking Operations**: Synchronous calls blocking main threads
- **Inefficient Algorithms**: Using inappropriate data structures or algorithms

### **Architecture Anti-Patterns**
- **Chatty Interfaces**: Too many small API calls instead of batch operations
- **God Services**: Monolithic services handling too many responsibilities
- **Database Per Service**: Excessive database connections and transactions
- **Synchronous Communication**: Blocking service-to-service communication
- **No Caching Strategy**: Missing or ineffective caching layers

### **Infrastructure Anti-Patterns**
- **Resource Over-Provisioning**: Wasteful resource allocation
- **Manual Scaling**: Lack of auto-scaling for traffic variations
- **Single Points of Failure**: No redundancy for critical components
- **Inefficient Load Distribution**: Poor load balancing configuration
- **Missing Monitoring**: Lack of visibility into system performance

## Integration with Development Workflow

### **Continuous Performance Testing**
- Integrate performance tests into CI/CD pipeline
- Set performance budgets that fail builds on regression
- Use synthetic monitoring for production performance tracking
- Implement chaos engineering for resilience testing

### **Regular Performance Reviews**
- Schedule quarterly comprehensive performance audits
- Monthly performance metrics review and trend analysis
- Weekly performance incident post-mortems and learning
- Daily performance monitoring and alerting response

### **Team Performance Culture**
- Establish performance champions within development teams
- Create performance guidelines and best practices documentation
- Provide performance testing tools and training
- Recognize and reward performance optimization contributions

This performance audit command ensures comprehensive coverage of all performance aspects while providing actionable insights for continuous improvement of system performance and user experience.