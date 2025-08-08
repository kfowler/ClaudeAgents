use std::sync::Arc;
use std::collections::HashMap;
use std::path::Path;
use tokio::fs;
use serde_yaml;
use serde::{Deserialize, Serialize};
use tracing::{info, warn, error, debug};

use crate::error::{Result, OrchestrationError};
use crate::orchestration::{Agent, AgentId, AgentStatus, AgentMetrics, HealthStatus};

/// Adapter to integrate existing Claude agent definitions
pub struct ClaudeAgentAdapter {
    agents_directory: String,
    cached_agents: Arc<tokio::sync::RwLock<HashMap<AgentId, Agent>>>,
}

/// Claude agent definition from YAML frontmatter
#[derive(Debug, Clone, Serialize, Deserialize)]
struct ClaudeAgentDefinition {
    pub name: String,
    pub description: String,
    pub color: Option<String>,
    pub capabilities: Option<Vec<String>>,
    pub specializations: Option<Vec<String>>,
    pub tier: Option<u8>,
    pub keywords: Option<Vec<String>>,
    pub auto_select_conditions: Option<Vec<String>>,
    pub required_with: Option<Vec<String>>,
    pub conflicts_with: Option<Vec<String>>,
    pub max_concurrent_tasks: Option<usize>,
}

/// YAML frontmatter parser
#[derive(Debug, Clone, Serialize, Deserialize)]
struct AgentMarkdownFile {
    #[serde(flatten)]
    pub frontmatter: ClaudeAgentDefinition,
    pub content: Option<String>,
}

impl ClaudeAgentAdapter {
    pub fn new(agents_directory: String) -> Self {
        ClaudeAgentAdapter {
            agents_directory,
            cached_agents: Arc::new(tokio::sync::RwLock::new(HashMap::new())),
        }
    }
    
    /// Load all Claude agents from the agents directory
    pub async fn load_agents(&self) -> Result<Vec<Agent>> {
        info!("Loading Claude agents from: {}", self.agents_directory);
        
        let agents_path = Path::new(&self.agents_directory);
        if !agents_path.exists() {
            return Err(OrchestrationError::Agent(
                format!("Agents directory not found: {}", self.agents_directory)
            ));
        }
        
        let mut agents = Vec::new();
        let mut dir_entries = fs::read_dir(&agents_path).await?;
        
        while let Some(entry) = dir_entries.next_entry().await? {
            let path = entry.path();
            
            // Only process .md files
            if path.extension().and_then(|s| s.to_str()) == Some("md") {
                match self.load_agent_from_file(&path).await {
                    Ok(agent) => {
                        agents.push(agent);
                    }
                    Err(e) => {
                        warn!("Failed to load agent from {:?}: {}", path, e);
                    }
                }
            }
        }
        
        // Update cache
        {
            let mut cache = self.cached_agents.write().await;
            cache.clear();
            for agent in &agents {
                cache.insert(agent.id.clone(), agent.clone());
            }
        }
        
        info!("Loaded {} Claude agents", agents.len());
        Ok(agents)
    }
    
    /// Load a specific agent by ID
    pub async fn get_agent(&self, agent_id: &AgentId) -> Result<Option<Agent>> {
        // Check cache first
        {
            let cache = self.cached_agents.read().await;
            if let Some(agent) = cache.get(agent_id) {
                return Ok(Some(agent.clone()));
            }
        }
        
        // Try to load from file if not in cache
        let agent_file = format!("{}/{}.md", self.agents_directory, agent_id);
        if Path::new(&agent_file).exists() {
            match self.load_agent_from_file(Path::new(&agent_file)).await {
                Ok(agent) => {
                    // Update cache
                    {
                        let mut cache = self.cached_agents.write().await;
                        cache.insert(agent_id.clone(), agent.clone());
                    }
                    Ok(Some(agent))
                }
                Err(e) => {
                    warn!("Failed to load agent {}: {}", agent_id, e);
                    Ok(None)
                }
            }
        } else {
            Ok(None)
        }
    }
    
