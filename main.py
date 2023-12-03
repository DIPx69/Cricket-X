import re
import httpx
import asyncio
import os
import commands as command
from telebot.async_telebot import *
from keep_alive import keep_alive
from telebot import types
token = os.getenv("token")
bot = AsyncTeleBot(token)
@bot.callback_query_handler(func=lambda call: True)
async def handle_callback_query(call):
   print(call.data)
   if call.data == "live now":
     await command.live_game_list(call)
   elif call.data == "home":
     await command.home(call)
   elif call.data.startswith("recent_pages"):
     page_num = int(call.data.split()[1])
     await command.page_list(call,page_num)
   elif call.data.startswith("recent"):
     page_num = int(call.data.split()[1])
     await command.recent_game(call,page_num)
   elif call.data.startswith("upcoming_pages"):
     page_num = int(call.data.split()[1])
     await command.upcoming_page_list(call,page_num)
   elif call.data.startswith("upcoming"):
     page_num = int(call.data.split()[1])
     await command.upcoming_game(call,page_num)
   elif call.data.startswith("commentary"):
     game_id = int(call.data.split()[1])
     await command.commentary(call,game_id)
   elif call.data.startswith("auto_commentary"):
     game_id = int(call.data.split()[1])
     await command.commentary(call,game_id,auto=True)
   elif call.data.startswith("load"):
     load_url = call.data.split()[1]
     msg_id = int(call.data.split()[2])
     if load_url == "No_More":
       await bot.answer_callback_query(call.id, text=f"No More Commentary", show_alert=True)
     else:
       await command.load_commentary(call,load_url,msg_id)
   elif call.data.startswith("auto_load"):
     load_url = call.data.split()[1]
     msg_id = int(call.data.split()[2])
     await command.load_commentary(call,load_url,msg_id,auto=True)
   elif call.data.startswith("game"):
     game_id = int(call.data.split()[1])
     reference = call.data.split()[2]
     if reference == "recent":
       page_number = int(call.data.split()[3])
     else:
       page_number = None
     await command.check_state(call,game_id,reference,page_number)
   elif call.data == "delete":
       await bot.delete_message(call.from_user.id,call.message.id)
   elif call.data.startswith("all_delete"):
       get_id = int(call.data.split()[1])
       tasks = [bot.delete_message(call.from_user.id,message_id) for message_id in range(get_id+1,call.message.id+1)]
       try:
         await asyncio.gather(*tasks)
       except:
         ...
@bot.message_handler(commands=['start'])
async def live_now(message):
   keyboard = types.InlineKeyboardMarkup()
   live_button = types.InlineKeyboardButton(text=f'Live', callback_data='live now')
   recent_button = types.InlineKeyboardButton(text=f'Recent', callback_data='recent 1')
   upcoming_button = types.InlineKeyboardButton(text=f'Upcoming', callback_data='upcoming 1')
   keyboard.add(live_button,recent_button,upcoming_button) 
   await bot.send_message(message.chat.id,f"Working",parse_mode="Markdown",reply_markup=keyboard)
print("Bot Is Online... [Development Branch]")
if __name__ == "__main__":
   keep_alive()
   asyncio.run(bot.polling(non_stop=True))