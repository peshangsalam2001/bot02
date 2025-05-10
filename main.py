import telebot
import requests
import re
import os
import tempfile

API_TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'  # Replace with your Telegram bot token
bot = telebot.TeleBot(API_TOKEN)

def extract_video_url(fb_url, quality='hd'):
    """
    Extract Facebook video direct URL (HD or SD) from the Facebook video page URL.
    quality: 'hd' or 'sd'
    Returns direct video URL or None if not found.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(fb_url, headers=headers)
        response.raise_for_status()
        html = response.text

        if quality == 'hd':
            video_url_match = re.search(r'hd_src:"([^"]+)"', html)
            if not video_url_match:
                # fallback to sd if hd not found
                video_url_match = re.search(r'sd_src:"([^"]+)"', html)
        else:
            video_url_match = re.search(r'sd_src:"([^"]+)"', html)

        if video_url_match:
            video_url = video_url_match.group(1).replace('\\/', '/')
            return video_url
        else:
            return None
    except Exception as e:
        print(f"Error extracting video URL: {e}")
        return None

def download_video(video_url, save_path):
    """
    Download video from direct URL to save_path.
    """
    try:
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me a Facebook video URL, and I will download the video for you in HD or SD quality.")

@bot.message_handler(func=lambda message: 'facebook.com' in message.text.lower())
def handle_facebook_url(message):
    url = message.text.strip()
    bot.send_message(message.chat.id, "⏳ Extracting video link and downloading, please wait...")

    video_url = extract_video_url(url, quality='hd')
    if not video_url:
        bot.send_message(message.chat.id, "❌ Could not find HD video, trying SD quality...")
        video_url = extract_video_url(url, quality='sd')

    if not video_url:
        bot.send_message(message.chat.id, "❌ Sorry, could not extract video URL. Make sure the link is public and valid.")
        return

    # Download video to a temp file
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = os.path.join(tmpdirname, 'facebook_video.mp4')
            success = download_video(video_url, filename)
            if success and os.path.exists(filename):
                with open(filename, 'rb') as video_file:
                    bot.send_video(message.chat.id, video_file)
            else:
                bot.send_message(message.chat.id, "❌ Failed to download the video.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ An error occurred: {str(e)}")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "Please send a valid Facebook video URL.")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
