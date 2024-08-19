import json
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Bot tokeni
TOKEN = 'YOUR_BOT_API_TOKEN'


# Admin foydalanuvchi ID sini bu yerga qo'ying
ADMIN_ID = 123456789  # O'z ID'ingizni kiriting

# Botni sozlash
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# JSON faylidan savollar va javoblarni yuklash
with open("questions.json", "r", encoding="utf-8") as file:
    qa_data = json.load(file)

# Tugmalar menyusi yaratish
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [KeyboardButton(question) for question in qa_data.keys()]

# Buttons in pairs
for i in range(0, len(buttons), 2):
    main_menu.add(*buttons[i:i+2])

# Foydalanuvchi ma'lumotlarini saqlash funktsiyasi
def save_user_info(user_id, user_name, user_full_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
    ''')
    cursor.execute('INSERT OR REPLACE INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                   (user_id, user_name, user_full_name))
    conn.commit()
    conn.close()

# Start komandasi
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    user_full_name = message.from_user.full_name
    
    # Foydalanuvchi ma'lumotlarini saqlash
    save_user_info(user_id, user_name, user_full_name)
    
    response = (f"Salom, {user_full_name}!\n"
                "Men kiberxavfsizlik bo'yicha botman. Botdan foydalanish uchun tugmalar orqali savollarni tanlang yoki /help buyrug'ini kiriting.")
    await message.reply(response, reply_markup=main_menu)

# Help komandasi
@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = (
        "🛡️ @CyberSec_Salikha_bot haqida:\n\n"
        "Bu bot kiberxavfsizlik haqida ma'lumot olish uchun yaratilgan. Siz quyidagi savollarni so'rashingiz mumkin:\n"
        "1. 🛡️Kiberxavfsizlik haqida\n"
        "2. 🔍 Axborot xavfsizligi\n"
        "3. 🛡️ Tarmoq xavfsizligi\n"
        "4. 🦠 Viruslar haqida\n"
        "5. 🛡️Viruslardan qanday himoyalanish mumkin?\n"
        "6. ⚠️ Kiberhujumdan keyingi chora-tadbirlar\n"
        "7. 🛑 Ransomware haqida\n"
        "8. 📚Kiberxavfsizlikda ishlatiladigan atamalar\n"
        "9. 🔍 Xavfsizlik muammolari va hujumlar qanday aniqlanadi?\n"
        "10.📱IT_ga_doir_foydali_botlar\n\n"
        
        "❗️Botdan foydalanish uchun tugmalar orqali savollarni tanlang👇"
        
    )
    await message.reply(help_text)

# Savollarga javob berish
@dp.message_handler()
async def answer_question(message: types.Message):
    question = message.text.strip()
    answer = qa_data.get(question,  "❌ Noma'lum buyruq!\n\n"
                         "Siz to'g'ridan-to'g'ri bot chatiga xabar yubordingiz, yoki "
                         "bot tuzilishi yaratuvchisi tomonidan o'zgartirilgan bo'lishi mumkin.\n\n"
                         "ℹ️ Xabarlarni to'g'ridan-to'g'ri botga yubormang yoki "
                         "/start orqali bot menyusini yangilang.")
    await message.reply(answer)

# Foydalanuvchi ma'lumotlarini ko'rsatish
@dp.message_handler(commands=['status'])
async def status(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Sizda bu komanda uchun ruxsat yo'q.")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, full_name FROM users')
    users = cursor.fetchall()
    conn.close()

    if users:
        response = "Foydalanuvchi ma'lumotlari:\n"
        for user in users:
            user_id, username, full_name = user
            response += (f"ID: {user_id}\n"
                         f"Username: {username}\n"
                         f"Full Name: {full_name}\n\n")
    else:
        response = "Foydalanuvchi ma'lumotlari topilmadi."

    await message.reply(response)

# Botni ishga tushirish
async def on_startup(dp):
    admin_message = "Bot ishga tushdi."
    await bot.send_message(ADMIN_ID, admin_message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)




