import os
import time
import random
import shutil
import yt_dlp
import psutil
import asyncio
import subprocess
import config
import asyncio
from os import path
from typing import Union
from pytube import YouTube
from yt_dlp import YoutubeDL
from asyncio import QueueEmpty
from sys import version as pyver
from youtubesearchpython import VideosSearch

from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import (
    Message,
    Audio,
    Voice,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

import os
import aiohttp
import aiofiles

from os import path
from PIL import (
    Image,
    ImageFont,
    ImageDraw,
)

from yt_dlp import YoutubeDL

ytdl = YoutubeDL(
    {
        "format": "bestaudio[ext=m4a]",
        "geo_bypass": True,
        "noprogress": True,
        "nocheckcertificate": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "no_warnings": True,
        "quite": True,
    }
)

ytdl_opts = {"format": "bestaudio[ext=m4a]", "quiet": True}

def changeImageSize(maxWidth, maxHeight, image):
    if image.size[0] == image.size[1]:
        newImage = image.resize((maxHeight, maxHeight))
        img = Image.new("RGBA", (maxWidth, maxHeight))
        img.paste(newImage, (int((maxWidth - maxHeight) / 2), 0))
        return img
    else:
        widthRatio = maxWidth / image.size[0]
        heightRatio = maxHeight / image.size[1]
        newWidth = int(widthRatio * image.size[0])
        newHeight = int(heightRatio * image.size[1])
        newImage = image.resize((newWidth, newHeight))
    return newImage


async def gen_thumb(thumbnail, title, userid, theme, ctitle):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"search/thumb{userid}.jpg", mode="wb")
                await f.write(await resp.read())
                await f.close()
    image1 = Image.open(f"search/thumb{userid}.jpg")
    image2 = Image.open(f"cache/{theme}.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save(f"search/temp{userid}.png")
    img = Image.open(f"search/temp{userid}.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("cache/regular.ttf", 49)
    font2 = ImageFont.truetype("cache/medium.ttf", 70)
    draw.text((30, 543), f"Playing on {ctitle[:12]}", fill="black", font=font)
    draw.text((30, 615), f"{title[:20]}...", fill= "black", font=font2)
    img.save(f"search/final{userid}.png")
    os.remove(f"search/temp{userid}.png")
    os.remove(f"search/thumb{userid}.jpg") 
    final = f"search/final{userid}.png"
    return final


async def down_thumb(thumbnail, userid):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"search/thumb{userid}.jpg", mode="wb")
                await f.write(await resp.read())
                await f.close()
    final = f"search/thumb{userid}.jpg"
    return final

BOT_NAME = ""
BOT_USERNAME = ""
ASSID = 0
ASSNAME = ""
ASSUSERNAME = ""
ASSMENTION = ""
DURATION_LIMIT = "360"

from typing import Callable
from pyrogram import Client
from pyrogram.types import Message
from typing import Union
from pyrogram.types import Message, Audio, Voice

async def convert_count(count):
    if int(count) == 1:
        x = "First"
    elif int(count) == 2:
        x = "Second"
    elif int(count) == 3:
        x = "Third"
    elif int(count) == 4:
        x = "Fourth"
    elif int(count) == 5:
        x = "Fifth"    
    elif int(count) == 6:
        x = "Sixth"    
    elif int(count) == 7:
        x = "Seventh"    
    elif int(count) == 8:
        x = "Eighth"    
    elif int(count) == 9:
        x = "Ninth"
    elif int(count) == 10:
        x = "Tenth"    
    elif int(count) == 11:
        x = "Eleventh"
    elif int(count) == 12:
        x = "Twelfth"    
    elif int(count) == 13:
        x = "Thirteenth"     
    elif int(count) == 14:
        x = "Fourteenth"    
    elif int(count) == 15:
        x = "Fifteenth" 
    elif str(count) == "all":
        x = "all"
    return x


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
    return text[offset:offset + length]

random_assistant = ["5", "1", "2", "3", "4"]

themes = ["LightGreen"]

def bytes(size: float) -> str:
    """humanize size"""
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


async def ass_det(assistant: int):
    print("VEEZ MUSIC MEGA")

def errors(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        try:
            return await func(client, message)
        except Exception as e:
            await message.reply(f'{type(e).__name__}: {e}', False)

    return decorator
class FFmpegReturnCodeError(Exception):
    pass

from typing import List
from typing import Union
from pyrogram import filters

COMMAND_PREFIXES = "/"

other_filters = filters.group & ~ filters.edited & \
    ~ filters.via_bot & ~ filters.forwarded
other_filters2 = filters.private & ~ filters.edited \
    & ~ filters.via_bot & ~ filters.forwarded


def command(commands: Union[str, List[str]]):
    return filters.command(commands, COMMAND_PREFIXES)

async def convert(file_path: str) -> str:
    out = path.basename(file_path)
    out = out.split(".")
    out[-1] = "raw"
    out = ".".join(out)
    out = path.basename(out)
    out = path.join("raw_files", out)

    if path.isfile(out):
        return out

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd=(
                "ffmpeg " 
                "-y -i "
                f"{file_path} "
                "-f s16le "
                "-ac 1 "
                "-ar 48000 "
                "-acodec "
                "pcm_s16le "
                f"{out}"
            ),    
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await proc.communicate()

        if proc.returncode != 0:
            raise FFmpegReturnCodeError("FFmpeg did not return 0")

        return out
    except:
        raise FFmpegReturnCodeError("FFmpeg did not return 0")

from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)


def stream_markup(videoid, user_id):
    buttons= [
            [
                InlineKeyboardButton(text="❌ Cancel", callback_data=f'stopvc2'),      
                InlineKeyboardButton(text="🗑 Close", callback_data=f'close2')
            ],
        ]
    return buttons


def play_markup(videoid, user_id):
    buttons= [
            [
                InlineKeyboardButton(text="⚙️ Menu", callback_data=f'other {videoid}|{user_id}'),      
                InlineKeyboardButton(text="🗑 Close", callback_data=f'close2')
            ],
        ]
    return buttons 


def others_markup(videoid, user_id):
    buttons= [
            [
                InlineKeyboardButton(text="▶️", callback_data=f'resumevc2'),
                InlineKeyboardButton(text="⏸️", callback_data=f'pausevc2'),
                InlineKeyboardButton(text="⏭️", callback_data=f'skipvc2'),
                InlineKeyboardButton(text="⏹️", callback_data=f'stopvc2')
            ],
            [
                InlineKeyboardButton(text="✚ Your Playlist", callback_data=f'playlist {videoid}|{user_id}'),
                InlineKeyboardButton(text="✚ Group Playlist", callback_data=f'group_playlist {videoid}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="📥 Get Audio", callback_data=f'gets audio|{videoid}|{user_id}'),
                InlineKeyboardButton(text="📥 Get Video", callback_data=f'gets video|{videoid}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="🔙 Go Back", callback_data=f'goback {videoid}|{user_id}')
            ],
        ]
    return buttons


play_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "▶️", callback_data="resumevc"
                    ),
                    InlineKeyboardButton(
                        "⏸️", callback_data="pausevc"
                    ),
                    InlineKeyboardButton(
                        "⏭️", callback_data="skipvc"
                    ),
                    InlineKeyboardButton(
                        "⏹️", callback_data="stopvc"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🗑 Close", callback_data="close"
                    )
                ]    
            ]
        )

