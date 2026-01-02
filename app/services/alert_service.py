import json
from datetime import datetime
from typing import Set
from fastapi import WebSocket

class AlertService:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast_violation(self, violation_data: dict):
        message = {
            "type": "violation_alert",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": violation_data
        }
        await self._broadcast(message)
    
    async def broadcast_vehicle_alert(self, alert_data: dict):
        message = {
            "type": "vehicle_alert",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": alert_data
        }
        await self._broadcast(message)
    
    async def _broadcast(self, message: dict):
        if not self.active_connections: return
        disconnected = set()
        msg_str = json.dumps(message)
        for conn in self.active_connections:
            try:
                await conn.send_text(msg_str)
            except Exception:
                disconnected.add(conn)
        for conn in disconnected:
            self.disconnect(conn)

alert_service = AlertService()
