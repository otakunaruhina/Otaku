import os
import json
import random
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Setup ---
BOT_TOKEN = "7741081514:AAHk8WGnO31vD8zIcXZe5lsrR5gVa38Pqic"
WEATHER_API_KEY = "fc24205924275bbee9d542d34750177c"
DB_FILE = "file_store.json"

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Fact List (shortened for space) ---
facts = [
    "🌊 Prithvi ki zyada tar oxygen oceans se aati hai.",
    "🧬 Human body me 206 hadiyan hoti hain, lekin newborn me 300 ke kareeb hoti hain.",
    "🧠 Dimag body ki energy ka 20% use karta hai.",
    "🌕 Chand par din me 127°C aur raat me -173°C hota hai.",
    "🚀 Space me koi sound nahi hota kyunki wahan hawa nahi hoti.",
    "🪐 Shani ke ring barf aur pathar se bane hote hain.",
    "🦒 Giraffe ki jeebh kaali hoti hai taaki dhup se bach sake.",
    "🐘 Haathi ek matra jaanwar hai jo kabhi nahi koodta.",
    "🐦 Hummingbird duniya ka eklauta bird hai jo reverse me udd sakta hai.",
    "🍯 Shudh shahad kabhi kharab nahi hota.",
    "🗿 Statue of Unity duniya ki sabse oonchi murti hai - 182 meter.",
    "📧 Pehla email 1971 me bheja gaya tha.",
    "🦓 Har zebra ki stripe unique hoti hai – bilkul fingerprint ki tarah.",
    "🐢 Kuch turtles apni butt se saans le sakte hain!",
    "🎈 Helium earth par limited hai – khatam bhi ho sakta hai!",
    "🧠 Brain pain feel nahi karta – wo sirf signals process karta hai.",
    "🐬 Dolphins ek aankh khol ke sote hain.",
    "🦑 Squid ke paas 3 dil hote hain!",
    "🐓 Rooster bina light ke bhi apna internal alarm follow karta hai.",
    "🎮 Gaming se hand-eye coordination improve hota hai.",
    "🍇 Grapes microwave me spark karte hain – electricity ki wajah se.",
    "🧊 Cold water peene se body zyada calories burn karti hai.",
    "🕵️‍♂️ Fingerprints sirf humans ke nahi – koalas ke bhi unique hote hain.",
    "🌈 Rainbow gol hota hai, lekin zameen se aadha hi dikhta hai.",
    "📚 Reading stress ko 68% tak kam karta hai.",
    "🔥 Fire zero gravity me gol shape ka hota hai.",
    "🧬 DNA ka structure double helix 1953 me discover hua.",
    "🌖 Moon pe footprints lakhon saal tak rehenge kyunki wahan hawa nahi hai.",
    "🧼 Handwash se 80% germs remove hote hain.",
    "📱 Aaj ka smartphone Apollo mission ke computer se zyada powerful hai.",
    "🐘 Haathi dusre haathiyon ke death pe mourning karte hain.",
    "🔋 Lithium-ion battery 1970s me invent hui thi.",
    "🧊 Snow colorless hoti hai, lekin white dikhti hai kyunki light reflect hoti hai.",
    "🎶 Music plants ke growth ko bhi affect karta hai!",
    "🛰 GPS satellites ko Einstein ki relativity theory ke hisaab se adjust kiya jata hai.",
    "🌳 Ek mature tree ek din me 200 liters tak paani evaporate karta hai.",
    "🎇 Sabse pehla firework 7th century me China me bana tha.",
    "🐍 Saap apne kaan se nahi sunte, wo vibrations feel karte hain.",
    "🦅 Eagle 3 km door tak ka shikar dekh sakta hai.",
    "📷 Pehla camera photo lene me 8 ghante leta tha.",
    "🦁 Male lion din me 20 ghante tak sota hai.",
    "📖 Shakespeare ne 1700 naye words English me banaye.",
    "💡 Edison ne 1000 se zyada fail experiments ke baad bulb banaya.",
    "🌐 Pehla web page 1991 me publish hua tha.",
    "🌡 Garm paani thande paani se jaldi freeze ho sakta hai – isse Mpemba effect kehte hain.",
    "🧃 Tetra pack 1951 me invent hua tha.",
    "🧼 Soap virus ki outer layer tod deta hai – isliye effective hota hai.",
    "🐟 Fish bhi sote hain, bas unki aankhen band nahi hoti.",
    "🍀 Lucky clover 1 in 10,000 chance se milta hai.",
    "🧠 Brain kabhi rest mode me nahi jaata – sote waqt bhi active rehta hai.",
    "📡 Radio waves light ke comparison me slow nahi – dono same speed se travel karte hain.",
    "🦠 1 gram soil me 1 billion bacteria hote hain!",
    "🚽 Aadmi apni life ke 3 saal toilet me guzarta hai.",
    "🎂 Birthday cake tradition sabse pehle Egypt me shuru hua tha.",
    "👃 Smell memory se closely linked hota hai.",
    "🖐 Aapke dono haath ke nails alag speed se grow karte hain.",
    "🍎 Apple paani me float karta hai kyunki usme 25% hawa hoti hai.",
    "🦴 Haddi ka 31% weight calcium ka hota hai.",
    "🧪 Vinegar aur baking soda milake carbon dioxide gas banti hai.",
    "🚗 Pehla car accident 1891 me hua tha.",
    "🌐 WWW ka invention Tim Berners-Lee ne 1989 me kiya tha.",
    "🎧 Music sunne se memory aur focus dono improve hote hain.",
    "🌧 Rain transparent hoti hai – grey clouds ka illusion usse grey dikhata hai.",
    "🧊 Ice agar bubble-free ho to zyada transparent hoti hai.",
    "🧬 Human DNA 99.9% dusre insaan se match karta hai.",
    "🧠 Brain average 50,000 thoughts per day generate karta hai.",
    "🎓 Einstein ne light speed ko constant maana – isse relativity theory bani.",
    "🎈 Sabse pehla helium balloon 1824 me udaaya gaya tha.",
    "🧠 Aapka brain har second 100,000 chemical reactions karta hai.",
    "🍫 Chocolate dogs ke liye poisonous hoti hai.",
    "🦜 Parrots dusre parrots ke naam yaad rakhte hain.",
    "🐦 Penguins udd nahi sakte, par excellent swimmers hote hain.",
    "📖 Padhai karte waqt background music concentration badha sakta hai.",
    "🌐 Internet ka pehla message sirf 'LO' tha – LOGIN likhne se pehle crash ho gaya tha.",
    "🖥 Mouse ka invention 1964 me Douglas Engelbart ne kiya tha.",
    "🧠 Human brain 75% paani se bana hota hai.",
    "🪐 Pluto ab officially planet nahi – dwarf planet hai.",
    "🐾 Octopus ke paas 3 dil aur 9 dimaag hote hain!",
    "🎶 Music heart rate aur blood pressure ko control karne me madad karta hai.",
    "🧃 Coconut paani ko emergency IV fluid ke roop me use kiya gaya hai.",
    "🦋 Butterfly apne pairon se taste karti hai.",
    "🧼 Har bar handwash se 2 million germs hatte hain!",
    "💨 Human sneezing speed 160 km/h tak ho sakti hai.",
    "🐝 Bees geometry ke master hote hain – hexagon shape sabse efficient hoti hai.",
    "🌋 Volcano lightning tab hoti hai jab ash particles static electricity generate karte hain.",
    "🪶 Owl ki aankhen move nahi karti – isliye uska pura sir rotate karta hai.",
    "🐿 Squirrels trees ke liye thousands nuts chhupate hain – sab yaad nahi rakh pate.",
    "🧠 Brain multitasking me nahi, fast switching me expert hai.",
    "🧃 Orange juice brushing ke turant baad bitter lagta hai – toothpaste ke surfactant ki wajah se.",
    "🕰 Time travel theoretically possible hai – Einstein ki theory ke mutabik.",
    "🦷 Teeth enamel human body ka sabse hard substance hai.",
    "🌍 Earth ka magnetic pole change hota rehta hai – reversal ka proof mil chuka hai.",
    "🚶‍♂️ Walking 30 minutes daily heart health improve karta hai.",
    "🛌 Insomnia se brain shrink hone ka risk badhta hai.",
    "🦟 Mosquito logon ko unki blood type aur body smell ke basis pe chunte hain.",
    "🧼 20 second ka handwash viruses destroy karta hai – WHO ka guideline.",
    "🌌 Universe ka 95% hissa dark matter aur dark energy hai – jo invisible hai.",
    "🧠 Left aur right brain ka concept oversimplified hai – dono parts milke kaam karte hain.",
    "🔭 Hubble telescope ko space me 1990 me launch kiya gaya tha.",
    "🪐 Saturn ke kuch moons oceans hide karte hain unki surface ke neeche.",
    "🧪 Vaccines immunity create karne ke liye weakened virus ya protein ka use karti hain.",
    "🚶‍♀️ Human body 600+ muscles se bani hoti hai!",
]

