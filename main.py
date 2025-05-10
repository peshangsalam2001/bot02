import telebot
import yt_dlp
import os

# Replace with your bot token
BOT_TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'
bot = telebot.TeleBot(BOT_TOKEN)

# Function to download Facebook video using yt-dlp
def download_facebook_video(url):
    output_file = 'video.mp4'
    ydl_opts = {
        'cookies': 'fb_cookies.txt',  # Ensure this file exists
        'outtmpl': output_file,
        'format': 'best',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_file
    except Exception as e:
        print("Download error:", e)
        return None

# Handle all messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()

    if "facebook.com" not in url:
        bot.reply_to(message, "❌ Please send a valid Facebook video link.")
        return

    msg = bot.reply_to(message, "⏬ Downloading video... please wait.")
    video_path = download_facebook_video(url)

    if video_path and os.path.exists(video_path):
        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove(video_path)
    else:
        bot.send_message(message.chat.id, "❌ Failed to download. Make sure your cookies allow access or the video is public.")

bot.polling()
