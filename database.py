import asyncio
from models import runner


# Initialize the database
if __name__ == "__main__":
    asyncio.run(runner.init_db())
    print("Database setup complete.")