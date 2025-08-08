use std::sync::Arc;
use std::time::Duration;
use tokio::time::sleep;
use uuid::Uuid;

use claude_orchestration::{
    Config, OrchestrationEngine, Task, Agent, 
    TaskStatus, AgentStatus, SessionId, TaskId, AgentId
};

/// Integration tests for the orchestration engine
#[tokio::test]
async fn test_orchestration_engine_lifecycle() {
    let config = Arc::new(Config::default());
    
    // Initialize engine
    let engine = OrchestrationEngine::new(config).await
        .expect("Failed to create orchestration engine");
    
    // Start engine
    engine.start().await
        .expect("Failed to start orchestration engine");
    
    // Create session
    let session_id = engine.create_session(
        "Test Session".to_string(),
        "Integration test session".to_string(),
    ).await.expect("Failed to create session");
    
    // Create task
    let mut task = Task::new(
        session_id,
        "Test Task".to_string(),
        "A test task for integration testing".to_string(),
    );
    
    task.requirements.required_capabilities.push("testing".to_string());
    task.requirements.min_agents = 1;
    task.requirements.max_agents = 1;
    
    // Submit task
    let task_id = engine.submit_task(session_id, task).await
        .expect("Failed to submit task");
    
    // Wait a bit for processing
    sleep(Duration::from_millis(100)).await;
    
    // Check task status
    let status = engine.get_task_status(task_id).await
        .expect("Failed to get task status");
    
    // Task should be pending or assigned since we don't have real agents
    assert!(matches!(status, TaskStatus::Pending | TaskStatus::Assigned));
    
    // Check session status
    let session_status = engine.get_session_status(session_id).await
        .expect("Failed to get session status");
    
    // Session should be active
    assert!(matches!(session_status, claude_orchestration::orchestration::SessionStatus::Active));
    
    // Shutdown engine
    engine.shutdown().await
        .expect("Failed to shutdown orchestration engine");
}

#[tokio::test]
async fn test_agent_registration() {
    let config = Arc::new(Config::default());
    let engine = OrchestrationEngine::new(config).await
        .expect("Failed to create orchestration engine");
    
    engine.start().await
        .expect("Failed to start orchestration engine");
    
    // Create test agent
    let agent = Agent {
        id: "test-agent".to_string(),
        name: "Test Agent".to_string(),
        description: "A test agent".to_string(),
        capabilities: vec!["testing".to_string(), "example".to_string()],
        specializations: vec!["integration-testing".to_string()],
        status: AgentStatus::Available,
        current_load: 0.0,
        max_concurrent_tasks: 3,
        active_tasks: Vec::new(),
        performance_metrics: Default::default(),
        health: claude_orchestration::orchestration::HealthStatus {
            is_healthy: true,
            last_check: chrono::Utc::now(),
            response_time_ms: Some(100),
            error_count: 0,
            warnings: Vec::new(),
            details: std::collections::HashMap::new(),
        },
        configuration: std::collections::HashMap::new(),
        last_heartbeat: chrono::Utc::now(),
        version: "1.0.0".to_string(),
    };
    
    // Register agent
    engine.register_agent(agent).await
        .expect("Failed to register agent");
    
    // Create session and task that requires the agent
    let session_id = engine.create_session(
        "Agent Test Session".to_string(),
        "Testing agent registration".to_string(),
    ).await.expect("Failed to create session");
    
    let mut task = Task::new(
        session_id,
        "Agent Test Task".to_string(),
        "A task to test agent assignment".to_string(),
    );
    
    task.requirements.required_capabilities.push("testing".to_string());
    task.requirements.preferred_agents.push("test-agent".to_string());
    
    let task_id = engine.submit_task(session_id, task).await
        .expect("Failed to submit task");
    
    sleep(Duration::from_millis(100)).await;
    
    let status = engine.get_task_status(task_id).await
        .expect("Failed to get task status");
    
    // Task should be assigned to our registered agent
    assert!(matches!(status, TaskStatus::Assigned | TaskStatus::InProgress));
    
    engine.shutdown().await
        .expect("Failed to shutdown orchestration engine");
}

#[tokio::test]
async fn test_health_check() {
    let config = Arc::new(Config::default());
    let engine = OrchestrationEngine::new(config).await
        .expect("Failed to create orchestration engine");
    
    engine.start().await
        .expect("Failed to start orchestration engine");
    
    let health = engine.health_check().await
        .expect("Failed to perform health check");
    
    assert!(health.is_healthy);
    assert_eq!(health.active_sessions, 0);
    assert_eq!(health.active_tasks, 0);
    
    engine.shutdown().await
        .expect("Failed to shutdown orchestration engine");
}

