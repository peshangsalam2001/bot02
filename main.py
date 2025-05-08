import telebot
from tiktok import TikTokApi  # adjust if your package name differs
import os

API_TOKEN = '7835872937:AAHmy808cQtDdMysSxlli_RlbVKOBkkyApA'
bot = telebot.TeleBot(API_TOKEN)

# Initialize TikTok API client
api = TikTokApi()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Send me a TikTok video link, and I'll download the video for you.")

@bot.message_handler(func=lambda message: True)
def download_tiktok_video(message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "⏳ Downloading your TikTok video, please wait...")

    try:
        # Extract video ID from URL
        video_id = url.split("/video/")[1].split("?")[0]

        # Download video bytes
        video_bytes = api.video(id=video_id).bytes()

        # Save video temporarily
        filename = f"{video_id}.mp4"
        with open(filename, 'wb') as f:
            f.write(video_bytes)

        # Send video file to user
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)

        # Remove temp file
        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Failed to download video. Please make sure the link is valid.")
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()
