import telebot
import yt_dlp
import tempfile
import os

API_TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'  # Replace with your Telegram bot token
COOKIES_FILE = 'cookies.txt'  # Path to your Facebook cookies file

bot = telebot.TeleBot(API_TOKEN)

def download_facebook_video_with_cookies(url, cookies_path):
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookies_path,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # yt-dlp may merge to mp4, adjust filename if needed
            if not filename.endswith('.mp4'):
                base, ext = os.path.splitext(filename)
                mp4_filename = base + '.mp4'
                if os.path.exists(mp4_filename):
                    filename = mp4_filename
            return filename
    except Exception as e:
        print(f"Download error: {e}")
        return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                 "👋 Send me a Facebook video, reel, or story URL (private or public), "
                 "and I will download it for you using your Facebook cookies.")

@bot.message_handler(func=lambda message: 'facebook.com' in message.text.lower())
def handle_facebook_url(message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "⏳ Downloading your Facebook video, please wait...")

    if not os.path.exists(COOKIES_FILE):
        bot.send_message(message.chat.id,
                         "⚠️ Facebook cookies file not found on the server. "
                         "Please upload and configure it before using private video downloads.")
        return

    video_path = download_facebook_video_with_cookies(url, COOKIES_FILE)

    if video_path and os.path.exists(video_path):
        try:
            with open(video_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Failed to send the video.")
            print(f"Error sending video: {e}")
        finally:
            try:
                os.remove(video_path)
                os.rmdir(os.path.dirname(video_path))
            except Exception:
                pass
    else:
        bot.send_message(message.chat.id, "❌ Sorry, I couldn't download the video. Make sure the link is valid and your cookies allow access.")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "Please send a valid Facebook video, reel, or story URL.")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