def audio_markup(videoid, user_id):
    buttons= [
            [
                InlineKeyboardButton(text="▶️", callback_data=f'resumevc2'),
                InlineKeyboardButton(text="⏸️", callback_data=f'pausevc2'),
                InlineKeyboardButton(text="⏭️", callback_data=f'skipvc2'),
                InlineKeyboardButton(text="⏹️", callback_data=f'stopvc2')
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data="close2")              
            ],
        ]
    return buttons 


def search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query):
    buttons= [
            [
                InlineKeyboardButton(text="1️⃣", callback_data=f'yukki2 {ID1}|{duration1}|{user_id}'),
                InlineKeyboardButton(text="2️⃣", callback_data=f'yukki2 {ID2}|{duration2}|{user_id}'),
                InlineKeyboardButton(text="3️⃣", callback_data=f'yukki2 {ID3}|{duration3}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="4️⃣", callback_data=f'yukki2 {ID4}|{duration4}|{user_id}'),
                InlineKeyboardButton(text="5️⃣", callback_data=f'yukki2 {ID5}|{duration5}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="➡", callback_data=f'popat 1|{query}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data=f"ppcl2 smex|{user_id}")
            ],
        ]
    return buttons   


def search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10 ,user_id, query):
    buttons= [
            [
                InlineKeyboardButton(text="6️⃣", callback_data=f'yukki2 {ID6}|{duration6}|{user_id}'),
                InlineKeyboardButton(text="7️⃣", callback_data=f'yukki2 {ID7}|{duration7}|{user_id}'),
                InlineKeyboardButton(text="8️⃣", callback_data=f'yukki2 {ID8}|{duration8}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="9️⃣", callback_data=f'yukki2 {ID9}|{duration9}|{user_id}'),
                InlineKeyboardButton(text="🔟", callback_data=f'yukki2 {ID10}|{duration10}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="⬅", callback_data=f'popat 2|{query}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data=f"ppcl2 smex|{user_id}")
            ],
        ]
    return buttons 


def personal_markup(link):
    buttons= [
            [ 
                InlineKeyboardButton(text="🗑 Close", callback_data=f'cls')
            ],
        ]
    return buttons


start_keyboard = InlineKeyboardMarkup( 
            [
                [
                    InlineKeyboardButton(
                        "📚 Commands", url="https://telegra.ph/Veez-Mega-Bot-09-30"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🗑 Close", callback_data="close2"
                    )
                ]    
            ]
        )
 
   
confirm_keyboard = InlineKeyboardMarkup( 
            [
                [
                    InlineKeyboardButton(
                        "✅ Yes", callback_data="cbdel"
                    ),
                    InlineKeyboardButton(
                        "❌ No", callback_data="close2"
                    )
                ]    
            ]
        )


confirm_group_keyboard = InlineKeyboardMarkup( 
            [
                [
                    InlineKeyboardButton(
                        "✅ Yes", callback_data="cbgroupdel"
                    ),
                    InlineKeyboardButton(
                        "❌ No", callback_data="close2"
                    )
                ]    
            ]
        )


close_keyboard = InlineKeyboardMarkup( 
            [
                [
                    InlineKeyboardButton(
                        "🗑 Close", callback_data="close2"
                    )
                ]    
            ]
        )


none_keyboard = InlineKeyboardMarkup( 
            [
                [
                    InlineKeyboardButton(
                        "🗑 Close", callback_data="cls"
                    )
                ]    
            ]
        )


play_list_keyboard = InlineKeyboardMarkup( 
            [
                [
                    InlineKeyboardButton(
                        "Personal Playlist", callback_data="P_list"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Group's Playlist", callback_data="G_list"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🗑 Close", callback_data="close2"
                    )
                ]
            ]
        )


def playlist_markup(user_name, user_id):
    buttons= [
            [
                InlineKeyboardButton(text=f"Group's Playlist", callback_data=f'play_playlist {user_id}|group')
            ],
            [
                InlineKeyboardButton(text=f"{user_name[:8]}'s Playlist", callback_data=f'play_playlist {user_id}|personal')
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data="close2")              
            ],
        ]
    return buttons

