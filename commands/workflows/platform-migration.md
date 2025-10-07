---
name: platform-migration
description: "Cross-platform migration workflow coordinating macOS, Windows, and Linux specialists with DevOps for seamless application and infrastructure migration across operating systems"
agents:
  - macos-specialist
  - windows-specialist
  - linux-sysadmin
  - devops-engineer
  - project-orchestrator
complexity: high
duration: 10-15 hours
---

# Platform Migration Workflow

**Command:** `/platform-migration`
**Agents:** `project-orchestrator`, `macos-specialist`, `windows-specialist`, `linux-sysadmin`, `devops-engineer`
**Complexity:** High
**Duration:** 10-15 hours

## Overview

Comprehensive cross-platform migration workflow that coordinates platform specialists and DevOps engineers to migrate applications, infrastructure, and development environments across macOS, Windows, and Linux ecosystems with minimal downtime and maximum compatibility.

## What This Command Does

This command orchestrates platform migration across 5 phases:

### Phase 1: Platform Assessment & Compatibility Analysis (2-3 hours)
**Lead:** `project-orchestrator`, **Supporting:** All platform specialists

- Analyze current platform architecture and dependencies
- Identify platform-specific code, libraries, and system calls
- Assess filesystem differences (case sensitivity, path separators, permissions)
- Evaluate process management differences (systemd vs launchd vs Windows services)
- Identify GUI framework compatibility (Cocoa, Win32, GTK, Qt)
- Analyze package manager differences (Homebrew, Chocolatey, apt/yum)
- Assess networking stack differences (socket behavior, firewall, DNS)
- Identify shell scripting differences (bash, zsh, PowerShell, cmd)
- Evaluate compiler and runtime differences (MSVC vs GCC/Clang)
- Analyze security model differences (permissions, UAC, SELinux, sandboxing)

Platform-Specific Analysis:
- **macOS**: Identify Cocoa/Foundation usage, Xcode dependencies, .app bundles, launchd services
- **Windows**: Identify Win32 API usage, registry dependencies, MSI installers, Windows services
- **Linux**: Identify systemd units, kernel dependencies, package formats (deb/rpm), X11/Wayland

**Deliverables:**
- Platform compatibility matrix (what works where, what needs porting)
- Dependency inventory per platform (libraries, tools, frameworks)
- File system compatibility report (case sensitivity issues, path problems)
- Process management migration plan (systemd <-> launchd <-> Windows services)
- Security model mapping (permissions, sandboxing, firewall rules)
- Risk assessment with mitigation strategies
- Estimated migration effort by component

### Phase 2: Migration Planning & Architecture Design (2-3 hours)
**Lead:** `project-orchestrator`, **Supporting:** Platform specialists

Migration Strategy Selection:
- **Lift-and-shift**: Minimal code changes, platform-specific builds
- **Cross-platform abstraction**: Shared codebase, platform abstraction layer
- **Platform-native rewrite**: Separate implementations per platform
- **Containerization**: Docker/container-based deployment (reduces differences)
- **Hybrid approach**: Mix of strategies based on component

