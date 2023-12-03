import re
import httpx
import asyncio
import json
import os
import aiofiles
import time
from telebot.async_telebot import *
from bs4 import BeautifulSoup
from telebot import types
from telebot import formatting as formatx
token = os.getenv("token")
bot = AsyncTeleBot(token)

async def recent_matches():
  filename = f'time.json'
  async with aiofiles.open(filename, 'r') as f:
   times = json.loads(await f.read())
  last_backup_time = times['recent']
  current_time = int(time.time())
  difference_time = current_time-last_backup_time
  if difference_time <= 720:
     filename = f'backup/recent.json'
     async with aiofiles.open(filename, 'r') as f:
       recent_json = json.loads(await f.read())
     return recent_json
  else:
    matches = {}
    async with httpx.AsyncClient() as client:
      response = await client.get(
        "https://m.cricbuzz.com/cricket-match/live-scores/recent-matches")
      html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    total_live = soup.find_all('div', class_='ui-live-matches')
    total_game = len(total_live)
    main_text = f"Total Recent Game: *{total_game}*"
    for games in range(total_game):
      soup = BeautifulSoup(str(total_live[games]), 'html.parser')
      match_id = soup.select_one('a.btn')['href'].split('/')[2]
      match_header = soup.find('div', class_='matchheader').text.strip()
      try:
        team_a = soup.select_one(
          '.ui-bat-team-scores .cb-ovr-flo.dis-inline:first-child').text.strip(
          )
      except:
        team_a = soup.find_all('div', class_='ui-bat-team-scores')[0].text
      try:
        team_a_scores = soup.select_one(
          '.ui-bat-team-scores .cb-ovr-flo.dis-inline:not(:first-child)'
      ).text.strip()
      except:
        team_a_scores = "0/0"
      try:
        team_b = soup.select_one(
          '.ui-bowl-team-scores .cb-ovr-flo.dis-inline:first-child'
      ).text.strip()
      except:
        team_b = soup.find_all('div', class_='ui-bat-team-scores')[1].text
      try:
        team_b_scores = soup.select_one(
          '.ui-bowl-team-scores .cb-ovr-flo.dis-inline:not(:first-child)'
      ).text.strip()
      except:
        team_b_scores = "0/0"
      match_update = soup.find('div', class_='cbz-ui-status').text.strip()
      matches[str(match_id)] = {
        "title":match_header,
        "id": match_id,
        "team_a": team_a,
        "team_a_scores": team_a_scores,
        "team_b": team_b,
        "team_b_scores": team_b_scores,
        "match_update": match_update
    }
  #sorted_recent_matches = dict(sorted(recent_matches.items(), key=lambda item: item[1]['id'],reverse=True))
  async with aiofiles.open("time.json", 'w') as f:
     times['recent'] = int(time.time())
     await f.write(json.dumps(times))
  async with aiofiles.open("backup/recent.json", 'w') as f:
     await f.write(json.dumps(matches))
  return matches

async def page_list(call,total_page:int,current_page_number:int):
   keyboard = types.InlineKeyboardMarkup(row_width=4)
   pages = [types.InlineKeyboardButton(text=f"{i}", callback_data=f"recent {i}") for i in range(1,total_page+1)]
   keyboard.add(*pages)
   back = types.InlineKeyboardButton(text='🔙 Back', callback_data=f'recent {current_page_number}')
   keyboard.add(back)
   await bot.edit_message_text(f"Select Your Page Number",call.json["message"]['chat']['id'],call.json["message"]["message_id"],parse_mode="Markdown",reply_markup=keyboard)

async def recent_game(call,page_number):
   item_per_page = 10
   keyboard = types.InlineKeyboardMarkup(row_width=4)
   data = await recent_matches()
   list_data = list(data)
   game_data = {}
   for page_num, start_index in enumerate(range(0, len(list_data),item_per_page), start=1):
     page = list_data[start_index:start_index + item_per_page]
     game_data[str(page_num)] = page 
   total_page = len(game_data)
   page_data = game_data[str(page_number)]
   text = f"*Recent Games [{len(list_data)}]*\n\n"
   buttons = [types.InlineKeyboardButton(text=f'[{index+(page_number*item_per_page)-item_per_page}]', callback_data=f"game {match} recent {page_number}") for index,match in enumerate(page_data,start=1)]
   for index,match in enumerate(page_data,start=1):
     match_data = data[str(match)]
     text += f"*[{index+(page_number*item_per_page)-item_per_page}]*  {match_data['title']}\n"
     text += f"{match_data['team_a']} {match_data['team_a_scores']}\n"
     text += f"{match_data['team_b']} {match_data['team_b_scores']}\n"
     text += f"{match_data['match_update']}"
     text += "\n\n"
   if page_number != total_page:
     next_emoji = "⏭️"
   else:
     next_emoji = ""
   if page_number != 1:
     prev_emoji = "⏮️"
   else:
     prev_emoji = ""
   keyboard.add(*buttons)
   next_button = types.InlineKeyboardButton(text=f'{next_emoji}',callback_data=f'recent {page_number+1}')
   prev_button = types.InlineKeyboardButton(text=f'{prev_emoji}',callback_data=f'recent {page_number-1}')
   home_button = types.InlineKeyboardButton(text=f'🔙 Back',callback_data=f'home')
   switch_page_button = types.InlineKeyboardButton(text=f'{page_number}/{total_page}',callback_data=f'recent_pages {total_page} {page_number}')
   keyboard.add(prev_button,switch_page_button,next_button)
   keyboard.add(home_button)
   await bot.edit_message_text(text,call.from_user.id,call.message.id, parse_mode="Markdown",reply_markup=keyboard)