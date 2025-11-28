import asyncio
import logging
from database.database import DatabaseService
from config import load_config

logging.basicConfig(level=logging.INFO)

async def test_db_write():
    load_config()
    db = DatabaseService(db_url="sqlite+aiosqlite:///database.db")
    await db.init_db()
    
    print("Saving test message...")
    await db.save_message("test_user_verify", "user", "Verification message")
    
    print("Retrieving history...")
    history = await db.get_conversation_history("test_user_verify")
    print(f"History: {history}")
    
    await db.dispose()

if __name__ == "__main__":
    asyncio.run(test_db_write())
