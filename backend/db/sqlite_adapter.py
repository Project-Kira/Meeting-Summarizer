import asyncio
import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
import json

class SQLiteRepository:
    def __init__(self, db_path: str = "meeting_summarizer.db"):
        self.db_path = db_path
        
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    finalized INTEGER DEFAULT 0,
                    finalized_at TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS segments (
                    id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    speaker TEXT NOT NULL,
                    ts TEXT NOT NULL,
                    text TEXT NOT NULL,
                    token_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    payload TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )
            """)
            
            await db.commit()

# Simple test
async def test():
    repo = SQLiteRepository()
    await repo.init_db()
    print("✓ SQLite database initialized")

if __name__ == "__main__":
    asyncio.run(test())
