"""
WebSocket alert broadcasting system
Real-time alerts for violations and vehicle alerts
"""
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json


class AlertBroadcaster:
    """
    Simple in-memory WebSocket broadcaster for real-time alerts
    For production, consider using Redis pub/sub or similar
    """
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast_violation(self, violation_data: dict):
        """
        Broadcast violation alert to all connected clients
        
        Args:
            violation_data: Dictionary containing violation details
        """
        message = {
            "type": "violation_alert",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": violation_data
        }
        await self._broadcast(message)
    
    async def broadcast_vehicle_alert(self, alert_data: dict):
        """
        Broadcast vehicle alert to all connected clients
        
        Args:
            alert_data: Dictionary containing vehicle alert details
        """
        message = {
            "type": "vehicle_alert",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": alert_data
        }
        await self._broadcast(message)
    
    async def send_heartbeat(self):
        """Send heartbeat to all connected clients"""
        message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        await self._broadcast(message)
    
    async def _broadcast(self, message: dict):
        """Internal method to send message to all active connections"""
        if not self.active_connections:
            return
        
        disconnected = set()
        message_str = json.dumps(message)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global broadcaster instance
alert_broadcaster = AlertBroadcaster()
