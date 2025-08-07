# Rust Cargo Development Workflow

Comprehensive Rust development with cargo and the Rust ecosystem:

**Project Management:**
- Initialize new cargo projects with appropriate templates
- Manage workspace configurations for multi-crate projects
- Handle feature flags and conditional compilation
- Configure cargo.toml for different targets and platforms

**Dependency Management:**
- Search and add crates from crates.io with version constraints
- Manage dev-dependencies, build-dependencies, and optional features
- Handle dependency conflicts and version resolution
- Audit dependencies for security vulnerabilities with cargo-audit

**Build & Compilation:**
- Configure build profiles for development, release, and custom targets
- Handle cross-compilation for different architectures
- Manage build scripts and procedural macros
- Optimize compilation times with incremental builds and caching

**Testing & Quality:**
- Run unit tests, integration tests, and doc tests
- Generate test coverage reports with cargo-tarpaulin
- Run benchmarks with criterion or built-in bench tests
- Perform property-based testing with quickcheck

**Code Quality & Linting:**
- Run clippy with custom lint configurations
- Format code with rustfmt and custom style rules
- Check for unused dependencies with cargo-udeps
- Analyze code complexity and maintainability metrics

**Documentation:**
- Generate and serve documentation locally with cargo doc
- Write and test documentation examples
- Create comprehensive API documentation
- Generate mdBook documentation for projects

**Deployment & Distribution:**
- Build optimized release binaries
- Create distributable packages and installers
- Publish crates to crates.io or private registries
- Handle versioning and changelog generation

**Integration with Your Stack:**
- Connect Rust services to PostgreSQL via sqlx or diesel
- Deploy Rust applications to pi via dokku
- Create Docker images with distroless or alpine base
- Interface with C/C++ code through FFI

**Advanced Tooling:**
- Use cargo-expand to examine macro expansions
- Profile memory usage with valgrind or heaptrack
- Analyze binary size with cargo-bloat
- Generate flame graphs for performance analysis

Task/Component: $ARGUMENTS

