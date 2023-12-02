import re
import httpx
import asyncio
import json
import os
from telebot.async_telebot import *
from bs4 import BeautifulSoup
from telebot import types
from telebot import formatting as formatx
token = os.getenv("token")
bot = AsyncTeleBot(token)

async def commentary(call,game_id,auto=False):
   async with httpx.AsyncClient() as client:
    response = await client.get(f"https://m.cricbuzz.com/cricket-commentary/{game_id}")
    html_content = response.text
   keyboard = types.InlineKeyboardMarkup(row_width=4)
   soup = BeautifulSoup(html_content, 'html.parser')
   load_more_button = soup.find('button', id='loadMorePagination')
   if load_more_button == None:
    button_value = "load No_More"
    load_str = "No More Commentary"
   else:
     button_value = f"load {load_more_button.get('value')}"
     load_str = "Load More"
   comments_text = ""
   comments = soup.find_all('p', class_='commtext')
   for index,comment in enumerate(comments,start=1):
     if comment.text != "":
       txt = comment.text
       comments_text += f"*\[{index}]* {txt.replace('*','')}\n\n"
   delete_button = types.InlineKeyboardButton(text='Delete',callback_data=f"delete")
   delete_button_all = types.InlineKeyboardButton(text='Delete All',callback_data=f"all_delete {call.message.id}")
   keyboard.add(delete_button,delete_button_all)
   last_space_index = 0
   if len(comments_text) > 4095:
    last_space_index = comments_text.rfind(' ', 0, 4095)
    chunk_size = 4095
    while last_space_index != -1:
     chunk = comments_text[:last_space_index]
     sendx = await bot.send_message(call.from_user.id, f"*{chunk}*", parse_mode="Markdown", reply_markup=keyboard)
     comments_text = comments_text[last_space_index+1:]
     last_space_index = comments_text.rfind(' ', 0, chunk_size)
    if auto == False or load_str == "No More Commentary":
      load_more = types.InlineKeyboardButton(text=f'{load_str}',callback_data=f"{button_value} {call.message.id}")
      keyboard.add(load_more)
    if comments_text.isspace():
     comments_text = sendx.text
     await bot.edit_message_text(f"*{comments_text}*",call.from_user.id,sendx.message_id,parse_mode="Markdown",reply_markup=keyboard)
    else:
     await bot.send_message(call.from_user.id, f"*{comments_text}*", parse_mode="Markdown", reply_markup=keyboard)
   else:
    if auto == False or load_str == "No More Commentary":
      load_more = types.InlineKeyboardButton(text=f'{load_str}',callback_data=f"{button_value} {call.message.id}")
      keyboard.add(load_more)
    await bot.send_message(call.from_user.id, f"*{comments_text}*", parse_mode="Markdown", reply_markup=keyboard)
   print(auto)
   if load_more_button != None and auto:
     load_url = load_more_button.get('value')
     msg_id = int(call.message.id)
     await load_commentary(call,load_url,msg_id,auto=True)
async def load_commentary(call,load_url,main_message_id,auto=False,last_message={}):
   async with httpx.AsyncClient() as client:
    response = await client.get(f"https://m.cricbuzz.com{load_url}")
    html_content = response.text
   keyboard = types.InlineKeyboardMarkup(row_width=4)
   soup = BeautifulSoup(html_content, 'html.parser')
   load_more_button = soup.find('button', id='loadMorePagination')
   if load_more_button == None:
    button_value = "load No_More"
    load_str = "No More Commentary"
   else:
     button_value = f"load {load_more_button.get('value')}"
     load_str = "Load More"
   comments_text = ""
   comments = soup.find_all('p', class_='commtext')
   for index,comment in enumerate(comments,start=1):
     if comment.text != "":
       txt = comment.text
       comments_text += f"*\[{index}]* {txt.replace('*','')}\n\n"
   delete_button = types.InlineKeyboardButton(text='Delete',callback_data=f"delete")
   delete_button_all = types.InlineKeyboardButton(text='Delete All',callback_data=f"all_delete {main_message_id}")
   keyboard.add(delete_button,delete_button_all)
   last_space_index = 0
   if len(comments_text) > 4095:
    last_space_index = comments_text.rfind(' ', 0, 4095)
    chunk_size = 4095
    while last_space_index != -1:
     chunk = comments_text[:last_space_index]
     sendx = await bot.send_message(call.from_user.id, f"*{chunk}*", parse_mode="Markdown", reply_markup=keyboard)
     comments_text = comments_text[last_space_index+1:]
     last_space_index = comments_text.rfind(' ', 0, chunk_size)
    if auto == False or load_str == "No More Commentary":
      load_more = types.InlineKeyboardButton(text=f'{load_str}',callback_data=f"{button_value} {main_message_id}")
      keyboard.add(load_more)
    if comments_text.isspace():
     comments_text = sendx.text
     await bot.edit_message_text(f"D1P\n*{comments_text}*",call.from_user.id,sendx.message_id,parse_mode="Markdown",reply_markup=keyboard)
    else:
     await bot.send_message(call.from_user.id, f"*{comments_text}*", parse_mode="Markdown", reply_markup=keyboard)
   else:
    if auto == False or load_str == "No More Commentary":
      load_more = types.InlineKeyboardButton(text=f'{load_str}',callback_data=f"{button_value} {main_message_id}")
      keyboard.add(load_more)
    try:
     sendx = await bot.send_message(call.from_user.id, f"*{comments_text}*", parse_mode="Markdown", reply_markup=keyboard)
    except:
     comments_text = last_message.text
     await bot.edit_message_text(f"*{comments_text}*",call.from_user.id,last_message.message_id,parse_mode="Markdown",reply_markup=keyboard)
   if load_more_button != None and auto:
     load_url = load_more_button.get('value')
     msg_id = int(main_message_id)
     await load_commentary(call,load_url,msg_id,auto=True,last_message=sendx)