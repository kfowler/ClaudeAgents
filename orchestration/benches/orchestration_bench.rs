use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use std::sync::Arc;
use tokio::runtime::Runtime;

use claude_orchestration::{Config, OrchestrationEngine, Task};

/// Benchmark task submission performance
fn benchmark_task_submission(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("task_submission");
    
    for num_tasks in [10, 50, 100, 500].iter() {
        group.bench_with_input(
            BenchmarkId::new("submit_tasks", num_tasks),
            num_tasks,
            |b, &num_tasks| {
                b.to_async(&rt).iter(|| async {
                    let config = Arc::new(Config::default());
                    let engine = OrchestrationEngine::new(config).await
                        .expect("Failed to create engine");
                    
                    engine.start().await
                        .expect("Failed to start engine");
                    
                    let session_id = engine.create_session(
                        "Benchmark Session".to_string(),
                        "Performance test session".to_string(),
                    ).await.expect("Failed to create session");
                    
                    for i in 0..num_tasks {
                        let task = Task::new(
                            session_id,
                            format!("Benchmark Task {}", i),
                            "A benchmark task".to_string(),
                        );
                        
                        let _ = black_box(engine.submit_task(session_id, task).await);
                    }
                    
                    engine.shutdown().await
                        .expect("Failed to shutdown engine");
                });
            },
        );
    }
    
    group.finish();
}

/// Benchmark session creation performance
fn benchmark_session_creation(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    c.bench_function("session_creation", |b| {
        b.to_async(&rt).iter(|| async {
            let config = Arc::new(Config::default());
            let engine = OrchestrationEngine::new(config).await
                .expect("Failed to create engine");
            
            engine.start().await
                .expect("Failed to start engine");
            
            let _session_id = black_box(
                engine.create_session(
                    "Benchmark Session".to_string(),
                    "Performance test session".to_string(),
                ).await.expect("Failed to create session")
            );
            
            engine.shutdown().await
                .expect("Failed to shutdown engine");
        });
    });
}

/// Benchmark engine initialization
fn benchmark_engine_init(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    c.bench_function("engine_initialization", |b| {
        b.to_async(&rt).iter(|| async {
            let config = Arc::new(Config::default());
            let engine = black_box(
                OrchestrationEngine::new(config).await
                    .expect("Failed to create engine")
            );
            
            engine.start().await
                .expect("Failed to start engine");
            
            engine.shutdown().await
                .expect("Failed to shutdown engine");
        });
    });
}

/// Benchmark concurrent operations
fn benchmark_concurrent_operations(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("concurrent_operations");
    
    for concurrency in [1, 5, 10, 20].iter() {
        group.bench_with_input(
            BenchmarkId::new("concurrent_sessions", concurrency),
            concurrency,
            |b, &concurrency| {
                b.to_async(&rt).iter(|| async {
                    let config = Arc::new(Config::default());
                    let engine = Arc::new(OrchestrationEngine::new(config).await
                        .expect("Failed to create engine"));
                    
                    engine.start().await
                        .expect("Failed to start engine");
                    
                    // Create concurrent sessions
                    let mut handles = Vec::new();
                    for i in 0..concurrency {
                        let engine_clone = engine.clone();
                        let handle = tokio::spawn(async move {
                            engine_clone.create_session(
                                format!("Concurrent Session {}", i),
                                "Concurrent benchmark session".to_string(),
                            ).await.expect("Failed to create session")
                        });
                        handles.push(handle);
                    }
                    
                    // Wait for all to complete
                    let mut _session_ids = Vec::new();
                    for handle in handles {
                        _session_ids.push(black_box(
                            handle.await.expect("Failed to join task")
                        ));
                    }
                    
                    engine.shutdown().await
                        .expect("Failed to shutdown engine");
                });
            },
        );
    }
    
    group.finish();
}

/// Memory usage benchmarks
fn benchmark_memory_usage(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("memory_usage");
    
    for num_entities in [100, 500, 1000].iter() {
        group.bench_with_input(
            BenchmarkId::new("large_state", num_entities),
            num_entities,
            |b, &num_entities| {
                b.to_async(&rt).iter(|| async {
                    let config = Arc::new(Config::default());
                    let engine = OrchestrationEngine::new(config).await
                        .expect("Failed to create engine");
                    
                    engine.start().await
                        .expect("Failed to start engine");
                    
                    // Create many sessions and tasks
                    let mut session_ids = Vec::new();
                    for i in 0..num_entities {
                        let session_id = engine.create_session(
                            format!("Session {}", i),
                            "Memory benchmark session".to_string(),
                        ).await.expect("Failed to create session");
                        
                        session_ids.push(session_id);
                        
                        // Add tasks to each session
                        for j in 0..5 {
                            let task = Task::new(
                                session_id,
                                format!("Task {} - {}", i, j),
                                "Memory benchmark task".to_string(),
                            );
                            
                            let _ = engine.submit_task(session_id, task).await;
                        }
                    }
                    
                    // Perform health check to ensure everything is loaded
                    let _health = black_box(
                        engine.health_check().await
                            .expect("Failed to perform health check")
                    );
                    
                    engine.shutdown().await
                        .expect("Failed to shutdown engine");
                });
            },
        );
    }
    
    group.finish();
}

criterion_group!(
    benches,
    benchmark_task_submission,
    benchmark_session_creation,
    benchmark_engine_init,
    benchmark_concurrent_operations,
    benchmark_memory_usage
);

criterion_main!(benches);