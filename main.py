import telebot
from TikTokApi import TikTokApi
import os

API_TOKEN = "7835872937:AAHmy808cQtDdMysSxlli_RlbVKOBkkyApA"
bot = telebot.TeleBot(API_TOKEN)

# Initialize TikTokApi with Playwright
api = TikTokApi()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send me a TikTok video link and I'll download it for you.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "Downloading your TikTok video, please wait...")

    try:
        # Use TikTokApi to get video bytes
        video = api.video(url=url)
        video_bytes = video.bytes()

        filename = "tiktok_video.mp4"
        with open(filename, 'wb') as f:
            f.write(video_bytes)

        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)

        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, "Failed to download video. Please check the link and try again.")
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()
