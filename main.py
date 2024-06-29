import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command

from aiogram.dispatcher.router import Router
from config import TOKEN, WEATHER

# Инициализация бота, диспетчера и хранилища состояний
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Определение состояний для FSM
class WeatherStates(StatesGroup):
    city = State()
    date = State()


# Функция для получения прогноза погоды
def get_weather(city: str, date: str, api_key: str):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    for forecast in data['list']:
        if date in forecast['dt_txt']:
            temperature = forecast['main']['temp']
            weather = forecast['weather'][0]['description']
            pressure = forecast['main']['pressure']
            return f"Погода в {city} на {date}:\nТемпература: {temperature}°C\nПогодные условия: {weather}\nДавление: {pressure} hPa"

    return "Не удалось найти прогноз на указанную дату."


# Обработчик команды /help
async def help_command(message: types.Message):
    await message.answer('Этот бот умеет выполнять команды:\n /start \n /help \n /weather')


# Обработчик команды /start
async def start_command(message: types.Message):
    await message.answer(
        'Привет! Я помогу тебе узнать погоду в любом регионе. Введите команду /weather, чтобы узнать погоду.')


# Обработчик команды /weather
async def weather_command(message: types.Message, state: FSMContext):
    await message.answer('В каком городе хотите узнать погоду?')
    await state.set_state(WeatherStates.city)


# Обработчик ввода города
async def get_city(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    await message.answer('На какое число? (Формат: ГГГГ-ММ-ДД)')
    await state.set_state(WeatherStates.date)


# Обработчик ввода даты
async def get_date(message: types.Message, state: FSMContext):
    date = message.text
    data = await state.get_data()
    city = data['city']
    api_key = WEATHER
    weather_info = get_weather(city, date, api_key)
    await message.answer(weather_info)
    await state.clear()


def register_handlers(dp: Dispatcher):
    dp.message.register(help_command, Command(commands=['help']))
    dp.message.register(start_command, Command(commands=['start']))
    dp.message.register(weather_command, Command(commands=['weather']))
    dp.message.register(get_city, WeatherStates.city)
    dp.message.register(get_date, WeatherStates.date)


# Основная функция запуска бота
async def main():
    register_handlers(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
