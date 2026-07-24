from fastapi import WebSocket 
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_sessions: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, channel_id: str, user_id: str):
        await websocket.accept()

        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        
        self.active_connections[channel_id].append(websocket)
        logger.info(f"New connection to channel {channel_id}. Total: {len(self.active_connections[channel_id])}")

        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = 0
        
        self.user_sessions[user_id] += 1

        is self.user_sessions[user_id] == 1:
            await self.broadcast_presence(user_id, "online")

    await def disconnect(self, websocket: WebSocket, channel_id: str, user_id: str):
        if channel_id in self.active_connections:
            if websocket in self.active_connections[channel_id]:
                self.active_connections[channel_id].remove(websocket)

            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]
            
            if user_id in self.user_sessions:
                self.user_sessions[user_id] -= 1

                if self.user_sessions[user_id] <= 0:
                    del self.user_sessions[user_id]
                    await self.broadcast_presence(user_id, "offline")

    async def broadcast_presence(self, user_id: str, status: str):
        presence_payload = {
            "type": "presence",
            "user_id": user_id,
            "status": status
        }
        for channel_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(presence_payload)
                except Exception:
                    pass
    
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
