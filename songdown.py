from __future__ import unicode_literals
import asyncio
import math
import io
import os
import time
import requests
import wget
import yt_dlp
import logging
from urllib.parse import urlparse
from pyrogram import filters
from pyrogram.types import Message
from tswift import Song
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from pyrogram import filters, Client, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, BOT_TOKEN

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

async def progress(current, total, message, start, type_of_ps, file_name=None):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        if elapsed_time == 0:
            return
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "{0}{1} {2}%\n".format(
            "".join(["🔴" for i in range(math.floor(percentage / 10))]),
            "".join(["🔘" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(total), time_formatter(estimated_total_time)
        )
        if file_name:
            try:
                await message.edit(
                    "{}\n**File Name:** `{}`\n{}".format(type_of_ps, file_name, tmp)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass
        else:
            try:
                await message.edit("{}\n{}".format(type_of_ps, tmp))
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass


def get_text(message: Message) -> [None, str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None

def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def download_youtube_audio(url: str):
    global is_downloading
    with yt_dlp.YoutubeDL(
        {
            "format": "bestaudio",
            "writethumbnail": True,
            "quiet": True,
        }
    ) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        if int(float(info_dict["duration"])) > 180:
            is_downloading = False
            return []
        ydl.process_info(info_dict)
        audio_file = ydl.prepare_filename(info_dict)
        basename = audio_file.rsplit(".", 1)[-2]
        if info_dict["ext"] == "webm":
            audio_file_opus = basename + ".opus"
            ffmpeg.input(audio_file).output(
                audio_file_opus, codec="copy", loglevel="error"
            ).overwrite_output().run()
            os.remove(audio_file)
            audio_file = audio_file_opus
        thumbnail_url = info_dict["thumbnail"]
        thumbnail_file = (
            basename + "." + get_file_extension_from_url(thumbnail_url)
        )
        title = info_dict["title"]
        performer = info_dict["uploader"]
        duration = int(float(info_dict["duration"]))
    return [title, performer, duration, audio_file, thumbnail_file]


@bot.on_message(filters.command(["vsong", "video"]))
async def ytmusic(client, message: Message):
    urlissed = get_text(message)

    pablo = await client.send_message(
        message.chat.id, f"`Getting {urlissed} From Youtube Servers. Please Wait.`"
    )
    if not urlissed:
        await pablo.edit("Invalid Command Syntax, Please Check Help Menu To Know More!")
        return

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            infoo = ytdl.extract_info(url, False)
            duration = round(infoo["duration"] / 60)
            LIMIT = "180"          
 
            if duration > LIMIT:
                await pablo.edit(
                    f"❌ **durasinya kelamaan gabisa tot:v**"
                )
                is_downloading = False
                return
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(f"**Failed To Download** \n**Error :** `{str(e)}`")
        return
    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"**Video Name ➠** [{thum}]({mo}) \n**Requested For :** `{urlissed}` \n**Channel :** `{thums}` "
    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        progress=progress,
        progress_args=(
            pablo,
            c_time,
            f"`Uploading {urlissed} Song From YouTube Music!`",
            file_stark,
        ),
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)


import asyncio
from os import path

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto, Message,
                            Voice)
from youtube_search import YoutubeSearch

from Yukki import (BOT_USERNAME, DURATION_LIMIT, DURATION_LIMIT_MIN,
                   MUSIC_BOT_NAME, app, db_mem)
from Yukki.Decorators.permission import PermissionCheck
from Yukki.Inline import song_download_markup, song_markup
from Yukki.Utilities.url import get_url
from Yukki.Utilities.youtube import (get_yt_info_query,
                                     get_yt_info_query_slider)

loop = asyncio.get_event_loop()


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


@app.on_callback_query(filters.regex("qwertyuiopasdfghjkl"))
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
