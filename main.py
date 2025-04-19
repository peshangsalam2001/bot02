import telebot
from telebot import types
import json
import os

TOKEN = '7007340673:AAEhp1W1PhoUq_rOcssQVDIvq0OZVEXHARM'
bot = telebot.TeleBot(TOKEN)

user_data_file = 'user_data.json'

def load_user_data():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(user_data_file, 'w') as file:
        json.dump(data, file)

user_data = load_user_data()

course_prices = {
    "کۆرسی مایکرۆسۆفت ئێکسڵ": 30,
    "کۆرسی زمانی پایسۆن": 20,
    "کۆرسی مایکرۆسۆفت ئەکسس": 10
}

course_links = {
    "کۆرسی مایکرۆسۆفت ئێکسڵ": "https://t.me/AboutMasterLord",
    "کۆرسی زمانی پایسۆن": "https://t.me/AboutMasterLord",
    "کۆرسی مایکرۆسۆفت ئەکسس": "https://t.me/AboutMasterLord"
}

def get_main_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("کۆرسەکان", callback_data="courses"),
        types.InlineKeyboardButton("کۆینەکانم", callback_data="coins")
    )
    keyboard.row(
        types.InlineKeyboardButton("لینکی بانگهێشتنامە", callback_data="invite"),
        types.InlineKeyboardButton("هەموو بۆتەکانم", callback_data="all_bots")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {"coins": 0, "invited": []}
        save_user_data(user_data)

    if message.text and message.text.startswith("/start "):
        ref_id = message.text.split()[1]
        if ref_id != user_id and ref_id in user_data:
            if user_id not in user_data[ref_id]["invited"]:
                user_data[ref_id]["coins"] += 1
                user_data[ref_id]["invited"].append(user_id)
                save_user_data(user_data)
                bot.send_message(ref_id, f"👤 کەسێک بە لینکە بانگهێشتنامەکەتەوە هاتە ناو بۆتەکە، 1 کۆینت زیادبوو 🪙\n\n👛 ژمارەی کۆینەکانت: {user_data[ref_id]['coins']}")

    photo_url = 'https://i.ibb.co/dJtHr9p/welcome.jpg'  # Replace with your actual image URL or local file
    caption = "بەخێربێیت بۆ بۆتی فێرکاری 📚\n\nتکایە یەکێک لە دوگمەکان هەلبژێرە"
    bot.send_photo(message.chat.id, photo=photo_url, caption=caption, reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = str(call.from_user.id)

    if call.data == "courses":
        markup = types.InlineKeyboardMarkup()
        for name, price in course_prices.items():
            markup.add(types.InlineKeyboardButton(f"{name} - {price} کۆین", callback_data=f"buy_{name}"))
        markup.add(types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back"))
        bot.edit_message_text("📚 ئەمە لیستی کۆرسەکانە:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "coins":
        coins = user_data.get(user_id, {}).get("coins", 0)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back"))
        bot.edit_message_text(f"👛 ژمارەی کۆینەکانت: {coins}", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "invite":
        invite_link = f"https://t.me/Bot02PA_Bot?start={user_id}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back"))
        bot.edit_message_text(f"🔗 ئەمە لینکە بانگهێشتنامەکەتە:\n{invite_link}", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "all_bots":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back"))
        bot.edit_message_text("🤖 لیستی بۆتەکان بەزودی زیاد دەکرێت...", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back":
        photo_url = 'https://i.ibb.co/dJtHr9p/welcome.jpg'  # Replace if needed
        caption = "بەخێربێیت بۆ بۆتی فێرکاری 📚\n\nتکایە یەکێک لە دوگمەکان هەلبژێرە"
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo_url, caption=caption),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_main_keyboard()
        )

    elif call.data.startswith("buy_"):
        course_name = call.data[4:]
        price = course_prices[course_name]
        if user_data[user_id]["coins"] >= price:
            bot.edit_message_text(f"🎉 پیرۆزە بەڕێز، ئەمە کۆرسەکەیە:\n{course_links[course_name]}", call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text("❗️ ببورە بڕی پێویست لە کۆینت نیە بۆ کڕینی ئەم کۆرسە، تکایە کۆینەکانت زیادبکە لەڕێگەی لینکی بانگهێشتنامە یاخود کڕینی کۆین.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
