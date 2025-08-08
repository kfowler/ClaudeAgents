use std::sync::Arc;
use axum::extract::ws::{WebSocket, Message};
use futures::{sink::SinkExt, stream::StreamExt};
use tokio::sync::broadcast;
use tracing::{info, warn, error};

use crate::error::Result;
use super::RealtimeEvent;

/// Handles WebSocket connections for real-time updates
pub struct WebSocketHandler {
    event_broadcaster: broadcast::Sender<RealtimeEvent>,
}

impl WebSocketHandler {
    pub fn new() -> Self {
        let (event_broadcaster, _) = broadcast::channel(1000);
        
        WebSocketHandler {
            event_broadcaster,
        }
    }
    
    pub async fn handle_socket(&self, socket: WebSocket) {
        info!("New WebSocket connection established");
        
        let mut event_receiver = self.event_broadcaster.subscribe();
        let (mut sender, mut receiver) = socket.split();
        
        // Spawn task to handle incoming messages
        let incoming_task = tokio::spawn(async move {
            while let Some(msg) = receiver.next().await {
                match msg {
                    Ok(Message::Text(text)) => {
                        info!("Received WebSocket message: {}", text);
                    }
                    Ok(Message::Close(_)) => {
                        info!("WebSocket connection closed");
                        break;
                    }
                    Err(e) => {
                        error!("WebSocket error: {}", e);
                        break;
                    }
                    _ => {}
                }
            }
        });
        
        // Handle outgoing events
        while let Ok(event) = event_receiver.recv().await {
            if let Ok(event_json) = serde_json::to_string(&event) {
                if sender.send(Message::Text(event_json)).await.is_err() {
                    warn!("Failed to send WebSocket message");
                    break;
                }
            }
        }
        
        incoming_task.abort();
        info!("WebSocket connection handler finished");
    }
    
    pub async fn broadcast_event(&self, event: RealtimeEvent) -> Result<()> {
        let _ = self.event_broadcaster.send(event);
        Ok(())
    }
}