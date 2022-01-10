import asyncio
import math
import io
import os
from os import path
import time
import requests
import logging
import wget
import yt_dlp
from urllib.parse import urlparse
from typing import Union
from pyrogram import filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InputMediaAudio,
                            InputMediaDocument, InputMediaPhoto, InputMediaVideo, Message, Voice)
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from pyrogram import filters, Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, DURATION_LIMIT_MIN, MUSIC_BOT_NAME
from youtubesearchpython import VideosSearch
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

loop = asyncio.get_event_loop()

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":")))
    )

# logging
bot = Client(
   "Music-Bot",
   api_id=API_ID,
   api_hash=API_HASH,
   bot_token=BOT_TOKEN,
)

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
BOT_USERNAME = "princexsongdownbot"
MUSIC_BOT_NAME = MUSIC_BOT_NAME


## Extra Fns -------
# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------
@bot.on_message(filters.command(['start']))
async def start(client, message):
       await message.reply("👋 𝗛𝗲𝗹𝗹𝗼 𝗕𝗿𝗼\n\n𝗝𝘂𝘀𝘁 𝗧𝘆𝗽𝗲 𝗮 𝗦𝗼𝗻𝗴 𝗡𝗮𝗺𝗲\n\n𝐄𝐠. `Love Nwantiti`",
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

def YT_info(yturl):
    ydl = yt_dlp.YoutubeDL()
    with ydl:
        formats_available = []
        r = ydl.extract_info(yturl, download=False)
        for format in r["formats"]:
            # Filter dash video(without audio)
            if not "dash" in str(format["format"]).lower():
                formats_available.append(
                    {
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "yturl": yturl,
                    }
                )

        return formats_available

def humanbytes(num, suffix="B"):
    if num is None:
        num = 0
    else:
        num = int(num)

    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)

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

@bot.on_callback_query(filters.regex("forceclose"))
async def forceclose(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "You're not allowed to close this.", show_alert=True
        )
    await CallbackQuery.message.delete()
    await CallbackQuery.answer()

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


user_time = {}
flex = {}

async def get_formats(CallbackQuery, videoid, user_id, type):
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        formats = YT_info(url)
    except Exception:
        return await CallbackQuery.message.reply_text(
            "Failed To Fetch Data..."
        )
    j = 0
    for x in formats:
        check = x["format"]
        if type == "audio":
            if "audio" in check:
                j += 1
                if j == 1:
                    a1 = InlineKeyboardButton(
                        text=f"Audio 🎵 {humanbytes(x['filesize'])}",
                        callback_data=f"ytdata audio||{x['format_id']}||{videoid}",
                    )
                if j == 2:
                    a2 = InlineKeyboardButton(
                        text=f"Audio 🎵 {humanbytes(x['filesize'])}",
                        callback_data=f"ytdata audio||{x['format_id']}||{videoid}",
                    )
                if j == 3:
                    a3 = InlineKeyboardButton(
                        text=f"Audio 🎵 {humanbytes(x['filesize'])}",
                        callback_data=f"ytdata audio||{x['format_id']}||{videoid}",
                    )
                if j == 4:
                    a4 = InlineKeyboardButton(
                        text=f"Audio 🎵 {humanbytes(x['filesize'])}",
                        callback_data=f"ytdata audio||{x['format_id']}||{videoid}",
                    )
                if j == 5:
                    a5 = InlineKeyboardButton(
                        text=f"Audio 🎵 {humanbytes(x['filesize'])}",
                        callback_data=f"ytdata audio||{x['format_id']}||{videoid}",
                    )
                if j == 6:
                    a6 = InlineKeyboardButton(
                        text=f"Audio 🎵 {humanbytes(x['filesize'])}",
                        callback_data=f"ytdata audio||{x['format_id']}||{videoid}",
                    )
        elif type == "video":
            if str(133) in check:
                j += 1
                a1 = InlineKeyboardButton(
                    text=f"(240)p 📹 {humanbytes(x['filesize'])}",
                    callback_data=f"ytdata video||{x['format_id']}||{videoid}",
                )
            if str(134) in check:
                j += 1
                a2 = InlineKeyboardButton(
                    text=f"(360)p 📹 {humanbytes(x['filesize'])}",
                    callback_data=f"ytdata video||{x['format_id']}||{videoid}",
                )
            if str(135) in check:
                j += 1
                a3 = InlineKeyboardButton(
                    text=f"(480)p 📹 {humanbytes(x['filesize'])}",
                    callback_data=f"ytdata video||{x['format_id']}||{videoid}",
                )
            if str(136) in check:
                j += 1
                a4 = InlineKeyboardButton(
                    text=f"(720)p 📹 {humanbytes(x['filesize'])}",
                    callback_data=f"ytdata video||{x['format_id']}||{videoid}",
                )
            if str(137) in check:
                j += 1
                a5 = InlineKeyboardButton(
                    text=f"(1080)p 📹 {humanbytes(x['filesize'])}",
                    callback_data=f"ytdata video||{x['format_id']}||{videoid}",
                )
            if str(313) in check:
                j += 1
                a6 = InlineKeyboardButton(
                    text=f"(2160)p 📹 {humanbytes(x['filesize'])}",
                    callback_data=f"ytdata video||{x['format_id']}||{videoid}",
                )
        else:
            return await CallbackQuery.message.reply_text(
                "Video Format Not Found."
            )
    if j == 0:
        return await CallbackQuery.message.reply_text(
            "Video Format Not Found.."
        )
    elif j == 1:
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️  Go Back",
                        callback_data=f"good {videoid}|{user_id}",
                    ),
                    InlineKeyboardButton(
                        text="🗑 Close Menu", callback_data=f"close2"
                    ),
                ],
            ]
        )
    elif j == 2:
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                    a2,
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️  Go Back",
                        callback_data=f"good {videoid}|{user_id}",
                    ),
                    InlineKeyboardButton(
                        text="🗑 Close Menu", callback_data=f"close2"
                    ),
                ],
            ]
        )
    elif j == 3:
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                    a2,
                ],
                [
                    a3,
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️  Go Back",
                        callback_data=f"good {videoid}|{user_id}",
                    ),
                    InlineKeyboardButton(
                        text="🗑 Close Menu", callback_data=f"close2"
                    ),
                ],
            ]
        )
    elif j == 4:
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                    a2,
                ],
                [
                    a3,
                    a4,
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️  Go Back",
                        callback_data=f"good {videoid}|{user_id}",
                    ),
                    InlineKeyboardButton(
                        text="🗑 Close Menu", callback_data=f"close2"
                    ),
                ],
            ]
        )
    elif j == 5:
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                    a2,
                ],
                [
                    a3,
                    a4,
                ],
                [
                    a5,
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️  Go Back",
                        callback_data=f"good {videoid}|{user_id}",
                    ),
                    InlineKeyboardButton(
                        text="🗑 Close Menu", callback_data=f"close2"
                    ),
                ],
            ]
        )
    elif j == 6:
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                    a2,
                ],
                [
                    a3,
                    a4,
                ],
                [
                    a5,
                    a6,
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️  Go Back",
                        callback_data=f"good {videoid}|{user_id}",
                    ),
                    InlineKeyboardButton(
                        text="🗑 Close Menu", callback_data=f"close2"
                    ),
                ],
            ]
        )
    else:
        return await CallbackQuery.message.reply_text(
            "Video Format Not Found...."
        )
    return key