flex = {}
chat_watcher_group = 3

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":")))
    )

app = Client(
    'mega',
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
)

@Client.on_message(command(["music", "song"]) & ~filters.edited)
async def musicdl(_, message: Message):
    await message.delete()
    chat_id = message.chat.id
    if message.sender_chat:
        return await message.reply_text("You'll need to switch to a user account to download video/music.")  
    user_id = message.from_user.id
    chat_title = message.chat.title
    username = message.from_user.first_name
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    url = get_url(message)
    fucksemx = 0
    if url:
        query = " ".join(message.command[1:])
        mystic = await _.send_message(chat_id, "🔍 **Searching...**")
        ydl_opts = {"format": "bestaudio/best"}
        try:
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = (result["title"])
                duration = (result["duration"])
                views = (result["viewCount"]["short"])  
                thumbnail = (result["thumbnails"][0]["url"])
                link = (result["link"])
                idxz = (result["id"])
                videoid = (result["id"])
        except Exception as e:
            return await mystic.edit_text("😕 Sorry, we **couldn't** find the song you were looking for\n\n• Check that the **name is correct** or **try by searching the artist.**")    
        smex = int(time_to_seconds(duration))
        if smex > DURATION_LIMIT:
            return await mystic.edit_text(f"❌ **duration error**\n\n**allowed duration: {DURATION_LIMIT}\n**received duration:** {duration}")
        if duration == "None":
            return await mystic.edit_text("❌ **live stream not supported**")
        if views == "None":
            return await mystic.edit_text("❌ **live stream not supported**")
        thumb = await down_thumb(thumbnail, user_id)
        buttons = gets(videoid, user_id)
        m = await message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),    
            caption=(f"🏷 <b>Name:</b> [{title[:65]}]({url})\n\n💡 [Check music information](https://t.me/{BOT_USERNAME}?start=info_{id})")
        )   
        os.remove(thumb)
    else:
        if len(message.command) < 2:
            await message.reply_text("**usage:**\n\n/song [youtube url/song name]")
        query = " ".join(message.command[1:])
        mystic = await _.send_message(chat_id, "🔍 **Searching...**")
        try:
            a = VideosSearch(query, limit=5)
            result = (a.result()).get("result")
            title1 = (result[0]["title"])
            duration1 = (result[0]["duration"])
            title2 = (result[1]["title"])
            duration2 = (result[1]["duration"])      
            title3 = (result[2]["title"])
            duration3 = (result[2]["duration"])
            title4 = (result[3]["title"])
            duration4 = (result[3]["duration"])
            title5 = (result[4]["title"])
            duration5 = (result[4]["duration"])
            ID1 = (result[0]["id"])
            ID2 = (result[1]["id"])
            ID3 = (result[2]["id"])
            ID4 = (result[3]["id"])
            ID5 = (result[4]["id"])
        except Exception as e:
            return await mystic.edit_text("😕 Sorry, we **couldn't** find the song you were looking for\n\n• Check that the **name is correct** or **try by searching the artist.**")
        thumb ="cache/results.png"
        link = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await mystic.edit(
            f"• Choose the results to download !\n\n1️⃣ <b>[{title1[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n\n2️⃣ <b>[{title2[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n\n3️⃣ <b>[{title3[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n\n4️⃣ <b>[{title4[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n\n5️⃣ <b>[{title5[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID5})",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return
    
    
@Client.on_callback_query(filters.regex(pattern=r"beta"))
async def download_data(_,CallbackQuery): 
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id 
    try:
        id,duration,user_id = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"❌ an error occured\n\n**reason:** `{e}`")
    if duration == "None":
        return await CallbackQuery.message.reply_text(f"❌ **live stream not supported**")      
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer("💡 sorry this is not your request", show_alert=True)
    await CallbackQuery.message.delete()
    checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    url = (f"https://www.youtube.com/watch?v={id}")
    videoid = id
    idx = id
    smex = int(time_to_seconds(duration))
    if smex > DURATION_LIMIT:
        await CallbackQuery.message.reply_text(f"❌ **duration error**\n\n**allowed duration: {DURATION_LIMIT}\n**received duration:** {duration}")
        return 
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            x = ytdl.extract_info(url, download=False)
    except Exception as e:
        return await CallbackQuery.message.reply_text(f"failed to download this video.\n\n**reason:** `{e}`") 
    title = (x["title"])
    thumbnail = (x["thumbnail"])
    idx = (x["id"])
    videoid = (x["id"])
    thumb = await down_thumb(thumbnail, user_id)
    buttons = gets(videoid, user_id)
    m = await CallbackQuery.message.reply_photo(
        photo=thumb,
        reply_markup=InlineKeyboardMarkup(buttons),    
        caption=(f"🏷 **Name:** [{title[:80]}]({url})\n\n💡 [Check music information](https://t.me/{BOT_USERNAME}?start=info_{id})")
    )   
    os.remove(thumb)
    await CallbackQuery.message.delete()
        
        
