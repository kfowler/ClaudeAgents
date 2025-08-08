mod config;
mod orchestration;
mod communication;
mod persistence;
mod agents;
mod monitoring;
mod error;

use anyhow::Result;
use clap::Parser;
use config::Config;
use orchestration::OrchestrationEngine;
use tracing::{info, error};
use std::sync::Arc;

#[derive(Parser, Debug)]
#[command(name = "claude-orchestration")]
#[command(about = "High-performance multi-agent orchestration engine")]
struct Args {
    /// Configuration file path
    #[arg(short, long, default_value = "config.toml")]
    config: String,
    
    /// Log level
    #[arg(short, long, default_value = "info")]
    log_level: String,
    
    /// Port to run the server on
    #[arg(short, long, default_value_t = 8080)]
    port: u16,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(args.log_level)
        .json()
        .init();
    
    info!("Starting Claude Orchestration Engine");
    
    // Load configuration
    let config = Arc::new(Config::from_file(&args.config).await?);
    info!("Configuration loaded from: {}", args.config);
    
    // Initialize orchestration engine
    let engine = OrchestrationEngine::new(config.clone()).await?;
    info!("Orchestration engine initialized");
    
    // Start the engine
    match engine.start().await {
        Ok(_) => {
            info!("Orchestration engine started successfully");
        }
        Err(e) => {
            error!("Failed to start orchestration engine: {}", e);
            return Err(e);
        }
    }
    
    // Handle graceful shutdown
    tokio::signal::ctrl_c().await?;
    info!("Received shutdown signal, stopping orchestration engine");
    
    engine.shutdown().await?;
    info!("Orchestration engine stopped gracefully");
    
    Ok(())
}