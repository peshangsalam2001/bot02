import telebot
import requests
from bs4 import BeautifulSoup

# Telegram Bot Token
BOT_TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'
bot = telebot.TeleBot(BOT_TOKEN)

# Start message
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "👋 Welcome!\nSend me any Facebook video or reel link, and I’ll fetch the download link for you.")

# Handle Facebook links
@bot.message_handler(func=lambda message: 'facebook.com' in message.text or 'fb.watch' in message.text)
def download_fb_video(message):
    fb_url = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        # Simulate browser POST to fdown.net
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'URLz': fb_url
        }

        response = requests.post('https://fdown.net/download.php', headers=headers, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract SD and HD download links
        buttons = soup.find_all('a', class_='btn')

        download_links = []
        for btn in buttons:
            quality = btn.text.strip()
            link = btn.get('href')
            if 'https://' in link:
                download_links.append((quality, link))

        # Send result
        if download_links:
            markup = telebot.types.InlineKeyboardMarkup()
            for quality, link in download_links:
                markup.add(telebot.types.InlineKeyboardButton(quality, url=link))
            bot.send_message(message.chat.id, "📥 Choose your download quality:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Could not find a downloadable video. Make sure it's public.")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "⚠️ Error occurred while processing the video.")

# Default reply
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(message.chat.id, "❗ Please send a valid Facebook video or reel link.")

bot.infinity_polling()