def get_type(type, format, videoid, user_id):
    if type == "audio":
        a1 = InlineKeyboardButton(
            text=f"Audio Form",
            callback_data=f"boom audio||{format}||{videoid}",
        )
        a2 = InlineKeyboardButton(
            text=f"Document Form",
            callback_data=f"boom docaudio||{format}||{videoid}",
        )
    else:
        a1 = InlineKeyboardButton(
            text=f"Video Form",
            callback_data=f"boom video||{format}||{videoid}",
        )
        a2 = InlineKeyboardButton(
            text=f"Document Form",
            callback_data=f"boom docvideo||{format}||{videoid}",
        )
    key = InlineKeyboardMarkup(
        [
            [
                a1,
                a2,
            ],
            [
                InlineKeyboardButton(
                    text="⬅️  Go Back",
                    callback_data=f"good {videoid}|{user_id}",
                ),
                InlineKeyboardButton(
                    text="🗑 Close Menu", callback_data=f"close2"
                ),
            ],
        ]
    )
    return key

@bot.on_callback_query(filters.regex("close"))
async def closed(_, query: CallbackQuery):
    await query.message.delete()
    await query.answer()


@bot.on_callback_query(filters.regex(pattern=r"down"))
async def down(_, CallbackQuery):
    await CallbackQuery.answer()


@bot.on_callback_query(filters.regex(pattern=r"gets"))
async def getspy(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, videoid, user_id = callback_request.split("|")
    key = await get_formats(CallbackQuery, videoid, user_id, type)
    await CallbackQuery.edit_message_reply_markup(reply_markup=key)


@bot.on_callback_query(filters.regex(pattern=r"ytdata"))
async def ytdata(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, format, videoid = callback_request.split("||")
    user_id = CallbackQuery.from_user.id
    key = get_type(type, format, videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(reply_markup=key)


inl = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text="Downloading......", callback_data=f"down")]]
)

upl = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text="Uploading......", callback_data=f"down")]]
)


def inl_mark(videoid, user_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Download or Upload Failed......", callback_data=f"down"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️  Go Back", callback_data=f"good {videoid}|{user_id}"
            ),
            InlineKeyboardButton(
                text="🗑 Close Menu", callback_data=f"close2"
            ),
        ],
    ]
    return buttons


ytdl_opts = {"format": "bestaudio", "quiet": True}


