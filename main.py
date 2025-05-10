import telebot
from facebook_downloader import FacebookDownloader
import os

API_TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'  # Replace with your Telegram bot token
bot = telebot.TeleBot(API_TOKEN)

# Create FacebookDownloader instance
fb_downloader = FacebookDownloader()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me a Facebook video URL, and I will download it for you.")

@bot.message_handler(func=lambda message: 'facebook.com' in message.text.lower())
def handle_facebook_url(message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "Downloading your Facebook video, please wait...")

    try:
        # Create a temporary directory to store the downloaded video
        download_dir = "temp_videos"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Set the output path for the downloaded video
        output_path = os.path.join(download_dir, "facebook_video.mp4")

        # Download the Facebook video using facebook-downloader
        fb_downloader.download(url, output_path=output_path)

        if os.path.exists(output_path):
            with open(output_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
            # Clean up the downloaded file
            os.remove(output_path)
        else:
            bot.send_message(message.chat.id, "Sorry, I couldn't download the video. Please check the URL or try again later.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

bot.infinity_polling()
