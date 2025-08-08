use std::sync::Arc;
use sqlx::{PgPool, Row};
use tracing::{info, warn, error};

use crate::config::DatabaseConfig;
use crate::error::{Result, OrchestrationError};
use crate::orchestration::{Task, Agent, OrchestrationSession, SharedContext};
use super::PersistentStorage;

/// PostgreSQL-based persistent state storage
pub struct StateStore {
    pool: PgPool,
}

impl StateStore {
    pub async fn new(config: &DatabaseConfig) -> Result<Self> {
        info!("Initializing PostgreSQL state store");
        
        let pool = PgPool::connect(&config.url).await?;
        
        // Run migrations if enabled
        if config.migrate_on_startup {
            sqlx::migrate!("./migrations").run(&pool).await?;
        }
        
        info!("State store initialized successfully");
        Ok(StateStore { pool })
    }
}

#[async_trait::async_trait]
impl PersistentStorage for StateStore {
    async fn save_task(&self, task: &Task) -> Result<()> {
        let task_json = serde_json::to_value(task)?;
        
        sqlx::query!(
            r#"
            INSERT INTO tasks (id, session_id, name, status, task_data, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) 
            DO UPDATE SET 
                status = EXCLUDED.status,
                task_data = EXCLUDED.task_data,
                updated_at = EXCLUDED.updated_at
            "#,
            task.id,
            task.session_id,
            task.name,
            serde_json::to_string(&task.status)?,
            task_json,
            task.created_at,
            chrono::Utc::now()
        )
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
    
    async fn load_task(&self, task_id: uuid::Uuid) -> Result<Option<Task>> {
        let row = sqlx::query!(
            "SELECT task_data FROM tasks WHERE id = $1",
            task_id
        )
        .fetch_optional(&self.pool)
        .await?;
        
        if let Some(row) = row {
            let task: Task = serde_json::from_value(row.task_data)?;
            Ok(Some(task))
        } else {
            Ok(None)
        }
    }
    
    async fn load_active_tasks(&self) -> Result<Vec<Task>> {
        let rows = sqlx::query!(
            r#"
            SELECT task_data FROM tasks 
            WHERE status NOT IN ('Completed', 'Failed', 'Cancelled')
            ORDER BY created_at ASC
            "#
        )
        .fetch_all(&self.pool)
        .await?;
        
        let mut tasks = Vec::new();
        for row in rows {
            match serde_json::from_value::<Task>(row.task_data) {
                Ok(task) => tasks.push(task),
                Err(e) => warn!("Failed to deserialize task: {}", e),
            }
        }
        
        Ok(tasks)
    }
    
    async fn save_agent(&self, agent: &Agent) -> Result<()> {
        let agent_json = serde_json::to_value(agent)?;
        
        sqlx::query!(
            r#"
            INSERT INTO agents (id, name, status, agent_data, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id)
            DO UPDATE SET
                status = EXCLUDED.status,
                agent_data = EXCLUDED.agent_data,
                updated_at = EXCLUDED.updated_at
            "#,
            agent.id,
            agent.name,
            serde_json::to_string(&agent.status)?,
            agent_json,
            chrono::Utc::now(),
            chrono::Utc::now()
        )
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
    
    async fn load_agent(&self, agent_id: &str) -> Result<Option<Agent>> {
        let row = sqlx::query!(
            "SELECT agent_data FROM agents WHERE id = $1",
            agent_id
        )
        .fetch_optional(&self.pool)
        .await?;
        
        if let Some(row) = row {
            let agent: Agent = serde_json::from_value(row.agent_data)?;
            Ok(Some(agent))
        } else {
            Ok(None)
        }
    }
    
    async fn load_registered_agents(&self) -> Result<Vec<Agent>> {
        let rows = sqlx::query!(
            "SELECT agent_data FROM agents ORDER BY created_at ASC"
        )
        .fetch_all(&self.pool)
        .await?;
        
        let mut agents = Vec::new();
        for row in rows {
            match serde_json::from_value::<Agent>(row.agent_data) {
                Ok(agent) => agents.push(agent),
                Err(e) => warn!("Failed to deserialize agent: {}", e),
            }
        }
        
        Ok(agents)
    }
    
    async fn save_session(&self, session: &OrchestrationSession) -> Result<()> {
        let session_json = serde_json::to_value(session)?;
        
        sqlx::query!(
            r#"
            INSERT INTO sessions (id, name, status, session_data, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id)
            DO UPDATE SET
                status = EXCLUDED.status,
                session_data = EXCLUDED.session_data,
                updated_at = EXCLUDED.updated_at
            "#,
            session.id,
            session.name,
            serde_json::to_string(&session.status)?,
            session_json,
            session.created_at,
            chrono::Utc::now()
        )
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
    
    async fn load_session(&self, session_id: uuid::Uuid) -> Result<Option<OrchestrationSession>> {
        let row = sqlx::query!(
            "SELECT session_data FROM sessions WHERE id = $1",
            session_id
        )
        .fetch_optional(&self.pool)
        .await?;
        
        if let Some(row) = row {
            let session: OrchestrationSession = serde_json::from_value(row.session_data)?;
            Ok(Some(session))
        } else {
            Ok(None)
        }
    }
    
    async fn load_active_sessions(&self) -> Result<Vec<OrchestrationSession>> {
        let rows = sqlx::query!(
            r#"
            SELECT session_data FROM sessions 
            WHERE status IN ('Active', 'Paused')
            ORDER BY created_at ASC
            "#
        )
        .fetch_all(&self.pool)
        .await?;
        
        let mut sessions = Vec::new();
        for row in rows {
            match serde_json::from_value::<OrchestrationSession>(row.session_data) {
                Ok(session) => sessions.push(session),
                Err(e) => warn!("Failed to deserialize session: {}", e),
            }
        }
        
        Ok(sessions)
    }
    
    async fn save_context(&self, context: &SharedContext) -> Result<()> {
        let context_json = serde_json::to_value(context)?;
        
        sqlx::query!(
            r#"
            INSERT INTO contexts (id, session_id, name, version, context_data, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id)
            DO UPDATE SET
                version = EXCLUDED.version,
                context_data = EXCLUDED.context_data,
                updated_at = EXCLUDED.updated_at
            "#,
            context.id,
            context.session_id,
            context.name,
            context.version as i64,
            context_json,
            context.created_at,
            context.updated_at
        )
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
    
    async fn load_context(&self, context_id: uuid::Uuid) -> Result<Option<SharedContext>> {
        let row = sqlx::query!(
            "SELECT context_data FROM contexts WHERE id = $1",
            context_id
        )
        .fetch_optional(&self.pool)
        .await?;
        
        if let Some(row) = row {
            let context: SharedContext = serde_json::from_value(row.context_data)?;
            Ok(Some(context))
        } else {
            Ok(None)
        }
    }
    
    async fn load_contexts(&self) -> Result<Vec<SharedContext>> {
        let rows = sqlx::query!(
            "SELECT context_data FROM contexts ORDER BY created_at ASC"
        )
        .fetch_all(&self.pool)
        .await?;
        
        let mut contexts = Vec::new();
        for row in rows {
            match serde_json::from_value::<SharedContext>(row.context_data) {
                Ok(context) => contexts.push(context),
                Err(e) => warn!("Failed to deserialize context: {}", e),
            }
        }
        
        Ok(contexts)
    }
    
    async fn is_healthy(&self) -> bool {
        match sqlx::query("SELECT 1").fetch_one(&self.pool).await {
            Ok(_) => true,
            Err(e) => {
                error!("Database health check failed: {}", e);
                false
            }
        }
    }
}