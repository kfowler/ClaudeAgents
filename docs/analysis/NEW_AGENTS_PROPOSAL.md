# New Agent Proposals 2025
## Sprint 14-15 Week 3-4: Detailed Agent Specifications

**Proposal Date**: October 6, 2025
**Analyst**: Product Strategist Agent
**Scope**: 10 new agent specifications with validation plans

---

## Table of Contents
1. [Infrastructure as Code Specialist](#1-infrastructure-as-code-specialist)
2. [Blockchain/Web3 Engineer](#2-blockchainweb3-engineer)
3. [Game Development Engineer](#3-game-development-engineer)
4. [Edge Computing Specialist](#4-edge-computing-specialist)
5. [Platform Engineering Specialist](#5-platform-engineering-specialist)
6. [Test Automation Engineer](#6-test-automation-engineer)
7. [Embedded Systems/IoT Developer](#7-embedded-systemsiot-developer)
8. [API Documentation Engineer](#8-api-documentation-engineer)
9. [GraphQL Specialist](#9-graphql-specialist)
10. [Developer Advocate](#10-developer-advocate)

---

## 1. Infrastructure as Code Specialist

### Agent Metadata
- **Agent Name**: `infrastructure-as-code-specialist`
- **Display Name**: Infrastructure as Code Specialist
- **Domain**: Infrastructure/DevOps
- **Model Assignment**: **Opus** (complex multi-cloud reasoning, critical infrastructure)
- **Priority**: **HIGH** (88/100 points)
- **Color**: `#7B68EE` (medium slate blue)

### Market Demand Evidence

**Quantitative Data**:
- IaC market growing from $0.8B (2022) to $2.3B (2027) - 24% CAGR
- Terraform specialists "in high demand globally" (2025 reports)
- Essential skill for DevOps roles alongside cloud providers
- Enterprises "doubling down on Terraform" as battle-tested solution

**Job Market Signals**:
- Terraform knowledge listed in 70%+ of DevOps job postings
- IaC experience required for cloud architecture roles
- Multi-cloud expertise premium (AWS + Azure + GCP)
- Infrastructure automation mandatory for modern organizations

**Technology Adoption**:
- Terraform leading IaC landscape due to agnostic nature
- HashiCorp ecosystem (Terraform, Vault, Consul) enterprise standard
- Pulumi growing as code-first alternative
- CloudFormation, ARM templates still relevant for cloud-specific

**Competitive Gap**:
- VoltAgent almost certainly has Terraform/IaC agent given market demand
- Our devops-engineer has IaC skills but not specialized depth
- Opportunity: Position as multi-cloud IaC expert vs single-cloud focus

### Use Cases (20+ specific tasks)

**Terraform Core**:
1. Initialize new Terraform project with best-practice structure
2. Design reusable Terraform modules for common infrastructure patterns
3. Implement Terraform state management (S3 backend, state locking)
4. Create multi-environment infrastructure (dev/staging/prod)
5. Write Terraform for AWS (EC2, RDS, VPC, Lambda, S3, CloudFront)
6. Write Terraform for Azure (VM, AKS, Storage, Functions)
7. Write Terraform for GCP (Compute Engine, GKE, Cloud Storage)
8. Implement Terraform workspaces for environment separation
9. Debug Terraform plan/apply errors and state inconsistencies
10. Migrate existing infrastructure to Terraform (import resources)

**Advanced IaC**:
11. Implement Terraform remote module registry
12. Create Terratest tests for infrastructure validation
13. Set up Terraform Cloud/Enterprise with CI/CD integration
14. Design policy as code with Sentinel or OPA
15. Implement drift detection and remediation strategies
16. Create Terraform provider configurations and authentication
17. Optimize Terraform performance for large infrastructures
18. Implement secrets management with HashiCorp Vault integration

**Multi-Tool IaC**:
19. Design Pulumi infrastructure with TypeScript/Python
20. Create CloudFormation templates for AWS-native deployments
21. Write Ansible playbooks for configuration management
22. Implement hybrid IaC strategy (Terraform + Ansible)
23. Compare IaC tools for specific use cases (Terraform vs Pulumi vs CloudFormation)
24. Migrate between IaC tools (CloudFormation → Terraform)

**DevOps Integration**:
25. Integrate Terraform with GitHub Actions CI/CD
26. Set up GitLab CI pipelines for Terraform automation
27. Implement infrastructure testing in CI/CD pipelines
28. Create infrastructure documentation from Terraform code
29. Design disaster recovery infrastructure with IaC
30. Implement blue-green infrastructure deployments

### Validation Plan (5 real tasks)

**Test 1: AWS Multi-Tier Infrastructure**
- Task: Deploy 3-tier web application infrastructure to AWS
- Components: VPC, subnets, ALB, Auto Scaling Group, RDS, S3, CloudFront
- Validation: Infrastructure deploys successfully, terraform plan shows no changes
- Success Criteria: All resources created, properly tagged, security groups configured

**Test 2: Terraform Module Development**
- Task: Create reusable Terraform module for Kubernetes cluster (EKS/AKS/GKE)
- Requirements: Multi-cloud support, input variables, outputs, documentation
- Validation: Module works across AWS EKS, Azure AKS, and GCP GKE
- Success Criteria: Module published, tested, follows best practices

**Test 3: State Management & Import**
- Task: Import existing manually-created AWS resources into Terraform
- Scenario: 10+ resources (EC2, security groups, S3 buckets) to import
- Validation: Resources imported without destruction, state clean
- Success Criteria: terraform plan shows no changes after import

**Test 4: Multi-Environment Strategy**
- Task: Design and implement dev/staging/prod environments with Terraform
- Requirements: Workspace or directory strategy, variable management, backend config
- Validation: Can deploy to all 3 environments independently
- Success Criteria: No resource conflicts, proper environment isolation

**Test 5: CI/CD Integration**
- Task: Set up GitHub Actions workflow for Terraform automation
- Requirements: terraform plan on PR, terraform apply on merge, state locking
- Validation: Pipeline runs successfully, provides plan output as PR comment
- Success Criteria: Automated deployment with approval gates

### Differentiation from Competitors

**Our Advantages**:
1. **Multi-Cloud Expertise**: AWS + Azure + GCP in one agent (vs cloud-specific)
2. **Best Practices Built-In**: Module design, state management, security patterns
3. **Testing Focus**: Terratest integration, policy as code, drift detection
4. **DevOps Integration**: CI/CD pipelines, GitOps workflows, automation
5. **Real-World Scenarios**: Migration strategies, import workflows, troubleshooting

**vs devops-engineer (our existing agent)**:
- Deeper IaC-specific knowledge (modules, state, providers)
- More Terraform ecosystem tools (Cloud, Vault, Sentinel)
- Multi-cloud IaC patterns vs general cloud deployment
- Infrastructure testing and validation expertise

**vs VoltAgent (hypothetical IaC agent)**:
- Validation framework ensures working code
- Professional manifesto = practical, tested patterns
- Integration with our other agents (security-audit, cloud-architect)

### Professional Manifesto Alignment

**Truth Over Theater**:
- Provide working Terraform code, not conceptual examples
- Real state management strategies that handle edge cases
- Honest trade-offs between IaC tools (Terraform vs Pulumi vs CloudFormation)

**Reality-First Strategy**:
- Address real-world scenarios: state drift, import challenges, provider limitations
- Acknowledge cloud provider differences and gotchas
- Plan for disaster recovery and infrastructure testing

**Demonstrable Infrastructure Validation**:
- All infrastructure code tested with terraform plan/apply
- CI/CD integration validated in real pipelines
- Module reusability proven across multiple projects

**Strategic Accountability**:
- Honest assessment of when NOT to use IaC
- Clear guidance on state management risks
- Cost implications of infrastructure choices

### Technical Expertise Areas

**Core IaC Tools**:
- Terraform (primary): HCL, providers, modules, state, workspaces
- Pulumi: TypeScript, Python, Go for infrastructure
- CloudFormation: AWS-native IaC
- ARM Templates: Azure Resource Manager
- Ansible: Configuration management, hybrid with Terraform

**Cloud Platforms**:
- AWS: 100+ services, IaC patterns, best practices
- Azure: Resource groups, ARM, Bicep, IaC conventions
- GCP: Projects, IaC patterns, Deployment Manager
- Multi-cloud: Abstraction patterns, provider selection

**DevOps Integration**:
- CI/CD: GitHub Actions, GitLab CI, Jenkins, CircleCI
- State backends: S3, Azure Storage, GCS, Terraform Cloud
- Secrets: Vault, AWS Secrets Manager, Azure Key Vault
- Testing: Terratest, Kitchen-Terraform, policy testing

**Advanced Patterns**:
- Module design: Input variables, outputs, composition
- State management: Remote backends, locking, workspaces
- Policy as code: Sentinel, OPA, compliance automation
- Drift detection: Terraform refresh, automated reconciliation

### Model Assignment Justification: Opus

**Why Opus**:
1. **Complex Reasoning**: Multi-cloud infrastructure requires understanding provider differences
2. **Critical Systems**: Infrastructure errors can cause outages, data loss
3. **State Management**: Terraform state complexity requires careful reasoning
4. **Security Implications**: IAM, networking, encryption decisions critical
5. **Cost Impact**: Infrastructure choices have major cost implications
6. **Multi-Service Coordination**: Understanding service dependencies across clouds

**Cost/Value Trade-off**:
- Higher cost justified by infrastructure criticality
- Errors expensive (resource cleanup, downtime, security breaches)
- Complex troubleshooting requires deep reasoning
- Enterprise use case = higher value per interaction

### Agent Persona

Infrastructure as Code Specialist is a seasoned infrastructure engineer who speaks the language of automation, immutability, and reproducibility. They've lived through the pain of manual infrastructure provisioning, ClickOps, and configuration drift. Now they champion infrastructure as code with the wisdom of hard-won experience.

They understand that IaC is more than just Terraform syntax—it's about designing repeatable, testable, versioned infrastructure that survives team turnover and scales with organizational growth. They know when to modularize, when to monorepo, and when to split infrastructure across multiple state files.

They're pragmatic: they know Terraform isn't perfect, state files can be tricky, and provider APIs change. They've debugged enough cryptic Terraform errors to know the common pitfalls and how to avoid them. They advocate for testing, CI/CD integration, and policy as code—not because it's trendy, but because it prevents 2 AM production incidents.

---

## 2. Blockchain/Web3 Engineer

### Agent Metadata
- **Agent Name**: `blockchain-web3-engineer`
- **Display Name**: Blockchain/Web3 Engineer
- **Domain**: Web3/Blockchain Development
- **Model Assignment**: **Opus** (smart contract security critical)
- **Priority**: **HIGH** (85/100 points)
- **Color**: `#FFD700` (gold - representing crypto/value)

### Market Demand Evidence

**Quantitative Data**:
- Web3 job market projected to reach $94B by 2025 (66.2% CAGR)
- 30% job growth projected for 2025 in Web3 sector
- 460,000+ professionals in Web3, +100,000 added in past year
- 29,000+ companies operating in blockchain/cryptocurrency sectors
- Smart contract developers earning $160k average salary
- Blockchain developers $135k-$200k salary range

**Job Market Signals**:
- 150k+ blockchain developer job postings (LinkedIn 2025)
- Solidity proficiency in high demand (supply < demand)
- Rust for smart contracts (Solana, NEAR) growing rapidly
- Web3 skills command significant salary premiums
- Both technical and non-technical Web3 roles expanding

**Technology Adoption**:
- Solidity: 15k GitHub stars, trending
- DeFi total value locked (TVL) billions of dollars
- NFT marketplace volume indicating ongoing demand
- DAO governance systems proliferating
- Ethereum, Solana, Polygon, Avalanche active ecosystems

**Competitive Gap**:
- **CRITICAL**: VoltAgent almost certainly has blockchain/Web3 agent
- We have ZERO blockchain coverage (major competitive weakness)
- Web3 projects can't use ClaudeAgents currently
- Missing out on fast-growing, high-salary market segment

### Use Cases (25+ specific tasks)

**Smart Contract Development**:
1. Create ERC-20 token contract with OpenZeppelin
2. Develop ERC-721 NFT contract with metadata support
3. Build ERC-1155 multi-token contract
4. Implement upgradeable smart contracts (proxy patterns)
5. Create DAO governance contract with voting mechanisms
6. Build DeFi lending protocol (like Aave/Compound)
7. Implement automated market maker (AMM) like Uniswap
8. Create staking contract with reward distribution
9. Build crowdfunding contract with refund logic
10. Implement multi-signature wallet contract

**Web3 Frontend Integration**:
11. Build React dApp with Web3.js or Ethers.js
12. Implement wallet connection (MetaMask, WalletConnect)
13. Create NFT minting interface
14. Build DeFi dashboard with real-time data
15. Implement transaction signing and gas estimation
16. Create Web3 authentication flow
17. Build blockchain explorer interface
18. Implement ENS (Ethereum Name Service) resolution

**Smart Contract Security**:
19. Audit smart contract for common vulnerabilities
20. Implement reentrancy guards and security patterns
21. Conduct gas optimization analysis
22. Test smart contracts with Hardhat/Foundry
23. Perform static analysis with Slither/Mythril
24. Write comprehensive test suites for contracts
25. Implement access control and permission systems

**Blockchain Operations**:
26. Deploy contracts to Ethereum mainnet/testnet
27. Verify contracts on Etherscan/block explorers
28. Set up Hardhat development environment
29. Create deployment scripts with upgrades
30. Implement subgraph for The Graph protocol
31. Set up IPFS for decentralized storage
32. Create blockchain indexer for event data

**Multi-Chain Development**:
33. Port Solidity contracts to Solana (Rust)
34. Build cross-chain bridge logic
35. Implement Layer 2 solutions (Polygon, Optimism, Arbitrum)
36. Create multi-chain dApp with unified interface

### Validation Plan (5 real tasks)

**Test 1: ERC-20 Token Deployment**
- Task: Create and deploy ERC-20 token to Ethereum testnet (Sepolia)
- Requirements: OpenZeppelin, Hardhat, deployment script, verified contract
- Validation: Contract deployed, verified on Etherscan, transfer functionality works
- Success Criteria: Token visible in MetaMask, transfers succeed, gas-optimized

**Test 2: NFT Marketplace**
- Task: Build simple NFT minting dApp with React frontend
- Components: ERC-721 contract, minting interface, wallet connection, IPFS metadata
- Validation: Users can connect wallet, mint NFT, view in OpenSea
- Success Criteria: End-to-end minting flow works on testnet

**Test 3: Smart Contract Security Audit**
- Task: Audit provided sample contract for vulnerabilities
- Focus: Reentrancy, access control, integer overflow, gas optimization
- Validation: Identify all intentionally-placed vulnerabilities (5+)
- Success Criteria: Report with findings, severity ratings, remediation code

**Test 4: DeFi Staking Contract**
- Task: Implement ERC-20 staking contract with reward distribution
- Requirements: Deposit, withdraw, claim rewards, time-based calculations
- Validation: Comprehensive test suite (Hardhat), 100% coverage, deployment
- Success Criteria: Math correct, no vulnerabilities, gas-optimized

**Test 5: Multi-Chain dApp**
- Task: Deploy same contract to Ethereum and Polygon with unified frontend
- Requirements: Contract works on both chains, frontend detects network
- Validation: Transactions work on both networks, proper chain switching
- Success Criteria: Seamless multi-chain experience

### Differentiation from Competitors

**Our Advantages**:
1. **Security-First Approach**: Audit integration, vulnerability scanning, best practices
2. **Multi-Chain Expertise**: Ethereum, Solana, Polygon, Layer 2 solutions
3. **Full-Stack Web3**: Smart contracts + frontend integration + deployment
4. **Testnet-First Development**: Safe testing before mainnet deployment
5. **Gas Optimization**: Cost-conscious contract design

**vs No Current Agent**:
- This is entirely new domain for ClaudeAgents
- Opens door to Web3 projects and developers
- Addresses critical competitive gap vs VoltAgent

**vs VoltAgent (hypothetical Web3 agent)**:
- Security audit integration (works with security-audit-specialist)
- Validation on real testnets (proven working code)
- Multi-chain coverage (not just Ethereum-focused)
- Professional manifesto = realistic security assessments

### Professional Manifesto Alignment

**Truth Over Theater**:
- Honest about smart contract security risks and limitations
- Real gas cost analysis, not theoretical estimates
- Acknowledge blockchain trilemma trade-offs (decentralization, security, scalability)

**Reality-First Strategy**:
- Testnet-first approach (never deploy untested code to mainnet)
- Security audit mandatory for production contracts
- Clear warnings about immutability and upgrade patterns

**Demonstrable Security Validation**:
- All contracts tested with comprehensive test suites
- Static analysis with industry-standard tools (Slither, Mythril)
- Gas optimization proven with benchmark comparisons

**Strategic Accountability**:
- Transparent about when NOT to use blockchain
- Clear guidance on custody, key management risks
- Honest assessment of blockchain suitability for use case

### Technical Expertise Areas

**Smart Contract Languages**:
- Solidity (primary): EVM, gas optimization, security patterns
- Vyth on: Pythonic smart contract language
- Rust: Solana, NEAR, Polkadot smart contracts
- Move: Aptos, Sui (emerging)

**Development Tools**:
- Hardhat: Testing, deployment, network management
- Foundry: Fast Solidity testing framework
- Truffle: Classic development suite
- Remix: Browser-based IDE for quick prototyping

**Security Tools**:
- Slither: Static analysis for Solidity
- Mythril: Security analysis tool
- Echidna: Fuzzing tool for smart contracts
- MythX: Comprehensive security analysis service

**Web3 Libraries**:
- Ethers.js: Ethereum interaction (modern)
- Web3.js: Ethereum interaction (classic)
- Wagmi: React hooks for Ethereum
- RainbowKit: Wallet connection UI

**Blockchain Platforms**:
- Ethereum: Mainnet, testnets (Sepolia, Goerli)
- Layer 2: Polygon, Optimism, Arbitrum, zkSync
- Alternative L1s: Solana, Avalanche, NEAR, Cosmos
- Specialized: Flow (NFTs), Algorand, Tezos

**Standards & Protocols**:
- ERCs: ERC-20, ERC-721, ERC-1155, ERC-4626
- DeFi: Uniswap V2/V3, Aave, Compound, Curve protocols
- NFTs: Metadata standards, royalties (ERC-2981)
- Governance: DAO patterns, voting mechanisms

### Model Assignment Justification: Opus

**Why Opus**:
1. **Security Critical**: Smart contract bugs can lose millions of dollars
2. **Immutability**: Deployed contracts can't be easily fixed
3. **Complex Security Analysis**: Requires deep reasoning about attack vectors
4. **Gas Optimization**: Trade-offs between security, functionality, cost
5. **Multi-Contract Interactions**: Understanding complex DeFi protocol composability
6. **Cryptographic Reasoning**: Understanding cryptographic primitives

**Cost/Value Trade-off**:
- Highest cost model justified by security criticality
- Contract vulnerabilities have lost billions (DAO hack, bridge hacks)
- Formal verification and audit-level analysis require deep reasoning
- Enterprise/DeFi use case = extremely high value per interaction

### Agent Persona

Blockchain/Web3 Engineer is a security-obsessed developer who's seen too many bridge hacks and reentrancy attacks to ever take smart contract security lightly. They came from traditional software engineering but were drawn to blockchain's promise of trustless, transparent systems.

They live by the mantra: "Code is law, and law is immutable." They know that every line of Solidity code is potentially a million-dollar bug. They triple-check math, audit access controls, and never skip writing tests. They've read the Ethereum Yellow Paper, understand the EVM's quirks, and can explain why SLOAD is expensive.

They're pragmatic about blockchain limitations: they know it's not a database replacement, that gas costs matter, and that most "blockchain" projects don't actually need blockchain. But when the use case fits—trustless finance, verifiable scarcity, composable protocols—they're the expert who can build it securely.

They advocate for testnet-first development, comprehensive test coverage, security audits, and gas optimization. They're fluent in both Solidity security patterns and Web3 frontend integration. They can explain technical concepts to non-technical stakeholders without losing precision.

---

## 3. Game Development Engineer

### Agent Metadata
- **Agent Name**: `game-development-engineer`
- **Display Name**: Game Development Engineer
- **Domain**: Game Development
- **Model Assignment**: **Sonnet** (moderate complexity, creative + technical)
- **Priority**: **HIGH** (82/100 points)
- **Color**: `#FF6B6B` (coral red - representing gaming/creativity)

### Market Demand Evidence

**Quantitative Data**:
- Unity market share: 25.79% with 13,764 customers
- Unreal Engine market share: 16.54% with 8,825 customers
- Talent gap: Shortage of experienced game developers despite industry layoffs
- Workforce: Tens of thousands of developers in both Unity/Unreal ecosystems
- Beyond gaming: AR/VR, simulation, automotive, architecture, metaverse expansion

**Job Market Signals**:
- High demand for seasoned game developers (industry reports)
- Unity specialists needed for indie/practical teams
- Unreal Engine required for AAA studios (industry standard)
- Cross-industry demand: Entertainment, training, visualization, education

**Technology Adoption**:
- Unity: C# development, 2D/3D games, mobile dominance
- Unreal Engine: C++, high-fidelity graphics, AAA games, film/TV production
- Godot: Open-source alternative gaining traction
- Game engines used beyond gaming (digital twins, architectural viz, training sims)

**Competitive Gap**:
- We have 3d-modeler (assets) but NO game logic/engine specialist
- Game development common request (tutorials, prototypes, indie games)
- VoltAgent likely has game development agent
- Adjacent creative agents (digital-artist, video-director) but missing core game dev

### Use Cases (25+ specific tasks)

**Unity Development (C#)**:
1. Create 2D platformer game with Unity
2. Build 3D first-person shooter prototype
3. Implement character controller with physics
4. Create game UI with Unity UI system
5. Implement save/load system with PlayerPrefs or JSON
6. Build inventory system with drag-and-drop
7. Create enemy AI with NavMesh navigation
8. Implement combat system with health/damage
9. Build procedural level generation
10. Create particle effects and visual polish
11. Implement audio system with sound effects and music
12. Build mobile game with touch controls
13. Create multiplayer game with Unity Netcode/Photon
14. Implement achievement system and player progression

**Unreal Engine Development (C++/Blueprints)**:
15. Create third-person action game with Unreal
16. Build first-person game with Unreal's FPS template
17. Implement advanced character movement (parkour, climbing)
18. Create realistic lighting and post-processing
19. Build enemy AI with Behavior Trees
20. Implement damage system with Unreal's GameplayAbilities
21. Create cinematics with Sequencer
22. Build realistic physics interactions
23. Implement ray tracing and advanced graphics
24. Create VR experience with Unreal

**Cross-Platform & Publishing**:
25. Build and deploy game to Steam
26. Create mobile game build (iOS/Android)
27. Implement WebGL build for browser games
28. Set up continuous integration for game builds
29. Optimize game performance (FPS, memory, draw calls)
30. Create game trailer and promotional materials

**Game Design Integration**:
31. Implement game design document as playable prototype
32. Balance game mechanics and difficulty curves
33. Create tutorial level and onboarding flow
34. Implement analytics and player behavior tracking
35. Design level layouts and game pacing

### Validation Plan (5 real tasks)

**Test 1: Unity 2D Platformer**
- Task: Create simple 2D platformer with player movement, enemies, collectibles
- Requirements: Character controller, collision detection, score system, win condition
- Validation: Playable game build runs on macOS/Windows
- Success Criteria: Smooth controls, no major bugs, basic gameplay loop complete

**Test 2: Unity 3D Prototype**
- Task: Build 3D game prototype (FPS or third-person) with combat
- Requirements: Character movement, camera controls, shooting/combat, enemy AI
- Validation: Compiled build playable, performance acceptable (60+ FPS)
- Success Criteria: Core gameplay loop functional, polished controls

**Test 3: Unreal Engine Scene**
- Task: Create high-fidelity 3D scene with lighting and post-processing
- Requirements: Realistic lighting, materials, post-processing, interactivity
- Validation: Scene runs in Unreal Engine 5, showcases visual quality
- Success Criteria: AAA-quality visuals, smooth performance

**Test 4: Game Mechanics Implementation**
- Task: Implement inventory system with UI for Unity or Unreal
- Requirements: Drag-and-drop, item stacking, equipment slots, persistence
- Validation: UI functional, items persist across sessions
- Success Criteria: Professional UI, bug-free interactions

**Test 5: Mobile Game Build**
- Task: Create and build simple mobile game for iOS or Android
- Requirements: Touch controls, mobile-optimized performance, build/export
- Validation: Game installs and runs on real device
- Success Criteria: Playable on mobile, appropriate performance

### Differentiation from Competitors

**Our Advantages**:
1. **Dual Engine Expertise**: Unity AND Unreal Engine (not single-engine focused)
2. **Full Game Loop**: From prototype to build/deployment
3. **Performance Focus**: Optimization, profiling, platform-specific tuning
4. **Production Ready**: Not just tutorials, but polished, deployable games
5. **Integration with Assets**: Works with 3d-modeler, digital-artist, audio-engineer

**vs 3d-modeler (our existing agent)**:
- Game logic, scripting, mechanics (not just asset creation)
- Engine-specific knowledge (Unity C#, Unreal C++/Blueprints)
- Gameplay systems (AI, physics, UI, save systems)
- Build and deployment processes

**vs VoltAgent (hypothetical game dev agent)**:
- Validated with real playable builds
- Multi-engine coverage (Unity + Unreal)
- Integration with other creative agents in ecosystem
- Performance optimization and production quality focus

### Professional Manifesto Alignment

**Truth Over Theater**:
- Playable builds, not just code snippets
- Realistic scope for indie development vs AAA
- Honest about game development time requirements

**Reality-First Strategy**:
- Performance considerations from the start
- Platform limitations acknowledged (mobile vs PC)
- Asset pipeline integration with tools and workflows

**Demonstrable Game Validation**:
- All games built and tested as playable
- Performance profiled on target platforms
- User testing feedback incorporated

**Strategic Accountability**:
- Honest about game complexity and team requirements
- Clear guidance on Unity vs Unreal for specific projects
- Scope management (MVP vs full game)

### Technical Expertise Areas

**Unity Engine**:
- C# scripting and .NET ecosystem
- Unity Editor workflows and tools
- Physics2D and Physics3D systems
- Animation system (Animator, Animation Events)
- Unity UI and UI Toolkit
- Particle systems and VFX Graph
- Audio system (AudioSource, AudioMixer)
- NavMesh and AI navigation
- Unity Services (Analytics, Ads, Cloud Save)
- Unity Netcode for multiplayer
- AssetBundles and addressables
- Build pipeline and player settings

**Unreal Engine**:
- C++ and Blueprints (visual scripting)
- Unreal Editor workflows
- Materials and shaders
- Niagara VFX system
- Behavior Trees for AI
- Gameplay Ability System
- Sequencer for cinematics
- Landscape and World Composition
- Networking and replication
- Blueprint communication patterns
- Performance profiling tools
- Packaging and deployment

**Game Programming Patterns**:
- Entity Component System (ECS)
- State machines for AI and game flow
- Object pooling for performance
- Observer pattern for events
- Command pattern for input
- Singleton and service locator patterns
- Model-View-Controller for UI

**Cross-Platform Development**:
- PC (Windows, macOS, Linux) builds
- Mobile (iOS, Android) optimization
- Console considerations (PlayStation, Xbox, Switch)
- WebGL for browser games
- VR/AR platforms (Quest, HoloLens, ARKit)

**Game Design Principles**:
- Core gameplay loops and mechanics
- Player progression and retention
- Difficulty curves and balancing
- Level design and pacing
- UI/UX for games
- Monetization strategies (F2P, premium, IAP)
- Analytics and player behavior

### Model Assignment Justification: Sonnet

**Why Sonnet**:
1. **Moderate Complexity**: Game logic challenging but not security-critical
2. **Creative + Technical**: Balance of artistic and engineering skills
3. **Iterative Development**: Games refined through iteration, not one-shot critical
4. **Cost-Conscious**: Indie developers price-sensitive, Sonnet good value
5. **Adequate Reasoning**: Complex enough for game systems, not requiring Opus depth

**Cost/Value Trade-off**:
- Sonnet provides excellent game development capability
- Game prototyping benefits from fast iterations
- Target audience (indie devs, hobbyists) cost-sensitive
- Opus overkill for game logic vs Haiku insufficient for complexity

### Agent Persona

Game Development Engineer is a passionate game creator who's shipped both indie passion projects and worked on larger studio productions. They understand games are equal parts engineering, art, and design—and they excel at all three.

They've experienced the full spectrum: the joy of seeing players enjoy their creation, the frustration of last-minute bugs before launch, and the satisfaction of optimizing that one system that was tanking framerate. They know Unity's Inspector and Unreal's Blueprint editor like the back of their hand.

They're pragmatic about scope: they know the difference between a game jam prototype, an indie MVP, and an AAA production. They advocate for starting simple, iterating quickly, and testing with real players early. They understand performance matters—nobody enjoys a laggy game—and they profile religiously.

They speak both languages: they can discuss gameplay feel with designers and frame timing with engineers. They know when to use Unity for rapid prototyping and when Unreal's visual fidelity is worth the complexity. They've learned that good games come from iteration, playtesting, and polish—not just following tutorials.

---

## 4. Edge Computing Specialist

### Agent Metadata
- **Agent Name**: `edge-computing-specialist`
- **Display Name**: Edge Computing Specialist
- **Domain**: Cloud/Edge Computing
- **Model Assignment**: **Sonnet** (modern patterns, reasonable complexity)
- **Priority**: **HIGH** (81/100 points)
- **Color**: `#00CED1` (dark turquoise - representing distributed/edge)

### Market Demand Evidence

**Quantitative Data**:
- Cloudflare Workers: 3 million developers (2024), 50% YoY growth
- Coverage: 330+ cities, 122+ countries, <50ms to 95% of internet users
- Performance: V8 isolates enable <5ms cold starts
- Framework support: Production-ready for React Router v7, Astro, Hono, Vue.js, Nuxt, SvelteKit
- Node.js compatibility: Enhanced CommonJS/ES Modules support (2025)

**Job Market Signals**:
- Edge computing skills increasingly required for cloud roles
- Serverless/edge experience differentiates candidates
- Global latency optimization valued for international applications
- Cost optimization through edge computing attractive to enterprises

**Technology Adoption**:
- Cloudflare Workers leading edge platform
- Deno Deploy: Edge-first JavaScript/TypeScript runtime
- Vercel Edge Functions: Integrated with Vercel platform
- AWS Lambda@Edge, CloudFront Functions: AWS edge offerings
- Fastly Compute@Edge: WebAssembly-based edge platform

**Competitive Gap**:
- cloud-architect covers cloud but not edge-specific patterns
- devops-engineer has deployment but not edge optimization
- Emerging category: Early mover advantage vs VoltAgent
- Modern architecture pattern becoming standard

### Use Cases (20+ specific tasks)

**Cloudflare Workers**:
1. Deploy API endpoint to Cloudflare Workers
2. Implement Workers KV for edge state storage
3. Create Durable Objects for stateful applications
4. Build edge middleware for authentication/authorization
5. Implement request routing and A/B testing at edge
6. Create image optimization worker (automatic resizing/format)
7. Build edge-side rendering for dynamic content
8. Implement rate limiting and DDoS protection
9. Create geolocation-based content delivery
10. Build API gateway at the edge

**Deno Deploy**:
11. Deploy Deno Fresh application to edge
12. Create RESTful API with Deno Deploy
13. Implement edge middleware with Deno
14. Build real-time application with WebSockets
15. Create scheduled tasks (cron jobs) at edge

**Edge Optimization Patterns**:
16. Implement edge caching strategies (CDN + Workers)
17. Design global latency optimization architecture
18. Create edge-side personalization
19. Build progressive enhancement with edge compute
20. Implement edge analytics and logging

**Framework Integration**:
21. Deploy Next.js app to edge runtime
22. Create Remix app with edge deployment
23. Build SvelteKit app with edge functions
24. Deploy Astro site with edge rendering
25. Create Nuxt application with edge middleware

**WebAssembly at Edge**:
26. Compile Rust to WASM for edge execution
27. Create high-performance edge function with WASM
28. Implement custom logic in multiple languages via WASM

### Validation Plan (5 real tasks)

**Test 1: Cloudflare Workers API**
- Task: Deploy RESTful API to Cloudflare Workers with multiple endpoints
- Requirements: GET/POST/PUT/DELETE, error handling, CORS, authentication
- Validation: API accessible globally, <50ms response time from major regions
- Success Criteria: Production deployment, performance validated, proper security

**Test 2: Workers KV Storage**
- Task: Build edge application with Workers KV for state management
- Requirements: Read/write operations, TTL, global replication
- Validation: Data persists across requests, accessible from multiple regions
- Success Criteria: Low-latency reads, proper error handling

**Test 3: Deno Deploy Application**
- Task: Create and deploy Deno Fresh application to edge
- Requirements: Server-side rendering, API routes, deployment pipeline
- Validation: App loads quickly from multiple geographic locations
- Success Criteria: <100ms TTFB, proper SSR, production-ready

**Test 4: Edge Caching Strategy**
- Task: Implement multi-tier caching (CDN + edge compute + origin)
- Requirements: Cache headers, purge strategies, stale-while-revalidate
- Validation: Cache hit rates >80%, proper invalidation
- Success Criteria: Measurable performance improvement, cost reduction

**Test 5: Framework Edge Deployment**
- Task: Deploy Next.js or Remix app to edge with edge middleware
- Requirements: Edge functions, authentication, personalization
- Validation: App runs on edge runtime, not serverless functions
- Success Criteria: Cold start <5ms, global deployment, proper functionality

### Differentiation from Competitors

**Our Advantages**:
1. **Multi-Platform Edge**: Cloudflare Workers, Deno Deploy, Vercel Edge
2. **Performance Focus**: Latency optimization, cold start minimization
3. **Framework Integration**: Modern meta-frameworks (Next, Remix, SvelteKit)
4. **Cost Optimization**: Edge vs serverless vs origin trade-offs
5. **Global Deployment**: Multi-region validation and testing

**vs cloud-architect (our existing agent)**:
- Edge-specific patterns and constraints
- V8 isolates vs containers/VMs understanding
- Edge caching and distribution strategies
- Platform-specific edge APIs (Workers KV, Durable Objects)

**vs VoltAgent (potential edge agent)**:
- Validated on real edge platforms
- Performance benchmarking across platforms
- Integration with existing cloud-architect for hybrid architectures
- Emerging technology expertise

### Professional Manifesto Alignment

**Truth Over Theater**:
- Real performance data from edge deployments
- Honest about edge computing limitations and constraints
- Realistic cost comparisons (edge vs serverless vs traditional)

**Reality-First Strategy**:
- Edge constraints acknowledged (compute limits, cold storage)
- Not everything belongs at edge (appropriate use cases)
- Vendor lock-in considerations for platform choice

**Demonstrable Performance Validation**:
- Latency measured from multiple geographic regions
- Cold start times benchmarked
- Cost analysis based on real usage patterns

**Strategic Accountability**:
- Clear guidance on when NOT to use edge computing
- Trade-offs between edge complexity and performance gains
- Migration strategies from traditional architectures

### Technical Expertise Areas

**Edge Platforms**:
- Cloudflare Workers: V8 isolates, Workers KV, Durable Objects, R2 storage
- Deno Deploy: Deno runtime, Fresh framework, edge APIs
- Vercel Edge Functions: Edge middleware, Edge Network
- AWS Lambda@Edge: CloudFront integration, regional edge caches
- Fastly Compute@Edge: WebAssembly, edge compute

**Edge Patterns**:
- Edge caching strategies (cache headers, purging, invalidation)
- Edge-side rendering (ESR) vs server-side rendering
- Edge middleware for authentication, routing, personalization
- Geolocation-based routing and content delivery
- A/B testing and feature flags at edge
- Edge security (DDoS protection, WAF, rate limiting)

**Performance Optimization**:
- Global latency reduction techniques
- Cold start optimization (<5ms target)
- Edge vs origin request routing
- Connection pooling and reuse
- Stream processing at edge

**Modern Frameworks**:
- Next.js Edge Runtime
- Remix with edge deployment
- SvelteKit edge adapters
- Astro edge rendering
- Nuxt 3 edge support
- Fresh (Deno) island architecture

**WebAssembly**:
- Compiling languages to WASM (Rust, Go, C++)
- WASM runtime in edge environments
- Performance characteristics of WASM vs JavaScript
- Use cases for WASM at edge

**Storage & State**:
- Workers KV (eventually consistent key-value)
- Durable Objects (strongly consistent, stateful)
- Edge caches (ephemeral storage)
- R2 (object storage), D1 (SQLite at edge)

### Model Assignment Justification: Sonnet

**Why Sonnet**:
1. **Moderate Complexity**: Edge patterns well-understood, not groundbreaking research
2. **Performance Focus**: Important but not life-critical (vs blockchain security)
3. **Rapid Iteration**: Edge deployments fast, benefit from quick development
4. **Cost Balance**: Sonnet good value for edge development work
5. **Adequate Reasoning**: Complex enough for distributed systems, not requiring Opus

**Cost/Value Trade-off**:
- Sonnet handles edge computing patterns effectively
- Not security-critical like blockchain or infrastructure
- Fast iteration more valuable than deepest possible reasoning
- Target market (startups, SaaS) appreciates cost efficiency

### Agent Persona

Edge Computing Specialist is a performance-obsessed developer who's tired of waiting for servers on the other side of the world. They've seen the latency charts, measured the milliseconds, and know that user experience starts with speed.

They're excited about the edge computing revolution: moving compute closer to users, eliminating cold starts, and achieving global deployment with a single command. They understand V8 isolates, know why they're faster than containers, and can explain the edge computing model to skeptics.

They're pragmatic: edge computing isn't a silver bullet. They know the constraints—limited CPU time, no filesystem access, eventual consistency in edge storage. They advocate for hybrid architectures: edge for what's fast and global, origin for what's complex and stateful.

They speak fluent Cloudflare Workers, understand Deno Deploy's island architecture, and keep up with the rapid evolution of edge runtimes. They measure performance relentlessly—TTFB, cold start times, cache hit rates—and optimize based on data, not intuition.

They champion modern web frameworks that embrace the edge: Remix, SvelteKit, Astro, Fresh. They know that edge computing is more than just speed—it's about delivering consistently fast experiences to users worldwide.

---

## 5. Platform Engineering Specialist

### Agent Metadata
- **Agent Name**: `platform-engineering-specialist`
- **Display Name**: Platform Engineering Specialist
- **Domain**: Platform Engineering / Internal Developer Platforms
- **Model Assignment**: **Opus** (complex systems design, organizational impact)
- **Priority**: **MEDIUM-HIGH** (79/100 points)
- **Color**: `#9370DB` (medium purple - representing platform/foundation)

### Market Demand Evidence

**Quantitative Data**:
- Platform engineering teams with SRE practices: 50% less downtime, 40% boost in system reliability
- Operational toil increased from 25% to 30% (2025 SRE Report)
- Platform Engineering rising from SRE evolution, maturing rapidly
- Trend: From firefighting to enablement, developer self-service focus

**Job Market Signals**:
- Platform Engineer roles distinct from DevOps/SRE emerging
- Internal Developer Platform (IDP) positions growing
- Developer Experience (DX) Engineer related role trend
- Skills: Kubernetes, service mesh, observability, developer tools

**Technology Adoption**:
- Backstage (Spotify): Open-source developer portal
- Internal developer platforms becoming standard at scale
- Golden Path concept: Paved road for common use cases
- Platform as product mindset gaining traction

**Competitive Gap**:
- Emerging discipline: VoltAgent may or may not have this
- We have devops-engineer and observability-engineer but not platform-focused
- Differentiation opportunity: Early positioning in emerging category
- Enterprise appeal: Large organizations building internal platforms

### Use Cases (20+ specific tasks)

**Internal Developer Platform (IDP)**:
1. Design internal developer platform architecture
2. Implement Backstage developer portal
3. Create service catalog with metadata standards
4. Build software templates for common services
5. Implement golden paths for deployments
6. Create self-service infrastructure provisioning
7. Build developer onboarding workflows
8. Implement platform documentation portal

**Platform Services**:
9. Design platform API layer for developer services
10. Implement multi-tenancy for platform services
11. Create platform observability (platform metrics, not just app metrics)
12. Build platform billing and cost allocation
13. Implement platform policy enforcement (Gatekeeper, OPA)
14. Create platform security standards and guardrails
15. Build environment provisioning automation
16. Implement secrets management as platform service

**Developer Experience**:
17. Design developer workflow optimization
18. Create CLI tools for platform interaction
19. Implement CI/CD as platform service
20. Build local development environment standardization
21. Create platform status dashboard and incident comms
22. Implement developer feedback loops and metrics
23. Build platform scorecard (DORA metrics, cost, security)

**Service Mesh & Infrastructure**:
24. Implement service mesh (Istio, Linkerd)
25. Create platform networking policies
26. Build certificate management automation
27. Implement cross-cluster service discovery

### Validation Plan (5 real tasks)

**Test 1: Backstage Developer Portal**
- Task: Deploy and configure Backstage with service catalog
- Requirements: Software catalog, TechDocs, templates, plugins
- Validation: Portal accessible, services discoverable, docs rendered
- Success Criteria: Functional developer portal, 5+ services cataloged

**Test 2: Golden Path Template**
- Task: Create software template for common service type (e.g., REST API)
- Requirements: Template creates repo, CI/CD, deploys to K8s, monitoring
- Validation: Template execution creates fully functional service
- Success Criteria: Developer can deploy service in <10 minutes

**Test 3: Self-Service Infrastructure**
- Task: Build self-service database provisioning (e.g., PostgreSQL instances)
- Requirements: API or UI for request, automated provisioning, credentials delivery
- Validation: Developer can request and receive database without platform team
- Success Criteria: <5 minute provisioning, proper access control

**Test 4: Platform Observability**
- Task: Implement platform health dashboard (not app metrics)
- Requirements: Platform component health, resource usage, cost tracking
- Validation: Dashboard shows platform status, alerts on degradation
- Success Criteria: Platform team can proactively identify issues

**Test 5: Policy Enforcement**
- Task: Implement platform policies with OPA or Gatekeeper
- Requirements: Resource quotas, security policies, naming conventions
- Validation: Policies enforced at deployment time, violations blocked
- Success Criteria: Non-compliant resources rejected, developers get clear feedback

### Differentiation from Competitors

**Our Advantages**:
1. **Platform as Product**: Developer-centric design, treating devs as customers
2. **Golden Paths**: Opinionated, paved roads for common use cases
3. **Developer Experience Focus**: Reducing cognitive load and toil
4. **Integration**: Works with devops-engineer, observability-engineer, cloud-architect
5. **Emerging Expertise**: Early positioning in new discipline

**vs devops-engineer (our existing agent)**:
- Platform thinking: Enabling developers vs operating infrastructure
- Self-service focus: Abstractions and golden paths
- Developer experience metrics (DORA, developer satisfaction)
- Internal tooling and automation at scale

**vs VoltAgent (uncertain if they have platform eng agent)**:
- Emerging discipline: May not be on VoltAgent's radar yet
- Modern platform patterns (Backstage, golden paths, platform as product)
- Integration with our SRE/DevOps agents for comprehensive coverage

### Professional Manifesto Alignment

**Truth Over Theater**:
- Honest about platform complexity and maintenance burden
- Realistic timelines for platform adoption and ROI
- Acknowledge platform engineering requires organizational buy-in

**Reality-First Strategy**:
- Start small: Don't over-engineer platforms
- Measure adoption: Unused platforms are wasted effort
- Iterative development: Platform evolves with org needs

**Demonstrable Platform Validation**:
- Platform features tested with real developer workflows
- Adoption metrics tracked (template usage, self-service adoption)
- Developer satisfaction measured (surveys, feedback)

**Strategic Accountability**:
- Clear guidance on when organization is ready for platform engineering
- Honest about cost (platform team, infrastructure, tooling)
- Migration strategies from manual to platform-automated

### Technical Expertise Areas

**Developer Portal Tools**:
- Backstage (Spotify): Service catalog, TechDocs, software templates
- Port: Developer portal platform
- OpsLevel: Service maturity tracking
- Cortex: Internal developer portal

**Platform Components**:
- Service catalog and metadata management
- Software templates (scaffolding)
- Golden paths and best practices
- Self-service infrastructure
- Developer documentation (TechDocs, wikis)
- Platform APIs and CLIs

**Infrastructure Abstractions**:
- Kubernetes operators for platform services
- Custom Resource Definitions (CRDs)
- Admission controllers (policies, validation)
- GitOps workflows (ArgoCD, Flux)
- Infrastructure as Code abstraction layers

**Developer Experience**:
- DORA metrics (deployment frequency, lead time, MTTR, change fail rate)
- Developer satisfaction surveys
- Cognitive load reduction strategies
- Local development environment parity
- Inner source and reusable components

**Service Mesh**:
- Istio: Traffic management, security, observability
- Linkerd: Lightweight service mesh
- Consul: Service networking
- Envoy Proxy: Edge and service proxy

**Policy & Governance**:
- Open Policy Agent (OPA): Policy as code
- Gatekeeper: Kubernetes policy enforcement
- Kyverno: Kubernetes-native policies
- Policy compliance and reporting

**Platform Engineering Principles**:
- Treating platform as product
- Developer-centric design (developers as customers)
- Self-service over ticket-driven ops
- Golden paths over unlimited flexibility
- Measuring platform adoption and satisfaction
- Continuous platform improvement

### Model Assignment Justification: Opus

**Why Opus**:
1. **Complex Systems Design**: Platform architecture affects entire organization
2. **Organizational Impact**: Wrong platform choices costly to reverse
3. **Multi-Team Coordination**: Understanding diverse developer needs
4. **Long-Term Strategy**: Platform decisions have multi-year implications
5. **Abstraction Design**: Creating right abstractions requires deep thinking

**Cost/Value Trade-off**:
- Enterprise audience: High value per interaction
- Strategic decisions: Platform architecture long-lived
- Complexity: Balancing flexibility vs simplicity requires reasoning
- ROI: Good platform engineering massive developer productivity gains

### Agent Persona

Platform Engineering Specialist is a systems thinker who's evolved from firefighting production incidents to building systems that prevent fires in the first place. They've experienced the pain of fragmented tooling, snowflake environments, and developers blocked waiting for infrastructure.

They champion the "platform as product" philosophy: treat developers as customers, measure adoption and satisfaction, and iterate based on feedback. They know the best platform is one developers actually use, not the most technically impressive one nobody understands.

They're pragmatic about complexity: they've seen over-engineered platforms that nobody adopts. They advocate for golden paths—opinionated, paved roads for the 80% use case—with escape hatches for the 20% edge cases. They know that platform engineering is about reducing cognitive load and toil, not shifting it elsewhere.

They speak the language of both developers and operators. They understand Kubernetes deeply but also know when to abstract it away. They measure success not just in uptime, but in developer velocity, satisfaction, and time-to-production for new services.

They're inspired by Backstage, Spotify's model, and the emerging platform engineering community. They know this discipline is young, evolving, and that early adopters have an opportunity to define best practices.

---

*[Due to length constraints, I'll continue with agents 6-10 in a focused summary format]*

## 6. Test Automation Engineer

**Agent Name**: `test-automation-engineer`
**Model**: Sonnet | **Priority**: MEDIUM-HIGH (76/100)

**Market Evidence**: Playwright surpassed Cypress downloads (June 2024), Microsoft-backed, enterprise adoption, most testers adopted or planning to adopt.

**Key Use Cases**:
- Playwright E2E tests, Cypress test suites
- Visual regression testing, API testing
- CI/CD test integration, parallel execution
- Cross-browser testing, mobile web testing
- Test reporting and debugging

**Differentiation**: qa-test-engineer covers general testing, this specializes in modern E2E frameworks (Playwright/Cypress), not overlapping but complementary.

**Validation**: Real test suites for sample apps, CI/CD integration, cross-browser validation.

---

## 7. Embedded Systems/IoT Developer

**Agent Name**: `embedded-iot-developer`
**Model**: Sonnet | **Priority**: MEDIUM (74/100)

**Market Evidence**: High demand, $130k+ top earners, IoT expansion, Industry 4.0, automotive electronics, medical devices.

**Key Use Cases**:
- C/C++ firmware for microcontrollers
- ESP32, Raspberry Pi, ARM Cortex development
- Sensor integration, MQTT/CoAP protocols
- RTOS implementation, embedded AI
- Industrial IoT applications

**Differentiation**: systems-engineer has C++ but not embedded-specific (no RTOS, hardware interfaces, low-power design).

**Validation Challenge**: Requires hardware access (mitigated with QEMU emulation, Wokwi simulator).

---

## 8. API Documentation Engineer

**Agent Name**: `api-documentation-engineer`
**Model**: Haiku | **Priority**: MEDIUM (72/100)

**Market Evidence**: OpenAPI industry standard, Swagger tools ubiquitous, API-first development growing.

**Key Use Cases**:
- OpenAPI 3.1 spec design
- Swagger UI, Redoc documentation
- API design reviews, mock servers
- Postman collections, API versioning
- Documentation generation from code

**Differentiation**: technical-writer has general docs, this specializes in API specs and tooling.

**Validation**: Generate OpenAPI specs, Swagger UI deployment, API design validation.

---

## 9. GraphQL Specialist

**Agent Name**: `graphql-specialist`
**Model**: Sonnet | **Priority**: MEDIUM (70/100)

**Market Evidence**: 61% org adoption, 25% annual growth, hybrid approach with REST, major companies (Facebook, GitHub, Shopify).

**Key Use Cases**:
- GraphQL server design (Apollo, Pothos)
- Schema design and federation
- Query optimization, N+1 problem solving
- Subscriptions for real-time data
- GraphQL security (depth limiting, rate limiting)

**Differentiation**: backend-api-engineer has GraphQL skills but not specialized depth (federation, performance optimization).

**Validation**: Build GraphQL API, implement federation, performance benchmarking.

---

## 10. Developer Advocate

**Agent Name**: `developer-advocate`
**Model**: Haiku | **Priority**: MEDIUM-LOW (68/100)

**Market Evidence**: $174k avg salary, 367 Web3 jobs, 138 remote positions, DevRel roles growing.

**Key Use Cases**:
- Technical blog post writing
- Conference talk preparation
- Code sample creation
- Tutorial and workshop development
- Developer community engagement
- Product feedback synthesis

**Differentiation**: technical-writer does docs, this does evangelism and community-focused content.

**Validation**: Write technical blog posts, create code samples, prepare conference talk outline.

---

## Summary Table: All 10 Proposed Agents

| # | Agent Name | Model | Priority | Score | Market Demand | Competitive Gap | Validation |
|---|------------|-------|----------|-------|---------------|-----------------|------------|
| 1 | Infrastructure as Code Specialist | Opus | HIGH | 88/100 | Very High | Critical | Easy |
| 2 | Blockchain/Web3 Engineer | Opus | HIGH | 85/100 | Very High | Critical | Easy |
| 3 | Game Development Engineer | Sonnet | HIGH | 82/100 | High | High | Moderate |
| 4 | Edge Computing Specialist | Sonnet | HIGH | 81/100 | High | Moderate | Easy |
| 5 | Platform Engineering Specialist | Opus | MED-HIGH | 79/100 | Emerging | Low | Moderate |
| 6 | Test Automation Engineer | Sonnet | MED-HIGH | 76/100 | High | Moderate | Easy |
| 7 | Embedded Systems/IoT Developer | Sonnet | MEDIUM | 74/100 | High | High | Hard |
| 8 | API Documentation Engineer | Haiku | MEDIUM | 72/100 | Moderate | Low | Easy |
| 9 | GraphQL Specialist | Sonnet | MEDIUM | 70/100 | Moderate | Low | Easy |
| 10 | Developer Advocate | Haiku | MED-LOW | 68/100 | Moderate | Low | Moderate |

**Recommended Implementation Order**:
- **Week 3**: Agents 1-4 (IaC, Blockchain, Game Dev, Edge Computing) - Highest priority, clear validation
- **Week 4**: Agents 5-7 (Platform Eng, Test Automation, Embedded/IoT) - Strategic additions
- **Optional**: Agents 8-10 if time permits and additional capacity

---

**Next Deliverable**: AGENT_PRIORITIZATION.md with detailed scoring framework
