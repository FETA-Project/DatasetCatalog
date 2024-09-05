import motor.motor_asyncio
from beanie import init_beanie

from config import config
from models import Comment, Dataset, User


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        config.DATABASE_URI
    )

    db = client[config.DATABASE_NAME]

    await init_beanie(database=client.db_name,
                      document_models=[Dataset, User, Comment])
