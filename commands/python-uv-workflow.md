# Python UV Development Workflow

Modern Python development with UV and the latest tooling ecosystem:

**Project Initialization & Management:**
- Create new Python projects with `uv init` and modern pyproject.toml
- Set up virtual environments with lightning-fast `uv venv`
- Configure project metadata, dependencies, and build system
- Handle monorepo and workspace configurations

**Dependency Management:**
- Install packages with `uv add` for blazing fast dependency resolution
- Manage dev dependencies, optional dependencies, and extras
- Handle dependency conflicts and version constraints
- Lock dependencies with `uv.lock` for reproducible builds

**Environment Management:**
- Create isolated environments per project
- Switch between Python versions with `uv python`
- Handle multiple Python interpreters (CPython, PyPy)
- Sync environments across development and production

**Build & Distribution:**
- Build wheels and source distributions with modern build backends
- Configure build systems (setuptools, hatchling, pdm-backend)
- Handle C extensions and platform-specific builds
- Create distributable packages for PyPI or private indexes

**Development Tools Integration:**
- Set up pre-commit hooks with ruff, black, mypy
- Configure testing with pytest and coverage reporting
- Integrate with modern linters and formatters
- Handle documentation generation with sphinx or mkdocs

**Performance & Optimization:**
- Profile Python applications with py-spy or scalene
- Optimize dependency resolution and installation times
- Handle large dependency trees efficiently
- Minimize virtual environment size and startup time

**Cross-Platform Development:**
- Handle platform-specific dependencies and wheels
- Test across different operating systems in containers
- Manage platform markers and conditional dependencies
- Build universal wheels for distribution

**Integration with Your Stack:**
- Connect Python services to PostgreSQL in OrbStack
- Deploy Python applications to pi via dokku
- Interface with Rust extensions via PyO3 or ctypes
- Handle data processing pipelines and ETL workflows

**Advanced Workflows:**
- Set up matrix testing across Python versions
- Handle security scanning and vulnerability management
- Create custom build scripts and automation
- Integrate with CI/CD pipelines and deployment

**Troubleshooting & Debugging:**
- Debug dependency resolution conflicts
- Handle import errors and module path issues
- Profile memory usage and performance bottlenecks
- Diagnose virtual environment and path problems

Project/Task: $ARGUMENTS