# --- File Store DB Init ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def generate_unique_id(length=8):
    chars = "0123456789abcdef"
    return "".join(random.choice(chars) for _ in range(length))

def save_file_to_db(file_id, file_type, file_name, user_id):
    with open(DB_FILE, "r") as f:
        data = json.load(f)

    while True:
        new_id = generate_unique_id()
        if new_id not in data:
            break

    data[new_id] = {
        "file_id": file_id,
        "type": file_type,
        "name": file_name,
        "user_id": user_id,
    }

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return new_id

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Namaste! Yeh bot kaafi kuch karta hai:\n"
        "/fact – Random interesting fact\n"
        "/ping – Bot check\n"
        "/toss – Coin toss\n"
        "/define [word] – Word definition\n"
        "/translate [text] – English to Hindi\n"
        "/get [id] – File wapas paane ke liye\n\n"
        "📁 Koi bhi file bhejo, main uska unique ID de dunga!"
    )

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(facts))

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is alive and running.")

async def toss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["🪙 Heads!", "🪙 Tails!"])
    await update.message.reply_text(result)

async def define(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📖 Usage: /define [word]")
        return

    word = context.args[0]
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(url)
        data = response.json()

        if isinstance(data, dict) and data.get("title") == "No Definitions Found":
            await update.message.reply_text("❌ Word not found.")
            return

        meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
        await update.message.reply_text(f"📚 {word}: {meaning}")

    except Exception:
        await update.message.reply_text("⚠️ Error while fetching definition.")

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🌐 Usage: /translate [text]")
        return

    text = " ".join(context.args)

    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": "en|hi"}
        response = requests.get(url, params=params)
        data = response.json()

        translation = data["responseData"]["translatedText"]
        await update.message.reply_text(f"🔤 Hindi: {translation}")

    except Exception:
        await update.message.reply_text("⚠️ Error during translation.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id

    file = message.document or message.video or message.audio or (message.photo[-1] if message.photo else None)

    if file and hasattr(file, 'file_id'):
        file_id = file.file_id
        file_name = getattr(file, 'file_name', 'unnamed')
        file_type = type(file).__name__

        save_id = save_file_to_db(file_id, file_type, file_name, user_id)

        await message.reply_text(
            f"✅ File saved!\n🆔 Your File ID: `{save_id}`\n\nUse `/get {save_id}` to download later.",
            parse_mode="Markdown"
        )
    else:
        await message.reply_text("⚠️ Yeh file type support nahi karta ya file detect nahi hui.")

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ File ID do bhai. Usage: `/get <file_id>`", parse_mode="Markdown")
        return

    file_id = args[0]
    with open(DB_FILE, "r") as f:
        data = json.load(f)

    if file_id in data:
        file_info = data[file_id]
        ftype = file_info["type"]
        fid = file_info["file_id"]

        if ftype == "PhotoSize":
            await update.message.reply_photo(fid, caption=f"📸 Photo: {file_info['name']}")
        elif ftype == "Document":
            await update.message.reply_document(fid, caption=f"📄 Document: {file_info['name']}")
        elif ftype == "Video":
            await update.message.reply_video(fid, caption=f"🎥 Video: {file_info['name']}")
        elif ftype == "Audio":
            await update.message.reply_audio(fid, caption=f"🎵 Audio: {file_info['name']}")
        else:
            await update.message.reply_document(fid, caption=f"📁 File: {file_info['name']}")
    else:
        await update.message.reply_text("❌ File ID nahi mila, check karo sahi ID dali hai.", parse_mode="Markdown")

# --- Main ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("toss", toss))
    app.add_handler(CommandHandler("define", define))
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(CommandHandler("get", get_file))
    app.add_handler(MessageHandler(filters.ATTACHMENT | filters.PHOTO, handle_file))

    print("🤖 Bot chal raha hai...")
    app.run_polling()

if __name__ == "__main__":
    main()