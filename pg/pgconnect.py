import asyncio
import asyncpg
from decouple import config

user = config('PG_USER')
password = config('PG_PASSWORD')
database = config('PG_DATABASE')
host = config('PG_HOST')
port = config('PG_PORT')

async def conn():
    conn = await asyncpg.connect(user=user, password=password,
                                 database=database, host=host, port=port)
    # values = await conn.fetch('''SELECT * FROM mytable''')
    await conn.close()

asyncio.run(conn())