import asyncio
import math
import io
import os
from os import path
import time
import requests
import logging
from urllib.parse import urlparse
from typing import Union
from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto, Message,
                            Voice)
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from pyrogram import filters, Client, idle
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InputMediaPhoto, Message)
from config import API_ID, API_HASH, BOT_TOKEN, DURATION_LIMIT_MIN, MUSIC_BOT_NAME

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":")))
    )

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
BOT_USERNAME = ""
MUSIC_BOT_NAME = MUSIC_BOT_NAME
BOT_USERNAME = getme.username

# logging
bot = Client(
   "Music-Bot",
   api_id=API_ID,
   api_hash=API_HASH,
   bot_token=BOT_TOKEN,
)
## Extra Fns -------
# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------
@bot.on_message(filters.command(['start']))
async def start(client, message):
       await message.reply("👋 𝗛𝗲𝗹𝗹𝗼 𝗕𝗿𝗼\n\n I Am Song Downloader Bot\n\n𝑺𝒆𝒏𝒕 𝒕𝒉𝒆 𝑵𝒂𝒎𝒆 𝒐𝒇 𝒕𝒉𝒆 𝐒𝐨𝐧𝐠 𝒀𝒐𝒖 𝑾𝒂𝒏𝒕... 😍🥰🤗\n\n𝗝𝘂𝘀𝘁 𝗧𝘆𝗽𝗲 𝗮 𝗦𝗼𝗻𝗴 𝗡𝗮𝗺𝗲\n\n𝐄𝐠. `Love Nwantiti`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿', url='https://t.me/about_devildad'),
                    InlineKeyboardButton('𝗦𝗼𝘂𝗿𝗰𝗲', url='https://t.me/princebotsupport')
                ]
            ]
        )
    )

@bot.on_message(filters.command(['help']))
async def help(client, message):
       await message.reply("<b>Simplest Way😂</b>\n\n<i>How many times have I said that just giving the name of a song is enough.🙄\nDo not expect any other help from me😠</i>\n\n<b>Eg</b> `Vaathi Coming`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('𝗦𝗼𝘂𝗿𝗰𝗲', url='https://github.com/arupmandal/Music')
                ]
            ]
        )
    )

@bot.on_message(filters.command(['about']))
async def about(client, message):
       await message.reply("➪<b>Name</b> : ✫<i>Song Downloader</i>\n➪<b>Developer</b> : ✫[Prince](https://t.me/About_devildad)\n➪<b>Language</b> : ✫<i>Python3</i>\n➪<b>Server</b> : ✫[𝘏𝘦𝘳𝘰𝘬𝘶](https://heroku.com/)\n➪<b>Source Code</b> : ✫[𝘊𝘭𝘪𝘤𝘬 𝘏𝘦𝘳𝘦](https://t.me/princebotsupport)",
    )

def init_db():
    global db_mem
    db_mem = {}

def song_markup(videoid, duration, user_id, query, query_type):
    buttons = [
        [
            InlineKeyboardButton(
                text="❮",
                callback_data=f"song_right B|{query_type}|{query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="Download",
                callback_data=f"qwertyuiopasdfghjkl {videoid}|{user_id}",
            ),
            InlineKeyboardButton(
                text="❯",
                callback_data=f"song_right F|{query_type}|{query}|{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑 Close Search",
                callback_data=f"forceclose {query}|{user_id}",
            )
        ],
    ]
    return buttons