    /// Refresh agent cache by reloading from disk
    pub async fn refresh_cache(&self) -> Result<()> {
        debug!("Refreshing Claude agents cache");
        self.load_agents().await?;
        Ok(())
    }
    
    /// Get agent selection recommendations based on task requirements
    pub async fn recommend_agents(
        &self,
        task_description: &str,
        required_capabilities: &[String],
        excluded_agents: &[AgentId],
    ) -> Result<Vec<(AgentId, f32)>> {
        let cache = self.cached_agents.read().await;
        let mut recommendations = Vec::new();
        
        for (agent_id, agent) in cache.iter() {
            if excluded_agents.contains(agent_id) {
                continue;
            }
            
            let score = self.calculate_agent_match_score(
                agent,
                task_description,
                required_capabilities,
            );
            
            if score > 0.3 { // Minimum threshold
                recommendations.push((agent_id.clone(), score));
            }
        }
        
        // Sort by score (descending)
        recommendations.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        
        Ok(recommendations)
    }
    
    /// Get agents by tier (for progressive disclosure)
    pub async fn get_agents_by_tier(&self, tier: u8) -> Result<Vec<Agent>> {
        let cache = self.cached_agents.read().await;
        let agents: Vec<Agent> = cache
            .values()
            .filter(|agent| {
                // Extract tier from configuration or default to tier 2
                self.get_agent_tier(agent) == tier
            })
            .cloned()
            .collect();
        
        Ok(agents)
    }
    
    /// Check if agents conflict with each other
    pub async fn check_agent_conflicts(&self, agent_ids: &[AgentId]) -> Result<Vec<(AgentId, AgentId)>> {
        let cache = self.cached_agents.read().await;
        let mut conflicts = Vec::new();
        
        for i in 0..agent_ids.len() {
            for j in (i + 1)..agent_ids.len() {
                let agent_a = &agent_ids[i];
                let agent_b = &agent_ids[j];
                
                if let (Some(a), Some(b)) = (cache.get(agent_a), cache.get(agent_b)) {
                    if self.agents_conflict(a, b) {
                        conflicts.push((agent_a.clone(), agent_b.clone()));
                    }
                }
            }
        }
        
        Ok(conflicts)
    }
    
    // Private helper methods
    
    async fn load_agent_from_file(&self, path: &Path) -> Result<Agent> {
        let content = fs::read_to_string(path).await?;
        
        // Split frontmatter and content
        let (frontmatter, markdown_content) = self.parse_markdown_with_frontmatter(&content)?;
        
        // Parse YAML frontmatter
        let agent_def: ClaudeAgentDefinition = serde_yaml::from_str(&frontmatter)?;
        
        // Extract agent ID from filename
        let agent_id = path.file_stem()
            .and_then(|s| s.to_str())
            .ok_or_else(|| OrchestrationError::Agent("Invalid filename".to_string()))?
            .to_string();
        
        // Convert to orchestration Agent
        let agent = self.convert_to_orchestration_agent(agent_id, agent_def, markdown_content)?;
        
        debug!("Loaded agent: {}", agent.name);
        Ok(agent)
    }
    
    fn parse_markdown_with_frontmatter(&self, content: &str) -> Result<(String, String)> {
        let lines: Vec<&str> = content.lines().collect();
        
        if lines.len() < 3 || lines[0] != "---" {
            return Err(OrchestrationError::Agent("No YAML frontmatter found".to_string()));
        }
        
        // Find the end of frontmatter
        let mut frontmatter_end = 0;
        for (i, line) in lines.iter().enumerate().skip(1) {
            if *line == "---" {
                frontmatter_end = i;
                break;
            }
        }
        
        if frontmatter_end == 0 {
            return Err(OrchestrationError::Agent("Invalid frontmatter format".to_string()));
        }
        
        let frontmatter = lines[1..frontmatter_end].join("\n");
        let markdown_content = if frontmatter_end + 1 < lines.len() {
            lines[(frontmatter_end + 1)..].join("\n")
        } else {
            String::new()
        };
        
        Ok((frontmatter, markdown_content))
    }
    