@bot.on_callback_query(filters.regex(pattern=r"boom"))
async def boom(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    type, format_id, videoid = callback_request.split("||")
    mystic = await CallbackQuery.edit_message_text(
        "Download Started\n\nDownloading speed could be slow. Please hold on..",
        reply_markup=inl,
    )
    yturl = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(yturl, limit=1)
    for result in results.result()["result"]:
        title = result["title"]
        duration = result["duration"]
        views = result["viewCount"]["short"]
        thumb_image_path = result["thumbnails"][0]["url"]
        channel = channel = result["channel"]["name"]
        fetched = f"""
🔍**Track Downloaded**

❇️**Title:** {title}

⏳**Duration:** {duration} Mins
👀**Views:** `{views}`
🎥**Channel Name:** {channel}
🔗**Video Link:** [Link]({yturl})

⚡️ __Youtube Inline Download Powered By {MUSIC_BOT_NAME}__"""
    filext = "%(title)s.%(ext)s"
    userdir = os.path.join(os.getcwd(), "downloads", str(user_id))
    if not os.path.isdir(userdir):
        os.makedirs(userdir)
    filepath = os.path.join(userdir, filext)
    img = wget.download(thumb_image_path)
    im = Image.open(img).convert("RGB")
    output_directory = os.path.join(os.getcwd(), "search", str(user_id))
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    thumb_image_path = f"{output_directory}.jpg"
    im.save(thumb_image_path, "jpeg")
    width = 0
    height = 0
    if os.path.exists(thumb_image_path):
        metadata = extractMetadata(createParser(thumb_image_path))
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
        img = Image.open(thumb_image_path)
        if type == "audio":
            img.resize((320, height))
        elif type == "docaudio":
            img.resize((320, height))
        elif type == "docvideo":
            img.resize((320, height))
        else:
            img.resize((90, height))
        img.save(thumb_image_path, "JPEG")
    audio_command = [
        "yt-dlp",
        "-c",
        "--prefer-ffmpeg",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        format_id,
        "-o",
        filepath,
        yturl,
    ]
    video_command = [
        "yt-dlp",
        "-c",
        "--embed-subs",
        "-f",
        f"{format_id}+140",
        "-o",
        filepath,
        "--hls-prefer-ffmpeg",
        yturl,
    ]
    loop = asyncio.get_event_loop()
    med = None
    perf = MUSIC_BOT_NAME
    if type == "audio":
        filename = await downloadaudiocli(audio_command)
        med = InputMediaAudio(
            media=filename,
            thumb=thumb_image_path,
            caption=fetched,
            title=os.path.basename(filename),
            performer=perf,
        )
    if type == "video":
        filename = await downloadvideocli(video_command)
        dur = int(time_to_seconds(duration))
        med = InputMediaVideo(
            media=filename,
            duration=dur,
            width=width,
            height=height,
            thumb=thumb_image_path,
            caption=fetched,
            supports_streaming=True,
        )
    if type == "docaudio":
        filename = await downloadaudiocli(audio_command)
        med = InputMediaDocument(
            media=filename,
            thumb=thumb_image_path,
            caption=fetched,
        )
    if type == "docvideo":
        filename = await downloadvideocli(video_command)
        dur = int(time_to_seconds(duration))
        med = InputMediaDocument(
            media=filename,
            thumb=thumb_image_path,
            caption=fetched,
        )
    if med:
        loop.create_task(
            send_file(
                CallbackQuery, med, filename, videoid, user_id, yturl, channel
            )
        )
    else:
        print("med not found")


def p_mark(link, channel):
    buttons = [
        [InlineKeyboardButton(text="Watch on Youtube", url=f"{link}")],
    ]
    return buttons


async def send_file(
    CallbackQuery, med, filename, videoid, user_id, link, channel
):
    await CallbackQuery.edit_message_text(
        "Upload Started\n\nUploading speed could be slow. Please hold on..",
        reply_markup=upl,
    )
    try:
        await app.send_chat_action(
            chat_id=CallbackQuery.message.chat.id, action="upload_document"
        )
        buttons = p_mark(link, channel)
        await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        buttons = inl_mark(videoid, user_id)
        await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    try:
        os.remove(filename)
    except:
        pass


import json
import subprocess as sp


def probe(vid_file_path):
    if type(vid_file_path) != str:
        raise Exception("Give ffprobe a full file path of the file")

    command = [
        "ffprobe",
        "-loglevel",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        vid_file_path,
    ]

    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    out, err = pipe.communicate()
    return json.loads(out)


def duration(vid_file_path):
    _json = probe(vid_file_path)

    if "format" in _json:
        if "duration" in _json["format"]:
            return float(_json["format"]["duration"])

    if "streams" in _json:
        # commonly stream 0 is the video
        for s in _json["streams"]:
            if "duration" in s:
                return float(s["duration"])

    raise Exception("duration Not found")


async def downloadvideocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    filename = t_response.split("Merging formats into")[-1].split('"')[1]
    return filename


async def downloadaudiocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()

    return (
        t_response.split("Destination")[-1]
        .split("Deleting")[0]
        .split(":")[-1]
        .strip()
    )


@bot.on_message(filters.text)
async def play(client,message):
    query=message.text
    chat_id = message.chat.id
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
        if len(message.text) < 2:
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

@bot.on_callback_query(filters.regex(pattern=r"song_right"))
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