#[tokio::test]
async fn test_task_cancellation() {
    let config = Arc::new(Config::default());
    let engine = OrchestrationEngine::new(config).await
        .expect("Failed to create orchestration engine");
    
    engine.start().await
        .expect("Failed to start orchestration engine");
    
    let session_id = engine.create_session(
        "Cancellation Test".to_string(),
        "Testing task cancellation".to_string(),
    ).await.expect("Failed to create session");
    
    let task = Task::new(
        session_id,
        "Cancellable Task".to_string(),
        "A task that will be cancelled".to_string(),
    );
    
    let task_id = engine.submit_task(session_id, task).await
        .expect("Failed to submit task");
    
    // Cancel the task
    engine.cancel_task(task_id).await
        .expect("Failed to cancel task");
    
    let status = engine.get_task_status(task_id).await
        .expect("Failed to get task status");
    
    assert_eq!(status, TaskStatus::Cancelled);
    
    engine.shutdown().await
        .expect("Failed to shutdown orchestration engine");
}

/// Performance benchmark tests
mod benchmarks {
    use super::*;
    use std::time::Instant;
    
    #[tokio::test]
    async fn benchmark_task_submission() {
        let config = Arc::new(Config::default());
        let engine = OrchestrationEngine::new(config).await
            .expect("Failed to create orchestration engine");
        
        engine.start().await
            .expect("Failed to start orchestration engine");
        
        let session_id = engine.create_session(
            "Benchmark Session".to_string(),
            "Performance benchmark session".to_string(),
        ).await.expect("Failed to create session");
        
        let num_tasks = 100;
        let start_time = Instant::now();
        
        for i in 0..num_tasks {
            let task = Task::new(
                session_id,
                format!("Benchmark Task {}", i),
                "A benchmark task".to_string(),
            );
            
            engine.submit_task(session_id, task).await
                .expect("Failed to submit benchmark task");
        }
        
        let duration = start_time.elapsed();
        let tasks_per_second = num_tasks as f64 / duration.as_secs_f64();
        
        println!("Task submission rate: {:.2} tasks/second", tasks_per_second);
        
        // Should be able to submit at least 100 tasks per second
        assert!(tasks_per_second >= 100.0, 
               "Task submission rate too slow: {:.2} tasks/second", tasks_per_second);
        
        engine.shutdown().await
            .expect("Failed to shutdown orchestration engine");
    }
    
    #[tokio::test]
    async fn benchmark_concurrent_sessions() {
        let config = Arc::new(Config::default());
        let engine = Arc::new(OrchestrationEngine::new(config).await
            .expect("Failed to create orchestration engine"));
        
        engine.start().await
            .expect("Failed to start orchestration engine");
        
        let num_sessions = 50;
        let start_time = Instant::now();
        
        // Create sessions concurrently
        let mut handles = Vec::new();
        for i in 0..num_sessions {
            let engine_clone = engine.clone();
            let handle = tokio::spawn(async move {
                engine_clone.create_session(
                    format!("Concurrent Session {}", i),
                    "Concurrent benchmark session".to_string(),
                ).await.expect("Failed to create concurrent session")
            });
            handles.push(handle);
        }
        
        // Wait for all sessions to be created
        let mut session_ids = Vec::new();
        for handle in handles {
            session_ids.push(handle.await.expect("Failed to join session creation task"));
        }
        
        let duration = start_time.elapsed();
        let sessions_per_second = num_sessions as f64 / duration.as_secs_f64();
        
        println!("Concurrent session creation rate: {:.2} sessions/second", sessions_per_second);
        
        // Verify all sessions were created
        assert_eq!(session_ids.len(), num_sessions);
        
        // Should be able to create at least 50 sessions per second
        assert!(sessions_per_second >= 50.0,
               "Session creation rate too slow: {:.2} sessions/second", sessions_per_second);
        
        engine.shutdown().await
            .expect("Failed to shutdown orchestration engine");
    }
}

/// Test utilities and helpers
mod test_utils {
    use super::*;
    
    pub fn create_test_agent(id: &str, capabilities: Vec<String>) -> Agent {
        Agent {
            id: id.to_string(),
            name: format!("Test Agent {}", id),
            description: "A test agent for unit testing".to_string(),
            capabilities,
            specializations: vec!["testing".to_string()],
            status: AgentStatus::Available,
            current_load: 0.0,
            max_concurrent_tasks: 5,
            active_tasks: Vec::new(),
            performance_metrics: Default::default(),
            health: claude_orchestration::orchestration::HealthStatus {
                is_healthy: true,
                last_check: chrono::Utc::now(),
                response_time_ms: Some(50),
                error_count: 0,
                warnings: Vec::new(),
                details: std::collections::HashMap::new(),
            },
            configuration: std::collections::HashMap::new(),
            last_heartbeat: chrono::Utc::now(),
            version: "1.0.0".to_string(),
        }
    }
    
    pub fn create_test_task(session_id: SessionId, name: &str) -> Task {
        Task::new(
            session_id,
            name.to_string(),
            "A test task for unit testing".to_string(),
        )
    }
}