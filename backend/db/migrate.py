#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
from config import get_settings
import asyncpg


async def run_migrations():
    settings = get_settings()
    migrations_dir = Path(__file__).parent / "migrations"
    
    print(f"Connecting to database: {settings.database_url.split('@')[1]}")
    
    try:
        conn = await asyncpg.connect(settings.database_url)
        
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        for migration_file in migration_files:
            print(f"Running migration: {migration_file.name}")
            sql = migration_file.read_text()
            await conn.execute(sql)
            print(f"✓ {migration_file.name} completed")
        
        await conn.close()
        print("\n✓ All migrations completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_migrations())
