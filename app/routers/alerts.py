from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.alert_service import alert_service

router = APIRouter(prefix="/ws", tags=["Alerts"])

@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    await alert_service.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        alert_service.disconnect(websocket)
