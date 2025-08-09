---
name: architecture-review
description: Comprehensive architectural assessment coordinating multiple specialized agents to evaluate system design, identify structural issues, and provide strategic recommendations for scalable, maintainable, and robust software architecture.
---

# Architecture Review Command

## Overview

This command orchestrates a comprehensive architectural evaluation by deploying specialized agents to analyze system design from multiple perspectives. The review covers everything from high-level architectural patterns to implementation details, ensuring your system is well-positioned for current needs and future growth.

## Multi-Agent Orchestration Strategy

### **Phase 1: Strategic Architecture Analysis**
Deploy `the-critic` to evaluate:
- Overall architectural approach and pattern selection
- Technology stack appropriateness for requirements
- Architectural trade-offs and decision rationale
- Scalability and performance implications
- Risk assessment and mitigation strategies

### **Phase 2: Structural Assessment**
Engage `code-architect` to analyze:
- Code organization and module boundaries
- Design pattern implementation and consistency
- SOLID principles adherence
- Dependency management and coupling analysis
- Technical debt identification and prioritization

### **Phase 3: Security Architecture Review**
Deploy `security-audit-specialist` to examine:
- Security architecture patterns and implementation
- Authentication and authorization design
- Data flow security and encryption strategies
- Attack surface analysis and threat modeling
- Security controls integration and effectiveness

### **Phase 4: Infrastructure Architecture**
Use `devops-engineer` to assess:
- Deployment architecture and environments
- Infrastructure as Code (IaC) patterns
- Monitoring, logging, and observability design
- CI/CD pipeline architecture and security
- Disaster recovery and business continuity planning

### **Phase 5: Data Architecture Evaluation**
Deploy `data-engineer` to review:
- Data modeling and schema design
- Data flow architecture and processing patterns
- Storage solutions and data lifecycle management
- Analytics and reporting architecture
- Data governance and compliance considerations

### **Phase 6: Readability and Maintainability**
Engage `readability-expert` to evaluate:
- Code clarity and documentation architecture
- Naming conventions and architectural communication
- Onboarding complexity for new developers
- Knowledge management and architectural decision records
- Long-term maintainability of architectural choices

## Comprehensive Architecture Checklist

### **High-Level Architecture**
- [ ] Architecture aligns with business requirements and constraints
- [ ] Appropriate architectural patterns selected (microservices, modular monolith, etc.)
- [ ] Technology stack justification and modernization strategy
- [ ] Non-functional requirements addressed (performance, scalability, reliability)
- [ ] Cost optimization and operational efficiency considerations
- [ ] Future evolution and extensibility planning

### **System Design**
- [ ] Service boundaries and domain decomposition
- [ ] API design and contract management
- [ ] Data consistency and transaction management
- [ ] Error handling and fault tolerance strategies
- [ ] Configuration management and feature flags
- [ ] Versioning and backward compatibility strategy

### **Code Architecture**
- [ ] Package/module structure reflects domain boundaries
- [ ] Dependency injection and inversion of control patterns
- [ ] Separation of concerns and single responsibility principle
- [ ] Abstraction layers and interface design
- [ ] Code reuse strategies and shared libraries
- [ ] Testing architecture and testability design

### **Security Architecture**
- [ ] Authentication and authorization mechanisms
- [ ] Data encryption at rest and in transit
- [ ] Secure communication protocols and certificates
- [ ] Input validation and output encoding strategies
- [ ] Security monitoring and incident response integration
- [ ] Compliance requirements integration (GDPR, HIPAA, etc.)

### **Infrastructure Architecture**
- [ ] Environment strategy (dev, staging, production)
- [ ] Resource allocation and auto-scaling policies
- [ ] Load balancing and traffic management
- [ ] Backup and disaster recovery procedures
- [ ] Monitoring and alerting architecture
- [ ] Infrastructure security and access control

### **Data Architecture**
- [ ] Data storage solutions appropriate for use cases
- [ ] Data modeling and schema evolution strategies
- [ ] Data pipeline design and processing workflows
- [ ] Analytics and reporting infrastructure
- [ ] Data privacy and retention policies
- [ ] Data quality and validation mechanisms

## Architecture Quality Metrics

### **Structural Quality Indicators**
- **Coupling Metrics**: Low coupling between modules/services
- **Cohesion Metrics**: High cohesion within modules/services
- **Complexity Metrics**: Manageable cyclomatic and cognitive complexity
- **Dependency Metrics**: Minimal circular dependencies and clear dependency flow
- **Size Metrics**: Appropriate module/service sizing

### **Maintainability Indicators**
- **Code Duplication**: Minimal code duplication across components
- **Test Coverage**: Comprehensive test coverage across architectural layers
- **Documentation Coverage**: Adequate architectural documentation and decision records
- **Onboarding Time**: New developer productivity ramp-up metrics
- **Change Impact**: Low blast radius for typical changes