    fn convert_to_orchestration_agent(
        &self,
        agent_id: AgentId,
        def: ClaudeAgentDefinition,
        content: String,
    ) -> Result<Agent> {
        let now = chrono::Utc::now();
        
        // Build configuration from agent definition
        let mut configuration = HashMap::new();
        configuration.insert("tier".to_string(), serde_json::json!(def.tier.unwrap_or(2)));
        configuration.insert("color".to_string(), serde_json::json!(def.color.unwrap_or_default()));
        configuration.insert("keywords".to_string(), serde_json::json!(def.keywords.unwrap_or_default()));
        configuration.insert("auto_select_conditions".to_string(), serde_json::json!(def.auto_select_conditions.unwrap_or_default()));
        configuration.insert("required_with".to_string(), serde_json::json!(def.required_with.unwrap_or_default()));
        configuration.insert("conflicts_with".to_string(), serde_json::json!(def.conflicts_with.unwrap_or_default()));
        configuration.insert("content".to_string(), serde_json::json!(content));
        
        let agent = Agent {
            id: agent_id.clone(),
            name: def.name,
            description: def.description,
            capabilities: def.capabilities.unwrap_or_default(),
            specializations: def.specializations.unwrap_or_default(),
            status: AgentStatus::Available,
            current_load: 0.0,
            max_concurrent_tasks: def.max_concurrent_tasks.unwrap_or(1),
            active_tasks: Vec::new(),
            performance_metrics: AgentMetrics {
                tasks_completed: 0,
                tasks_failed: 0,
                average_execution_time_ms: 0.0,
                success_rate: 1.0,
                tokens_processed: 0,
                uptime_hours: 0.0,
                error_rate: 0.0,
                quality_score: 1.0,
            },
            health: HealthStatus {
                is_healthy: true,
                last_check: now,
                response_time_ms: None,
                error_count: 0,
                warnings: Vec::new(),
                details: HashMap::new(),
            },
            configuration,
            last_heartbeat: now,
            version: "1.0.0".to_string(),
        };
        
        Ok(agent)
    }
    
    fn calculate_agent_match_score(
        &self,
        agent: &Agent,
        task_description: &str,
        required_capabilities: &[String],
    ) -> f32 {
        let mut score = 0.0;
        
        // Capability matching (40% weight)
        if !required_capabilities.is_empty() {
            let matching_capabilities = required_capabilities
                .iter()
                .filter(|cap| agent.capabilities.contains(cap))
                .count();
            
            let capability_score = matching_capabilities as f32 / required_capabilities.len() as f32;
            score += capability_score * 0.4;
        } else {
            score += 0.4; // No specific requirements
        }
        
        // Keyword matching (30% weight)
        if let Some(keywords) = agent.configuration.get("keywords") {
            if let Some(keywords_array) = keywords.as_array() {
                let task_lower = task_description.to_lowercase();
                let matching_keywords = keywords_array
                    .iter()
                    .filter_map(|k| k.as_str())
                    .filter(|keyword| task_lower.contains(&keyword.to_lowercase()))
                    .count();
                
                if keywords_array.len() > 0 {
                    let keyword_score = matching_keywords as f32 / keywords_array.len() as f32;
                    score += keyword_score * 0.3;
                }
            }
        }
        
        // Specialization matching (20% weight)
        let task_lower = task_description.to_lowercase();
        let matching_specializations = agent.specializations
            .iter()
            .filter(|spec| task_lower.contains(&spec.to_lowercase()))
            .count();
        
        if !agent.specializations.is_empty() {
            let specialization_score = matching_specializations as f32 / agent.specializations.len() as f32;
            score += specialization_score * 0.2;
        }
        
        // Performance bonus (10% weight)
        let performance_bonus = agent.performance_metrics.success_rate * 0.1;
        score += performance_bonus;
        
        score.min(1.0)
    }
    
    fn get_agent_tier(&self, agent: &Agent) -> u8 {
        agent.configuration
            .get("tier")
            .and_then(|t| t.as_u64())
            .unwrap_or(2) as u8
    }
    
