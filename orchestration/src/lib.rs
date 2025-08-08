//! # Claude Multi-Agent Orchestration Engine
//!
//! A high-performance, production-ready orchestration system for real-time multi-agent collaboration
//! with advanced coordination capabilities.
//!
//! ## Features
//!
//! - **Real-Time Coordination**: Agents work simultaneously with shared context and communication
//! - **Dynamic Task Distribution**: Intelligent work splitting and load balancing across agents
//! - **Conflict Resolution**: Handle overlapping responsibilities and contradictory recommendations
//! - **Progress Synchronization**: Real-time status updates and coordination across agents
//! - **Resource Management**: Optimize token usage and computational resources
//! - **Fault Tolerance**: Graceful degradation and recovery when agents fail
//!
//! ## Architecture
//!
//! The orchestration engine is built with a modern event-driven architecture:
//!
//! - **Asynchronous Core**: Built on Rust with Tokio for maximum performance
//! - **Event-Driven**: Message-based communication with Redis/RabbitMQ support
//! - **Real-Time**: WebSocket connections for live coordination and progress updates
//! - **Fault Tolerant**: Circuit breakers, graceful degradation, and automatic recovery
//! - **Scalable**: Kubernetes-native with dynamic agent scaling
//! - **Observable**: Comprehensive metrics, tracing, and monitoring

pub mod config;
pub mod error;
pub mod orchestration;
pub mod communication;
pub mod persistence;
pub mod agents;
pub mod monitoring;

pub use config::Config;
pub use error::{OrchestrationError, Result};
pub use orchestration::{OrchestrationEngine, Task, Agent, SessionId, TaskId, AgentId};

/// Version information
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Build information
pub const BUILD_INFO: &str = concat!(
    env!("CARGO_PKG_VERSION"),
    " (",
    env!("VERGEN_GIT_SHA"),
    " ",
    env!("VERGEN_BUILD_TIMESTAMP"),
    ")"
);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn version_info() {
        assert!(!VERSION.is_empty());
        println!("Version: {}", VERSION);
        println!("Build: {}", BUILD_INFO);
    }
}