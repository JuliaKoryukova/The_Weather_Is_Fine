from aiogram import Router
from aiogram.types import Message

router = Router()

# Этот хэндлер будет реагировать на любые сообщения пользователя, не предусмотренные логикой бота
@router.message()
async def send_answer(message: Message):
    await message.answer('Извини, увы, это сообщение мне непонятно...')