    fn agents_conflict(&self, agent_a: &Agent, agent_b: &Agent) -> bool {
        // Check conflicts_with configuration
        if let Some(conflicts) = agent_a.configuration.get("conflicts_with") {
            if let Some(conflicts_array) = conflicts.as_array() {
                for conflict in conflicts_array {
                    if let Some(conflict_str) = conflict.as_str() {
                        if conflict_str == agent_b.id || conflict_str == agent_b.name {
                            return true;
                        }
                    }
                }
            }
        }
        
        // Check reverse conflict
        if let Some(conflicts) = agent_b.configuration.get("conflicts_with") {
            if let Some(conflicts_array) = conflicts.as_array() {
                for conflict in conflicts_array {
                    if let Some(conflict_str) = conflict.as_str() {
                        if conflict_str == agent_a.id || conflict_str == agent_a.name {
                            return true;
                        }
                    }
                }
            }
        }
        
        // Known conflict patterns (from the existing agent system)
        let conflicting_pairs = vec![
            ("full-stack-architect", "mobile-developer"),
            ("systems-engineer", "web-developer"),
        ];
        
        for (a, b) in conflicting_pairs {
            if (agent_a.id == a && agent_b.id == b) || (agent_a.id == b && agent_b.id == a) {
                return true;
            }
        }
        
        false
    }
}

/// Integration tests for Claude agent adapter
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    use std::fs;
    
    #[tokio::test]
    async fn test_load_agent_from_markdown() {
        let temp_dir = TempDir::new().unwrap();
        let agents_path = temp_dir.path().to_str().unwrap().to_string();
        
        // Create a test agent file
        let agent_content = r#"---
name: Test Agent
description: A test agent for testing
color: blue
capabilities:
  - test-capability
  - another-capability
specializations:
  - testing
tier: 1
keywords:
  - test
  - example
max_concurrent_tasks: 3
---

# Test Agent

This is a test agent for demonstration purposes.

The agent specializes in testing and provides example functionality.
"#;
        
        let agent_file = temp_dir.path().join("test-agent.md");
        fs::write(&agent_file, agent_content).unwrap();
        
        let adapter = ClaudeAgentAdapter::new(agents_path);
        let agents = adapter.load_agents().await.unwrap();
        
        assert_eq!(agents.len(), 1);
        
        let agent = &agents[0];
        assert_eq!(agent.id, "test-agent");
        assert_eq!(agent.name, "Test Agent");
        assert_eq!(agent.description, "A test agent for testing");
        assert_eq!(agent.capabilities, vec!["test-capability", "another-capability"]);
        assert_eq!(agent.specializations, vec!["testing"]);
        assert_eq!(agent.max_concurrent_tasks, 3);
    }
    
    #[tokio::test]
    async fn test_agent_recommendation() {
        let temp_dir = TempDir::new().unwrap();
        let agents_path = temp_dir.path().to_str().unwrap().to_string();
        
        // Create multiple test agents
        let agents_data = vec![
            ("web-dev", "Web Developer", vec!["html", "css", "javascript"], vec!["frontend"]),
            ("backend-dev", "Backend Developer", vec!["api", "database"], vec!["backend"]),
            ("full-stack", "Full Stack Developer", vec!["html", "css", "javascript", "api", "database"], vec!["frontend", "backend"]),
        ];
        
        for (id, name, capabilities, specializations) in agents_data {
            let content = format!(r#"---
name: {}
description: A {} agent
capabilities: {:?}
specializations: {:?}
---

# {}
"#, name, name, capabilities, specializations, name);
            
            let agent_file = temp_dir.path().join(format!("{}.md", id));
            fs::write(agent_file, content).unwrap();
        }
        
        let adapter = ClaudeAgentAdapter::new(agents_path);
        adapter.load_agents().await.unwrap();
        
        // Test recommendation for frontend task
        let recommendations = adapter.recommend_agents(
            "build a responsive web interface",
            &vec!["html".to_string(), "css".to_string()],
            &vec![]
        ).await.unwrap();
        
        assert!(!recommendations.is_empty());
        
        // Full stack should have highest score
        let (best_agent, _score) = &recommendations[0];
        assert_eq!(best_agent, "full-stack");
    }
}