@Client.on_callback_query(filters.regex(pattern=r"chonga"))
async def chonga(_,CallbackQuery): 
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    print(callback_request)
    userid = CallbackQuery.from_user.id 
    try:
        id , query, user_id = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"❌ an error occured\n**reason:** `{e}`")       
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer("💡 sorry this is not your request", show_alert=True)
    i=int(id)
    query = str(query)
    try:
        a = VideosSearch(query, limit=10)
        result = (a.result()).get("result")
        title1 = (result[0]["title"])
        duration1 = (result[0]["duration"])
        title2 = (result[1]["title"])
        duration2 = (result[1]["duration"])      
        title3 = (result[2]["title"])
        duration3 = (result[2]["duration"])
        title4 = (result[3]["title"])
        duration4 = (result[3]["duration"])
        title5 = (result[4]["title"])
        duration5 = (result[4]["duration"])
        title6 = (result[5]["title"])
        duration6 = (result[5]["duration"])
        title7= (result[6]["title"])
        duration7 = (result[6]["duration"])      
        title8 = (result[7]["title"])
        duration8 = (result[7]["duration"])
        title9 = (result[8]["title"])
        duration9 = (result[8]["duration"])
        title10 = (result[9]["title"])
        duration10 = (result[9]["duration"])
        ID1 = (result[0]["id"])
        ID2 = (result[1]["id"])
        ID3 = (result[2]["id"])
        ID4 = (result[3]["id"])
        ID5 = (result[4]["id"])
        ID6 = (result[5]["id"])
        ID7 = (result[6]["id"])
        ID8 = (result[7]["id"])
        ID9 = (result[8]["id"])
        ID10 = (result[9]["id"])                    
    except Exception as e:
        return await mystic.edit_text(f"song not found.\n**reason:** {e}")
    if i == 1:
        link = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10 ,user_id, query)
        await CallbackQuery.edit_message_text(
            f"• Choose the results to download !\n\n6️⃣ <b>[{title6[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID6})\n\n7️⃣ <b>[{title7[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID7})\n\n8️⃣ <b>[{title8[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID8})\n\n9️⃣ <b>[{title9[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID9})\n\n🔟 <b>[{title10[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID10})",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return    
    if i == 2:
        link = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await CallbackQuery.edit_message_text(
            f"• Choose the results to download !\n\n1️⃣ <b>[{title1[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n\n2️⃣ <b>[{title2[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n\n3️⃣ <b>[{title3[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n\n4️⃣ <b>[{title4[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n\n5️⃣ <b>[{title5[:30]}...]({link})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID5})",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return    
      

def search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query):
    buttons= [
            [
                InlineKeyboardButton(text="1️⃣", callback_data=f'beta {ID1}|{duration1}|{user_id}'),
                InlineKeyboardButton(text="2️⃣", callback_data=f'beta {ID2}|{duration2}|{user_id}'),
                InlineKeyboardButton(text="3️⃣", callback_data=f'beta {ID3}|{duration3}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="4️⃣", callback_data=f'beta {ID4}|{duration4}|{user_id}'),
                InlineKeyboardButton(text="5️⃣", callback_data=f'beta {ID5}|{duration5}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="➡️", callback_data=f'chonga 1|{query}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data=f"ppcl2 smex|{user_id}")
            ],
        ]
    return buttons   

def search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10 ,user_id, query):
    buttons= [
            [
                InlineKeyboardButton(text="6️⃣", callback_data=f'beta {ID6}|{duration6}|{user_id}'),
                InlineKeyboardButton(text="7️⃣", callback_data=f'beta {ID7}|{duration7}|{user_id}'),
                InlineKeyboardButton(text="8️⃣", callback_data=f'beta {ID8}|{duration8}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="9️⃣", callback_data=f'beta {ID9}|{duration9}|{user_id}'),
                InlineKeyboardButton(text="🔟", callback_data=f'beta {ID10}|{duration10}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="⬅️", callback_data=f'chonga 2|{query}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data=f"ppcl2 smex|{user_id}")
            ],
        ]
    return buttons     
      
def gets(videoid, user_id):
    buttons= [
            [
                InlineKeyboardButton(text="📥 Get Audio", callback_data=f'gets audio|{videoid}|{user_id}'),
                InlineKeyboardButton(text="📥 Get Video", callback_data=f'gets video|{videoid}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data=f'close2')
            ],
        ]
    return buttons