def song_download_markup(videoid, user_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="⬇️ Get Audio",
                callback_data=f"gets audio|{videoid}|{user_id}",
            ),
            InlineKeyboardButton(
                text="⬇️ Get Video",
                callback_data=f"gets video|{videoid}|{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑 Close Menu",
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons


loop = asyncio.get_event_loop()

def get_url(message_1: Message) -> Union[str, None]:
    messages = [message_1]
    if message_1.reply_to_message:
        messages.append(message_1.reply_to_message)
    text = ""
    offset = None
    length = None
    for message in messages:
        if offset:
            break
        if message.entities:
            for entity in message.entities:
                if entity.type == "url":
                    text = message.text or message.caption
                    offset, length = entity.offset, entity.length
                    break
    if offset in (None,):
        return None
    return text[offset : offset + length]

def get_yt_info_id(videoid):
    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    for result in results.result()["result"]:
        title = result["title"]
        duration_min = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        if str(duration_min) == "None":
            duration_sec = 0
        else:
            duration_sec = int(time_to_seconds(duration_min))
    return title, duration_min, duration_sec, thumbnail


def get_yt_info_query(query: str):
    results = VideosSearch(query, limit=1)
    for result in results.result()["result"]:
        title = result["title"]
        duration_min = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        videoid = result["id"]
        if str(duration_min) == "None":
            duration_sec = 0
        else:
            duration_sec = int(time_to_seconds(duration_min))
    return title, duration_min, duration_sec, thumbnail, videoid


def get_yt_info_query_slider(query: str, query_type: int):
    a = VideosSearch(query, limit=10)
    result = (a.result()).get("result")
    title = result[query_type]["title"]
    duration_min = result[query_type]["duration"]
    videoid = result[query_type]["id"]
    thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
    if str(duration_min) == "None":
        duration_sec = 0
    else:
        duration_sec = int(time_to_seconds(duration_min))
    return title, duration_min, duration_sec, thumbnail, videoid

@bot.on_message(
filters.command(["song", "video"])
)

async def play(_, message: Message):
    chat_id = message.chat.id
    if message.sender_chat:
        return await message.reply_text(
            "You're an __Anonymous Admin__ in this Chat Group!\nRevert back to User Account From Admin Rights."
        )
    user_id = message.from_user.id
    chat_title = message.chat.title
    username = message.from_user.first_name
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

    

    await message.delete()
    url = get_url(message)
    if url:
        mystic = await message.reply_text("🔄 Processing URL... Please Wait!")
        query = message.text.split(None, 1)[1]
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(None, get_yt_info_query, query)
        if str(duration_min) == "None":
            return await mystic.edit("Sorry! Its a Live Video")
        await mystic.delete()
        buttons = song_download_markup(videoid, message.from_user.id)
        return await message.reply_photo(
            photo=thumb,
            caption=f"📎Title: **{title}\n\n⏳Duration:** {duration_min} Mins\n\n__[Get Additional Information About Video](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:**\n\n/song [Youtube Url or Music Name]\n\nDownloads the Particular Query."
            )
            return
        mystic = await message.reply_text("🔍 Searching Your Query...")
        query = message.text.split(None, 1)[1]
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(None, get_yt_info_query, query)
        if str(duration_min) == "None":
            return await mystic.edit("Sorry! Its a Live Video")
        await mystic.delete()
        buttons = song_markup(
            videoid, duration_min, message.from_user.id, query, 0
        )
        return await message.reply_photo(
            photo=thumb,
            caption=f"📎Title: **{title}\n\n⏳Duration:** {duration_min} Mins\n\n__[Get Additional Information About Video](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@bot.on_callback_query(filters.regex("qwertyuiopasdfghjkl"))
async def qwertyuiopasdfghjkl(_, CallbackQuery):
    print("234")
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = song_download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(pattern=r"song_right"))
async def song_right(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, type, query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Search Your Own Music. You're not allowed to use this button.",
            show_alert=True,
        )
    what = str(what)
    type = int(type)
    if what == "F":
        if type == 9:
            query_type = 0
        else:
            query_type = int(type + 1)
        await CallbackQuery.answer("Getting Next Result", show_alert=True)
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(
            None, get_yt_info_query_slider, query, query_type
        )
        buttons = song_markup(
            videoid, duration_min, user_id, query, query_type
        )
        med = InputMediaPhoto(
            media=thumb,
            caption=f"📎Title: **{title}\n\n⏳Duration:** {duration_min} Mins\n\n__[Get Additional Information About Video](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
    if what == "B":
        if type == 0:
            query_type = 9
        else:
            query_type = int(type - 1)
        await CallbackQuery.answer("Getting Previous Result", show_alert=True)
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(
            None, get_yt_info_query_slider, query, query_type
        )
        buttons = song_markup(
            videoid, duration_min, user_id, query, query_type
        )
        med = InputMediaPhoto(
            media=thumb,
            caption=f"📎Title: **{title}\n\n⏳Duration:** {duration_min} Mins\n\n__[Get Additional Information About Video](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )

bot.run()
