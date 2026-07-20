from fastapi import WebSocket 
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: str):
        await websocket.accept()

        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        
        self.active_connections[channel_id].append(websocket)
        logger.info(f"New connection to channel {channel_id}. Total: {len(self.active_connections[channel_id])}")

    def disconnect(self, websocket: WebSocket, channel_id: str):
        if channel_id in self.active_connections:
            self.active_connections[channel_id].remove(websocket)

            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]
    
    async def broadcast_to_channel(self, channel_id: str, message: dict):
        """
        Pushes a JSON message to all users connected to a specific channel.
        """
        if channel_id in self.active_connections:
            for connection in self.active_connections[channel_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f'Failed to send message to a client: {e}')
                    self.disconnect(connection, channel_id)

manager = ConnectionManager()
