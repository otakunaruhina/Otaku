import logging
from pyrogram import Client, filters
import hashlib
import json
import os
from datetime import datetime

# 🔧 CONFIGURATION
API_ID = 28544353
API_HASH = "1e016228e6cd0fa4f24286a81b7e0384"
BOT_TOKEN = "7741081514:AAHk8WGnO31vD8zIcXZe5lsrR5gVa38Pqic"
CHANNEL_ID = -1002816506450  # ✅ Must start with -100

MAP_FILE = "file_map.json"

# 🧠 LOGGING
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🗂 File ID Storage
if not os.path.exists(MAP_FILE):
    with open(MAP_FILE, "w") as f:
        json.dump({}, f)

def load_map():
    with open(MAP_FILE, "r") as f:
        return json.load(f)

def save_map(data):
    with open(MAP_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_id(raw_data: bytes) -> str:
    return hashlib.sha256(raw_data).hexdigest()[:12]

# 🤖 BOT INSTANCE
bot = Client("file_store_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ /start
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Welcome to File Store Bot!\n\n"
        "📤 To store a file:\nReply to any file with /storefile\n\n"
        "📥 To retrieve:\nUse /getfile <file_id>\n\n"
        "📂 To list your files:\nUse /myfiles"
    )

# ✅ /storefile
@bot.on_message(filters.command("storefile") & filters.reply)
async def storefile(client, message):
    logging.info("Received /storefile command")
    reply = message.reply_to_message

    if not (reply.document or reply.photo or reply.video or reply.audio or reply.sticker or reply.animation):
        await message.reply_text("❌ Please reply to a file (photo/video/doc) to store.")
        return

    try:
        uid_source = f"{reply.id}_{reply.from_user.id if reply.from_user else 'unknown'}".encode()
        file_id = generate_id(uid_source)

        forwarded = await client.forward_messages(
            chat_id=CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_ids=reply.id
        )

        # Extract filename (if possible)
        file_name = ""
        if reply.document:
            file_name = reply.document.file_name
        elif reply.video:
            file_name = reply.video.file_name or "Unnamed Video"
        elif reply.audio:
            file_name = reply.audio.file_name or "Unnamed Audio"
        elif reply.photo:
            file_name = "Photo"
        elif reply.sticker:
            file_name = "Sticker"
        elif reply.animation:
            file_name = reply.animation.file_name or "Animation"

        mapping = load_map()
        mapping[file_id] = {
            "msg_id": forwarded.id,
            "user_id": message.from_user.id,
            "file_name": file_name,
            "stored_on": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        save_map(mapping)

        await message.reply_text(f"✅ File stored!\n🆔 Your ID: `{file_id}`")

    except Exception as e:
        logging.error(f"Store error: {e}")
        await message.reply_text(f"⚠️ Failed to store file:\n`{e}`")

# ✅ /getfile
@bot.on_message(filters.command("getfile"))
async def getfile(client, message):
    logging.info("Received /getfile command")
    args = message.text.split(" ", 1)

    if len(args) < 2:
        await message.reply_text("❌ Usage: /getfile <file_id>")
        return

    file_id = args[1].strip()
    mapping = load_map()

    if file_id in mapping:
        try:
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=mapping[file_id]["msg_id"]
            )
            logging.info(f"Sent file for ID: {file_id}")
        except Exception as e:
            logging.error(f"Retrieve error: {e}")
            await message.reply_text(f"⚠️ Could not retrieve the file:\n`{e}`")
    else:
        await message.reply_text("❌ File ID not found.")

# ✅ /myfiles — Only user's own files with ID, name & date
@bot.on_message(filters.command("myfiles"))
async def myfiles(client, message):
    user_id = message.from_user.id
    mapping = load_map()

    user_files = []
    for file_id, info in mapping.items():
        if isinstance(info, dict) and info.get("user_id") == user_id:
            user_files.append(
                f"🆔 `{file_id}`\n📄 {info.get('file_name', 'Unknown')}\n📅 {info.get('stored_on')}"
            )

    if not user_files:
        await message.reply_text("📭 You haven't stored any files yet.")
        return

    await message.reply_text(
        "📂 Your Stored Files:\n\n" + "\n\n".join(user_files),
        disable_web_page_preview=True
    )

# ✅ Start bot
bot.run()
