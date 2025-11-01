from typing import Dict, Set
from uuid import UUID
import asyncio
import asyncpg
from fastapi import WebSocket


class NotificationManager:
    def __init__(self):
        self.connections: Dict[UUID, Set[WebSocket]] = {}
        self.pg_connection = None
        self.listening = False

    async def connect(self, meeting_id: UUID, websocket: WebSocket):
        await websocket.accept()
        if meeting_id not in self.connections:
            self.connections[meeting_id] = set()
        self.connections[meeting_id].add(websocket)

    def disconnect(self, meeting_id: UUID, websocket: WebSocket):
        if meeting_id in self.connections:
            self.connections[meeting_id].discard(websocket)
            if not self.connections[meeting_id]:
                del self.connections[meeting_id]

    async def broadcast(self, meeting_id: UUID, message: dict):
        if meeting_id in self.connections:
            disconnected = set()
            for websocket in self.connections[meeting_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.add(websocket)
            
            for ws in disconnected:
                self.disconnect(meeting_id, ws)

    async def start_listener(self, database_url: str):
        self.pg_connection = await asyncpg.connect(database_url)
        await self.pg_connection.add_listener("summary_update", self._handle_notification)
        self.listening = True

    async def stop_listener(self):
        if self.pg_connection:
            self.listening = False
            await self.pg_connection.remove_listener("summary_update", self._handle_notification)
            await self.pg_connection.close()

    async def _handle_notification(self, connection, pid, channel, payload):
        try:
            meeting_id = UUID(payload)
            await self.broadcast(meeting_id, {"type": "summary_update", "meeting_id": str(meeting_id)})
        except Exception as e:
            print(f"Error handling notification: {e}")


notification_manager = NotificationManager()
