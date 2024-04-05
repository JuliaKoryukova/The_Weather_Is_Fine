import math
import datetime
from datetime import timezone, timedelta
import requests
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from lexicon.lexicon import code_to_smile
from config_data.config import load_config


router = Router()
conf = load_config()
# Инициализируем хранилище
storage = MemoryStorage()

class FSMFillForm(StatesGroup):
    fill_city = State() # Состояние ожидания ввода города

# Этот хэндлер будет реагировать на '/start'
@router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message, state: FSMContext):
    await message.reply('Привет! Напиши мне название города и я пришлю сводку погоды')
    # Устанавливаем состояние ожидания ввода названия города
    await state.set_state(FSMFillForm.fill_city)

# Этот хэндлер будет реагировать на сообщение с названием города и проверять на корректность
@router.message(StateFilter(FSMFillForm.fill_city), F.text.isalpha())
async def get_weather(message: Message, state: FSMContext):

    url = 'https://api.openweathermap.org/data/2.5/weather?q='+message.text+'&units=metric&lang=ru&appid='+ conf.tg_bot.token_weather
    data = requests.get(url).json()
    city = data['name']
    time_zone = data['timezone']
    tz = timezone(timedelta(seconds=time_zone))
    cur_temp = round(data['main']['temp'])
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind = data['wind']['speed']

    sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
    sunrise_str = sunrise.strftime("%H:%M")
    sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
    sunset_str = sunset.strftime("%H:%M")

    length_of_the_day = sunset - sunrise

    length_of_the_day_hours = length_of_the_day.seconds // 3600
    length_of_the_day_minutes = (length_of_the_day.seconds // 60) % 60

    length_of_the_day_str = "{} ч {} м".format(length_of_the_day_hours, length_of_the_day_minutes)

    # Получаем значение погоды
    weather_description = data['weather'][0]['main']

    if weather_description in code_to_smile:
        wd = code_to_smile[weather_description]
    else:
        wd = 'Посмотри в окно, я не понимаю, что там за погода...'

    await message.reply(f'{datetime.datetime.now(tz).strftime('%Y-%m-%d')}\n'
    f'Местное время {datetime.datetime.now(tz).strftime('%H:%M')}\n'
    f'Температура: {cur_temp}°C {wd}\n'
    f'Влажность: {humidity}%\nДавление: {math.ceil(pressure/1.333)} мм.рт.ст\nВетер: {wind} м/с \n'
    f'Восход солнца: {sunrise_str}\nЗакат солнца: {sunset_str}\nПродолжительность дня: {length_of_the_day_str}\n\n'
    f'Хорошего дня!'
    )
    #await state.clear()