### **Operational Quality Indicators**
- **Deployment Frequency**: Ability to deploy frequently and safely
- **Lead Time**: Time from code commit to production deployment
- **Mean Time to Recovery**: Speed of incident resolution and system restoration
- **Change Failure Rate**: Percentage of deployments causing incidents
- **System Availability**: Uptime and reliability metrics

## Architecture Assessment Framework

### **Architecture Review Dimensions**

**1. Business Alignment**
- Requirements fulfillment and business value delivery
- Cost-effectiveness and resource utilization
- Time-to-market and development velocity impact
- Competitive advantage and differentiation support

**2. Technical Excellence**
- Code quality and engineering best practices
- Performance characteristics and scalability limits
- Security posture and risk management
- Operational simplicity and maintenance burden

**3. Team Dynamics**
- Conway's Law alignment (team structure matches architecture)
- Knowledge distribution and bus factor mitigation
- Development workflow efficiency and collaboration support
- Skill requirement alignment with team capabilities

**4. Future Readiness**
- Extensibility and adaptability for changing requirements
- Technology evolution and modernization pathway
- Scalability headroom and growth accommodation
- Integration capabilities and ecosystem compatibility

### **Risk Assessment Matrix**

**High Risk Areas:**
- Single points of failure in critical paths
- Technology choices with limited community support
- Complex inter-service dependencies
- Manual processes in critical workflows
- Security vulnerabilities or compliance gaps

**Medium Risk Areas:**
- Performance bottlenecks under load
- Moderate technical debt accumulation
- Limited monitoring and observability
- Manual scaling requirements
- Documentation gaps in complex areas

**Low Risk Areas:**
- Well-established patterns and practices
- Comprehensive test coverage and automation
- Clear ownership and responsibility boundaries
- Effective monitoring and alerting
- Regular maintenance and updates

## Deliverables

### **Architecture Assessment Report**
1. **Executive Summary**: Key findings, risk assessment, and strategic recommendations
2. **Current State Analysis**: Detailed evaluation of existing architecture
3. **Gap Analysis**: Identified issues and improvement opportunities
4. **Future State Recommendations**: Proposed architectural improvements
5. **Implementation Roadmap**: Phased approach to architectural evolution

### **Technical Architecture Documentation**
1. **System Architecture Diagram**: High-level system overview and component relationships
2. **Component Architecture**: Detailed component design and interfaces
3. **Data Flow Diagrams**: Information flow and processing patterns
4. **Infrastructure Architecture**: Deployment and operational architecture
5. **Security Architecture**: Security controls and data protection measures

### **Implementation Strategy**
1. **Quick Wins**: Low-effort, high-impact architectural improvements
2. **Strategic Initiatives**: Major architectural evolution projects
3. **Risk Mitigation Plan**: Addressing identified architectural risks
4. **Migration Strategy**: Approach for transitioning to improved architecture
5. **Success Metrics**: KPIs for measuring architectural improvement progress

## Architecture Evolution Patterns

### **Incremental Improvement Strategies**
- **Strangler Fig Pattern**: Gradually replacing legacy components
- **Branch by Abstraction**: Isolating changes behind abstractions
- **Parallel Run**: Running old and new systems simultaneously
- **Feature Toggles**: Controlled rollout of architectural changes
- **Database per Service**: Gradual data decoupling and service isolation

### **Modernization Approaches**
- **Lift and Shift**: Infrastructure modernization with minimal code changes
- **Re-platforming**: Moderate changes for cloud optimization
- **Re-architecting**: Significant structural changes for better scalability
- **Rebuilding**: Complete rewrite with modern architecture patterns
- **Hybrid Approach**: Combination of strategies based on component analysis

## Continuous Architecture Practices

### **Architecture Governance**
- Regular architecture review meetings and decision making
- Architecture decision records (ADRs) for significant choices
- Architecture fitness functions for automated validation
- Technology radar for evaluating new tools and patterns
- Architecture guild for knowledge sharing and standards

### **Evolution Monitoring**
- Architecture metrics tracking and trend analysis
- Technical debt monitoring and management
- Performance and reliability trend analysis
- Developer productivity and satisfaction metrics
- Business impact measurement of architectural changes

### **Knowledge Management**
- Architecture documentation maintenance and updates
- Developer onboarding and training programs
- Best practices documentation and enforcement
- Lessons learned capture and dissemination
- Cross-team knowledge sharing and collaboration

This architecture review command ensures comprehensive evaluation of your system architecture from multiple perspectives, providing actionable insights for building scalable, maintainable, and robust software systems that support both current needs and future growth.