Architecture Design:
- Design cross-platform abstraction layers (filesystem, process, network)
- Plan conditional compilation strategy (#ifdef, build flags)
- Design platform-specific modules and interfaces
- Plan dependency injection for platform-specific implementations
- Design testing strategy per platform (unit, integration, E2E)
- Plan CI/CD pipeline for multi-platform builds
- Design deployment strategy per platform (installers, packages, containers)

Build System Design:
- Choose build system (CMake, Meson, Bazel for cross-platform consistency)
- Design platform-specific build configurations
- Plan cross-compilation strategy (if building on one platform for another)
- Design artifact naming and versioning per platform
- Plan codesigning and notarization (macOS, Windows)

**Deliverables:**
- Migration strategy document with component breakdown
- Cross-platform architecture diagram with abstraction layers
- Build system configuration (CMakeLists.txt, Makefile, etc.)
- CI/CD pipeline design (GitHub Actions, GitLab CI, Jenkins)
- Deployment strategy per platform (App Store, Microsoft Store, package repos)
- Code organization plan (shared code, platform-specific code)
- Timeline and resource allocation

### Phase 3: Platform-Specific Implementation (3-4 hours)
**Leads:** `macos-specialist`, `windows-specialist`, `linux-sysadmin`

**macOS Migration** (lead: `macos-specialist`):
- Port to Cocoa/AppKit or Swift UI (if native GUI)
- Create .app bundle structure and Info.plist
- Implement launchd service/agent plist files
- Configure sandboxing entitlements (com.apple.security.*)
- Implement macOS-specific features (Touch Bar, Notification Center, Continuity)
- Configure Keychain access for credentials
- Implement Sparkle or custom update mechanism
- Create installer (DMG, PKG, or Homebrew formula)
- Configure code signing and notarization (Apple Developer ID)
- Port shell scripts to bash/zsh (macOS default shell changed to zsh)
- Configure filesystem permissions (APFS considerations)
- Implement Finder integration (Quick Look, Spotlight)

**Windows Migration** (lead: `windows-specialist`):
- Port to Win32 API, WPF, or WinUI 3 (if native GUI)
- Create Windows services (ServiceBase, sc.exe)
- Implement registry access for configuration
- Configure UAC manifests and elevation requirements
- Implement Windows-specific features (taskbar, notifications, jump lists)
- Configure Credential Manager for secrets
- Implement auto-update mechanism (Squirrel.Windows, WinSparkle)
- Create installer (MSI via WiX, MSIX, Inno Setup)
- Configure code signing (Authenticode, signtool.exe)
- Port shell scripts to PowerShell or batch files
- Configure NTFS permissions and ACLs
- Implement Explorer integration (shell extensions, context menus)

**Linux Migration** (lead: `linux-sysadmin`):
- Port to GTK, Qt, or keep cross-platform (Electron, Tauri)
- Create systemd service units (.service files)
- Configure systemd unit dependencies (After=, Requires=)
- Implement Linux-specific features (D-Bus, desktop notifications)
- Configure Secret Service API for credentials (libsecret)
- Implement package-based updates (apt, yum, AppImage updates)
- Create packages (deb, rpm, AppImage, Flatpak, Snap)
- Port shell scripts to bash (ensure POSIX compatibility)
- Configure filesystem permissions (chmod, chown, setuid)
- Implement desktop integration (.desktop files, XDG autostart)
- Configure SELinux/AppArmor policies (if applicable)
- Setup logrotate for application logs

**Deliverables:**
- Platform-specific codebases or build artifacts
- macOS: .app bundle, DMG installer, launchd plists, entitlements
- Windows: .exe, MSI/MSIX installer, Windows service, registry keys
- Linux: binaries, .deb/.rpm packages, systemd units, .desktop files
- Platform-specific configuration files
- Build scripts per platform (Xcode project, Visual Studio solution, Makefile)
- Unit tests passing on all platforms
- Platform integration documented (services, notifications, updates)

### Phase 4: Cross-Platform Testing & Validation (2-3 hours)
**Lead:** `devops-engineer`, **Supporting:** All platform specialists

Testing Infrastructure:
- Setup CI/CD runners for all platforms (macOS, Windows, Linux)
- Configure automated builds on all platforms (GitHub Actions matrix builds)
- Setup VM/container environments for testing
- Configure automated testing on all platforms

Functional Testing:
- Run unit tests on all platforms (detect platform-specific bugs)
- Execute integration tests (file I/O, network, IPC, database)
- Perform E2E tests (full application workflow)
- Test installers on clean systems (no development tools)
- Verify uninstall/cleanup procedures
- Test update mechanisms (in-place upgrades, rollback)

Compatibility Testing:
- Test on multiple OS versions (macOS 12-14, Windows 10-11, Ubuntu 20.04-24.04)
- Verify platform-specific features (native UI, services, notifications)
- Test filesystem compatibility (case sensitivity, symlinks, permissions)
- Verify network behavior (firewall, DNS, proxy)
- Test clipboard and drag-and-drop
- Verify high-DPI scaling (Retina, 4K displays)
- Test with different locales and languages

Performance Testing:
- Benchmark performance on each platform
- Profile memory usage (detect leaks, excessive allocation)
- Profile CPU usage (detect platform-specific bottlenecks)
- Test startup time and shutdown cleanup
- Benchmark file I/O operations
- Test under load (stress testing, concurrency)

**Deliverables:**
- Automated test suite running on all platforms
- CI/CD pipeline with multi-platform builds
- Test reports with platform-specific results
- Performance benchmarks per platform
- Compatibility matrix (OS versions, hardware configurations)
- Bug reports for platform-specific issues
- Testing documentation and runbooks

### Phase 5: Deployment & Documentation (2-3 hours)
**Lead:** `devops-engineer`, **Supporting:** Platform specialists

Deployment Automation:
- Configure automated builds for releases (tag-based, nightly)
- Setup artifact storage (GitHub Releases, S3, CDN)
- Configure codesigning in CI/CD (macOS notarization, Windows Authenticode)
- Setup automatic installer generation
- Configure update server/mechanism per platform
- Plan rollout strategy (phased, canary, blue-green)

Distribution:
- **macOS**: Submit to App Store (if applicable), distribute DMG, Homebrew tap
- **Windows**: Submit to Microsoft Store (if applicable), distribute MSI/MSIX, Chocolatey package
- **Linux**: Submit to package repositories (apt, yum), Snap Store, Flathub
- Setup download page with platform detection
- Configure CDN for distribution (CloudFront, Cloudflare)

Monitoring & Observability:
- Setup crash reporting per platform (Sentry, Crashlytics, Bugsnag)
- Configure analytics (usage metrics, feature adoption)
- Setup logging aggregation (centralized logs across platforms)
- Configure alerting for deployment issues
- Plan rollback procedures per platform

Documentation:
- Create installation guides per platform (screenshots, videos)
- Document platform-specific configuration options
- Create troubleshooting guides (common issues per platform)
- Document build process for developers (how to build locally)
- Create platform-specific FAQ
- Document migration guide for users (moving from old version/platform)
- Create developer documentation (architecture, building, testing)

**Deliverables:**
- Automated deployment pipeline (CI/CD with releases)
- Distribution packages ready for all platforms
- Update mechanism configured and tested
- Crash reporting and monitoring configured
- Installation guides for all platforms
- User documentation (quick start, troubleshooting)
- Developer documentation (build, test, deploy)
- Platform-specific release notes

## Expected Outcomes

### Platform Artifacts
- **macOS**: Universal binary (x86_64 + ARM64), DMG installer, code-signed and notarized
- **Windows**: x64/ARM64 executables, MSI/MSIX installer, Authenticode-signed
- **Linux**: x86_64/ARM64 binaries, deb/rpm/AppImage/Flatpak/Snap packages
- **Cross-platform**: Docker images (if applicable)
- **Source**: Build scripts for all platforms (CMake, Makefiles, etc.)

### Architecture Quality
- **Abstraction layers** for platform differences (filesystem, process, network, GUI)
- **Shared codebase** maximized (80%+ common code, 20% platform-specific)
- **Consistent behavior** across platforms (same features, same UX)
- **Platform-native feel** (respects platform conventions and UX patterns)
- **Maintainable** (clear separation, documented platform-specific code)
- **Testable** (automated tests on all platforms, 80%+ coverage)

### Business Value
- **Market expansion** (reach users on all major platforms)
- **Reduced maintenance** (shared codebase, not separate implementations)
- **Better UX** (platform-native feel, not lowest-common-denominator)
- **Faster releases** (automated multi-platform builds)
- **Higher quality** (automated testing on all platforms)
- **Easier onboarding** (developers can build on any platform)

## Usage

```bash
# Migrate desktop application from macOS to Windows and Linux
/platform-migration --from=macos --to=windows,linux --app-type=desktop

# Migrate backend service from Linux to Windows
/platform-migration --from=linux --to=windows --app-type=service

# Migrate CLI tool to all platforms
/platform-migration --from=linux --to=all --app-type=cli

# Migrate with containerization strategy
/platform-migration --strategy=containers --platforms=all

# Migrate with platform-native UIs
/platform-migration --ui=native --platforms=macos,windows,linux
```

## Prerequisites

- [ ] Source code access (version control, build instructions)
- [ ] Current platform architecture documented
- [ ] Dependencies identified (libraries, tools, runtimes)
- [ ] Target platforms prioritized (which platforms first)
- [ ] Build environment setup (SDKs, compilers, tools)
- [ ] Testing resources (VMs, physical machines, CI/CD credits)
- [ ] Developer accounts (Apple Developer, Microsoft Partner, etc.)
- [ ] Budget for codesigning certificates and distribution

## Success Criteria

### Compatibility
- [ ] Application builds successfully on all target platforms
- [ ] All unit tests pass on all platforms (no platform-specific failures)
- [ ] Integration tests pass on all platforms
- [ ] Installers tested on clean systems (no dev tools required)
- [ ] Platform-specific features working (services, notifications, updates)
- [ ] Filesystem operations compatible (case sensitivity, paths, permissions)
- [ ] Network operations consistent across platforms

### Performance
- [ ] Performance within 10% across platforms (no major regressions)
- [ ] Memory usage acceptable on all platforms (<5% difference)
- [ ] Startup time consistent (<20% difference)
- [ ] Binary sizes reasonable (appropriate for each platform)

### Distribution
- [ ] Installers signed (macOS notarized, Windows Authenticode)
- [ ] Packages available (DMG, MSI, deb/rpm/AppImage)
- [ ] Update mechanism working on all platforms
- [ ] Distribution channels configured (stores, repositories, website)
- [ ] Installation guides complete and tested

### Operations
- [ ] CI/CD building all platforms automatically
- [ ] Crash reporting configured per platform
- [ ] Logging and monitoring operational
- [ ] Rollback procedures tested
- [ ] Documentation complete (user and developer docs)

## Real-World Example: Electron App Migration to Native

**Migration Time:** 12 hours
**Team:** 5 engineers (orchestrator, macOS specialist, Windows specialist, Linux sysadmin, DevOps)

**Starting Point:**
- Electron app (500MB installer, 200MB RAM, slow startup)
- macOS only
- App Store rejection (sandboxing issues, bundle size)

**Migration Strategy:**
- **macOS**: SwiftUI native app
- **Windows**: WinUI 3 native app
- **Linux**: GTK 4 native app
- **Shared**: Rust backend (80% shared code)

**Platform-Specific Delivered:**

**macOS:**
- SwiftUI app (10MB installer, 40MB RAM, instant startup)
- Universal binary (x86_64 + Apple Silicon)
- Notarized DMG + Homebrew Cask
- Spotlight integration, Touch Bar support
- macOS 12+ (targets latest 3 OS versions)

**Windows:**
- WinUI 3 app (15MB installer, 50MB RAM, fast startup)
- x64 + ARM64 binaries
- MSIX package + Chocolatey
- Windows 10/11 taskbar integration, notifications
- Auto-update via Microsoft Store

**Linux:**
- GTK 4 app (12MB package, 45MB RAM, fast startup)
- x86_64 + ARM64 binaries
- deb, rpm, AppImage, Flatpak
- D-Bus integration, GNOME/KDE theming
- Ubuntu 20.04+, Fedora 36+, Arch

**Shared Backend (Rust):**
- 15K lines shared Rust code (business logic, data, networking)
- Platform-specific: 2K lines each (macOS: Swift, Windows: C#, Linux: C/GTK)
- FFI layer for native UI <-> Rust backend

**Impact:**
- **Installer size**: 500MB → 10-15MB (97% reduction)
- **Memory usage**: 200MB → 40-50MB (75% reduction)
- **Startup time**: 3s → <200ms (95% faster)
- **User satisfaction**: 3.2 → 4.7 stars (47% improvement)
- **Market reach**: macOS only → macOS + Windows + Linux (3x potential users)
- **App Store**: Approved (native, small, sandboxed)
- **Performance**: Native feel, respects platform UX conventions

**Technical Highlights:**
- CI/CD: GitHub Actions with matrix builds (macOS-latest, windows-latest, ubuntu-latest)
- Codesigning: Automated in CI (Apple Developer cert, Windows cert, no signing for Linux)
- Testing: 82% test coverage, all platforms tested on every commit
- Release: Tag-based releases, automatic builds, GitHub Releases + distribution channels

## Related Commands

- `/quality:architecture-review` - Review migration architecture
- `/security-audit` - Security review per platform
- `/quality:performance-optimization` - Optimize per platform
- `/documentation-generator` - Generate platform-specific docs

## Notes

**When to Migrate Platforms:**
- Expanding market reach (new user segments)
- Current platform limitations (performance, features, distribution)
- Regulatory requirements (specific platforms required)
- Business requirements (enterprise customers need Windows/Linux)
- User demand (significant requests for other platforms)

**When NOT to Migrate:**
- Small user base (migration cost > benefit)
- Platform-specific app (deeply tied to platform features)
- Prototype/MVP phase (focus on product-market fit first)
- Insufficient resources (migration requires sustained effort)

**Migration Strategies:**

**1. Lift-and-Shift (Lowest effort, platform limitations remain):**
- Minimal code changes
- Platform-specific builds (conditional compilation)
- Shared codebase but platform quirks exposed
- Best for: CLI tools, backend services, simple apps

**2. Cross-Platform Framework (Medium effort, common denominator UX):**
- Qt, Electron, Flutter, Tauri
- Single codebase, multiple platforms
- Non-native look and feel
- Best for: Internal tools, MVPs, web-like apps

**3. Platform Abstraction (High effort, best results):**
- Shared business logic (Rust, Go, C++)
- Platform-native UI (SwiftUI, WinUI, GTK)
- Best UX, platform conventions respected
- Best for: Consumer apps, performance-critical apps

**4. Containerization (Special case):**
- Docker/Kubernetes for backend services
- Reduces platform differences significantly
- Not applicable for desktop apps
- Best for: Microservices, backend services, APIs

**Common Pitfalls:**

**Filesystem:**
- Case sensitivity (macOS/Linux: optional, Windows: always case-insensitive)
- Path separators (/ vs \)
- Symlinks (work differently on Windows)
- Permissions (POSIX vs ACLs)

**Process Management:**
- systemd vs launchd vs Windows services (completely different)
- Signal handling (SIGTERM, SIGKILL don't exist on Windows)
- Environment variables (different defaults)

**GUI:**
- Native look and feel (users expect platform conventions)
- High-DPI scaling (Retina, 4K)
- Dark mode support (different APIs)
- Clipboard and drag-and-drop (platform-specific)

**Networking:**
- Firewall (macOS prompts, Windows prompts, Linux silent)
- DNS resolution (different resolvers)
- Proxy settings (different locations)

**Security:**
- macOS: Sandboxing, entitlements, Gatekeeper, notarization
- Windows: UAC, SmartScreen, Authenticode
- Linux: SELinux, AppArmor, capabilities

This workflow ensures platform migration is systematic, thorough, and results in high-quality native experiences on all target platforms.
