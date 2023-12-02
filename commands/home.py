import asyncio
import json
import os
from telebot.async_telebot import *
from bs4 import BeautifulSoup
from telebot import types
from telebot import formatting as formatx
token = os.getenv("token")
bot = AsyncTeleBot(token)

async def home(call):
   keyboard = types.InlineKeyboardMarkup()
   live_button = types.InlineKeyboardButton(text=f'Live', callback_data='live now')
   recent_button = types.InlineKeyboardButton(text=f'Recent', callback_data='recent 1')
   upcoming_button = types.InlineKeyboardButton(text=f'Upcoming', callback_data='upcoming 1')
   keyboard.add(live_button,recent_button,upcoming_button)  
   await bot.edit_message_text("Cricket X",call.from_user.id,call.message.id, parse_mode="Markdown",reply_markup=keyboard)