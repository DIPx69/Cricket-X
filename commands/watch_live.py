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

async def check_state(call,game_id,reference,page_number=None):
   async with httpx.AsyncClient() as client:
    response = await client.get(f"https://m.cricbuzz.com/cricket-commentary/{game_id}")
    html_content = response.text
   soup = BeautifulSoup(html_content, 'html.parser')
   data_tag = soup.find('script', string=re.compile('var matchState'))
   script_content = data_tag.string
   match_state = re.search(r"var matchState = '(.+?)';", script_content).group(1)
   match_id = re.search(r"var matchId = '(.+?)';", script_content).group(1)
   series_id = re.search(r"var seriesId = '(.+?)';", script_content).group(1)
   if match_state == "inprogress":
     await inprogress(call,html_content,reference,page_number)
   elif match_state == "complete":
     await complete(call,html_content,reference,page_number)
   else:
     print(match_state)
async def complete(call,html,reference,page_number=None):
   keyboard = types.InlineKeyboardMarkup(row_width=4)
   soup = BeautifulSoup(html, 'html.parser')
   data_tag = soup.find('script', string=re.compile('var matchState'))
   match_id = re.search(r"var matchId = '(.+?)';", data_tag.string).group(1)
   update = soup.find('div', class_='cbz-ui-status').text
   match_name  = soup.find('h4', class_='cb-list-item ui-header ui-branding-header').text
   bowl_team = soup.find('span', class_='ui-allscores ui-bowl-team-scores').text
   bat_team = soup.find('span', class_='ui-allscores ui-bat-team-scores').text
   player_of_the_match = soup.find('a', href=lambda href: href and href.startswith('/cricket-stats/player/')).text
   if "*" in player_of_the_match:
     player_of_the_match = "Doesn't Exist"
   crr = soup.find('span', class_='crr').text
   header = match_name.split(",")
   text = f"*{header[0]}* ||*{header[1]}*\n\n*{update}*\n\n{bat_team}\n{bowl_team}\n\n*{crr}*\n\nPlayer Of The Match: *{player_of_the_match}*\n"
   if reference == "live":
     data = "live now"
   else:
     data = f"recent {page_number}"
   back_button = types.InlineKeyboardButton(text='🔙 Back',callback_data=data)
   commentary_button = types.InlineKeyboardButton(text='Commentary',callback_data=f"commentary {match_id}")
   auto_commentary_button = types.InlineKeyboardButton(text='Auto Commentary',callback_data=f"auto_commentary {match_id}")
   keyboard.add(commentary_button,back_button)
   keyboard.add(auto_commentary_button)
   await bot.edit_message_text(text,call.from_user.id,call.message.id, parse_mode="Markdown",reply_markup=keyboard)
async def inprogress(call,html,reference,page_number=None):
   keyboard = types.InlineKeyboardMarkup(row_width=4)
   soup = BeautifulSoup(html, 'html.parser')
   data_tag = soup.find('script', string=re.compile('var matchState'))
   script_content = data_tag.string
   match_id = re.search(r"var matchId = '(.+?)';", script_content).group(1)
   update = soup.find('div', class_='cbz-ui-status').text
   update_v2 = update.split("-")
   mini_data = soup.find('div', class_="cb-list-item miniscore-data ui-branding-style ui-branding-style-partner")
   partnership_text = mini_data.find('span', string=re.compile("Partnership")).next_sibling
   last_wkt = mini_data.find('span', string=re.compile("Last wkt"))
   if last_wkt is not None:
     last_wkt = last_wkt.next_sibling.text
   else:
     last_wkt = ""
   recent_ball = mini_data.find('span', string=re.compile("Recent")).next_sibling
   if len(update_v2) > 1:
     score_update = f"\n{update_v2[1].strip()}"
   else:
     score_update = ''
   match_name  = soup.find('h4', class_='cb-list-item ui-header ui-branding-header').text
   crr = soup.find('span', class_='crr').text
   bowl_team = soup.find('span', class_='teamscores ui-bowl-team-scores')
   if bowl_team is None:
     bowl_team = ""
   else:
     bowl_team = bowl_team.text
   bat_team = soup.find('span', class_='miniscore-teams ui-bat-team-scores')
   if bat_team is None:
     bat_team = ""
   else:
     bat_team = bat_team.text
   if reference == "live":
     data = "live now"
   else:
     data = f"recent {page_number}"
   comments = soup.find_all('p', class_='commtext')
   comments_text = ""
   for comment in comments[0:8]:
     if comment.text != "":
       txt = comment.text
       comments_text += f"- *{txt.replace('*','')}*\n"
   back_button = types.InlineKeyboardButton(text='🔙 Back',callback_data=data)
   refresh_button = types.InlineKeyboardButton(text='🔃 Refresh',callback_data=f"game {match_id} live")
   keyboard.add(refresh_button,back_button)
   header = match_name.split(",")
   text = f"*{header[0]}* || *{header[1]}*\n{update}\n\n*{bat_team}*\n{bowl_team}\n*{score_update}*\n*{crr}*\n\nRecent Ball: *{recent_ball.text}*\n\nPartnership: {partnership_text.text}\nLast Wicket: {last_wkt}\n\n*Commentary:*\n---------------------\n*{comments_text}*---------------------"
   try:
    print(score_update)
    print(bat_team)
    await asyncio.gather(bot.send_message(call.from_user.id,text,parse_mode="Markdown",reply_markup=keyboard),bot.delete_message(call.from_user.id,call.message.id))
    #await bot.edit_message_text(text,call.from_user.id,call.message.id, parse_mode="Markdown",reply_markup=keyboard)
   except:
    await bot.answer_callback_query(call.id, text="No Changes Has Been Made", show_alert=True)