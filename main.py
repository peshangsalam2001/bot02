import telebot
from facebook_downloader import FacebookDownloader
import os
import re

API_TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'  # Replace with your bot token
bot = telebot.TeleBot(API_TOKEN)
fb_downloader = FacebookDownloader()

# Regex to detect Facebook URLs
facebook_url_pattern = re.compile(r'(https?://)?(www\.)?(facebook|fb)\.(com|watch)/[^\s]+')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Send me any Facebook video, reel, or story link and I will download it for you!")

@bot.message_handler(func=lambda message: facebook_url_pattern.search(message.text))
def handle_facebook_video(message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "📥 Downloading your Facebook video, please wait...")

    try:
        # Temporary directory for video
        temp_dir = "downloads"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        output_path = os.path.join(temp_dir, "fb_video.mp4")
        fb_downloader.download(url, output_path=output_path)

        if os.path.exists(output_path):
            with open(output_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove(output_path)
        else:
            bot.send_message(message.chat.id, "❌ Failed to download the video. Please try again with a different link.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {str(e)}")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(message.chat.id, "❗ Please send a valid Facebook video/reel/story link.")

bot.infinity_polling()
