use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Communication protocol definitions
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProtocolMessage {
    pub id: Uuid,
    pub version: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub payload: ProtocolPayload,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProtocolPayload {
    Handshake { capabilities: Vec<String> },
    Acknowledgment { message_id: Uuid },
    Error { code: u32, message: String },
}

impl ProtocolMessage {
    pub fn new(payload: ProtocolPayload) -> Self {
        ProtocolMessage {
            id: Uuid::new_v4(),
            version: "1.0.0".to_string(),
            timestamp: chrono::Utc::now(),
            payload,
        }
    }
}