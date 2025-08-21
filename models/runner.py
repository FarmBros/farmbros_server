import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

dotenv.load_dotenv()

db_user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
database = os.getenv('DB_NAME')
host = os.getenv('DB_HOST')

database_uri = f"postgresql+asyncpg://{db_user}:{password}@{host}/{database}"

engine = create_async_engine(
    database_uri,
    # echo=True,  # Set to True for debugging purposes
    future=True  # Use future mode for SQLAlchemy 2.0 compatibility
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # Prevents objects from being expired after commit
)


Base = declarative_base()

async def get_db_session():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        # Create all tables in the database
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized and tables created.")
