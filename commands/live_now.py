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

async def live_now():
  live_games = {}
  async with httpx.AsyncClient() as client:
    response = await client.get(
        "https://m.cricbuzz.com/cricket-match/live-scores")
    html_content = response.text
  soup = BeautifulSoup(html_content, 'html.parser')
  total_live = soup.find_all('div', class_='ui-live-matches')
  total_game = len(total_live)
  main_text = f"Total Live: *{total_game}*"
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
      team_a_scores = ""
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
      team_b_scores = ""
    match_update = soup.find('div', class_='cbz-ui-status').text.strip()
    live_games[str(match_id)] = {
        "title":match_header,
        "id": match_id,
        "team_a": team_a,
        "team_a_scores": team_a_scores,
        "team_b": team_b,
        "team_b_scores": team_b_scores,
        "match_update": match_update
    }
  sorted_live_games = dict(sorted(live_games.items(), key=lambda item: item[1]['id']))
  return sorted_live_games

async def live_game_list(call):
  live_game_list = await live_now()
  text = f"*Live Now [{len(live_game_list)}]*\n\n"
  keyboard = types.InlineKeyboardMarkup(row_width=4)
  buttons = [types.InlineKeyboardButton(text=f'[{index}]', callback_data=f"game {match} live") for index,match in enumerate(live_game_list,start=1)]
  for index,match in enumerate(live_game_list,start=1):
     match_data = live_game_list[str(match)]
     text += f"*[{index}]*  {match_data['title']}\n"
     text += f"{match_data['team_a']} {match_data['team_a_scores']}\n"
     text += f"{match_data['team_b']} {match_data['team_b_scores']}\n"
     text += f"{match_data['match_update']}"
     text += "\n\n"
  #text = formatx.escape_markdown(text)
  refresh_button = types.InlineKeyboardButton(text='🔃 Refresh',callback_data="live now")
  back_button = types.InlineKeyboardButton(text='🔙 Back',callback_data="home")
  keyboard.add(*buttons)
  keyboard.add(refresh_button,back_button)
  try:
   await bot.edit_message_text(text,call.from_user.id,call.message.id, parse_mode="Markdown",reply_markup=keyboard)
  except:
   await bot.answer_callback_query(call.id, text="No Changes Has Been Made", show_alert=True)