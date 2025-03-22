import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from decouple import config
from aiogram.fsm.storage.redis import RedisStorage
from handlers import player
redis_url = config('127.0.0.1')
storage = RedisStorage.from_url(redis_url)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config('BOT_API'))
# Диспетчер
dp = Dispatcher(bot=bot, storage=storage)
dp.include_routers(player.router)
# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())