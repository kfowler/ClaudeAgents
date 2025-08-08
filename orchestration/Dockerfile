# Multi-stage build for optimal performance and minimal image size
FROM rust:1.75-slim-bullseye as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libpq-dev \
    cmake \
    clang \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Cache dependencies by building with dummy source
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Copy source code
COPY src ./src

# Build application with optimizations
ENV RUSTFLAGS="-C target-cpu=native"
RUN touch src/main.rs && cargo build --release

# Runtime stage
FROM debian:bullseye-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl1.1 \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r orchestration && useradd -r -g orchestration orchestration

# Create app directory
WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/target/release/claude-orchestration ./orchestration

# Copy configuration
COPY config.toml ./

# Create logs directory
RUN mkdir -p logs && chown -R orchestration:orchestration /app

# Switch to non-root user
USER orchestration

# Expose ports
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["./orchestration", "--config", "config.toml"]