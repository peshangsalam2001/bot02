import os
import re
import time
import json
import requests
import telebot
from telebot import types
import yt_dlp

TOKEN = "7595180485:AAELAJ6ZWq2x-S5ruuQzbmSG89zrDqZtvLU"  # Replace with your bot token
CHANNEL = "@KurdishBots"
ADMIN = "@MasterLordBoss"
OWNER_USERNAME = "MasterLordBoss"
USER_DATA_FILE = 'bot_users.json'

bot = telebot.TeleBot(TOKEN)

# Persistent user storage functions
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('users_started', []))
        except Exception:
            return set()
    return set()

def save_users(users):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users_started': list(users)}, f)

stats = {
    'users_started': load_users(),
    'valid_links': 0,
}

user_last_download_time = {}
awaiting_link = set()

TUTORIAL_VIDEO_URL = "https://media-hosting.imagekit.io/a031c091769643da/IMG_4141%20(1).MP4?Expires=1841246907&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=z6BkaPkTwhTwjl-QZw6VNroAuS7zbxxIboZclk8Ww1GTQpxK~M-03JNLXt5Ml6pReIyvxJGGKBGX60~uGI2S5Tev3QtMHz3hIa7iPTQIrfv1p32oTvwyycnFfvecpFAofB-4qGSvZ5YsynhnrpUJT-fH25ROpkGnj9xMo87KWlrd6E1G9sWP5PNwpnLkRMkoh2uZLyWA935JPLX0bJMRGdovqmrORlp7XvxoOom2vHg2zydq1JSDVDlbxGFsM3guN8GWSPSM-pfOymZfJY-r~ajDT8sD~fjDCUwji~zW~LCqLTYdwHhglJXmtOStjsmeXqn4JOU2Q85LtIM~LHRTgA__"

# Check if user is member of the channel
def is_member(user_id):
    try:
        return bot.get_chat_member(CHANNEL, user_id).status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# Check if text is a YouTube URL
def is_youtube_url(text):
    return re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+', text)

# Check if text is a TikTok URL
def is_tiktok_url(text):
    return re.match(r'https?://(www\.tiktok\.com|vt\.tiktok\.com|vm\.tiktok\.com)/.+', text)

# Main inline keyboard markup with single buttons as requested
def main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("کەناڵی سەرەکی", url="https://t.me/KurdishBots"))
    markup.row(types.InlineKeyboardButton("چۆنیەتی بەکارهێنانی بۆتەکە", callback_data='howto'))
    markup.row(types.InlineKeyboardButton("پەیوەندیم پێوەبکە", url=f"https://t.me/{ADMIN[1:]}"))
    return markup

# Welcome message
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in stats['users_started']:
        stats['users_started'].add(user_id)
        save_users(stats['users_started'])
    if is_member(user_id):
        name = message.from_user.first_name or ""
        text = (
            "بەخێربێن بۆ بۆتی داونلۆدکردنی ڤیدیۆ لەم پلاتفۆڕمانە (یوتوب، تیکتۆک) ✅\n\n"
            "تکایە جۆینی ئەم کەناڵە بکە بۆ ئاگاداربوون لە هەموو گۆڕانکاریەکانی بۆتەکە و بەدەستهێنانی چەندین بۆتی بەسوودی هاوشێوە 👑\n"
            "https://t.me/KurdishBots"
        )
        bot.send_message(message.chat.id, text, reply_markup=main_markup())
    else:
        bot.send_message(message.chat.id, f"ببورە، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")

@bot.message_handler(commands=['start', 'سەرەکی'])
def start_handler(message):
    send_welcome(message)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.username == OWNER_USERNAME:
        user_count = len(stats['users_started'])
        valid_links = stats['valid_links']
        text = (
            f"📊 نوێترین زانیاری بۆت:\n"
            f"👥 ژمارەی بەکارهێنەران: {user_count}\n"
            f"🎬 ژمارەی لینکی ڤیدیۆی دروست داواکراوە: {valid_links}\n"
            f"⏰ کاتی داواکاری: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "فەرمانەکە تەنها بۆ خاوەنی بۆتە.")

@bot.message_handler(commands=['post'])
def post_command(message):
    if message.from_user.username == OWNER_USERNAME:
        msg = bot.send_message(message.chat.id, "تکایە پەیامەکەت بنێرە تاکو منیش بینێرم بۆ بەکارهێنەران")
        bot.register_next_step_handler(msg, process_post)
    else:
        bot.delete_message(message.chat.id, message.message_id)

def process_post(message):
    if message.from_user.username == OWNER_USERNAME:
        sent = 0
        errors = 0
        for user_id in stats['users_started']:
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id, message.text)
                elif message.content_type == 'photo':
                    bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video':
                    bot.send_video(user_id, message.video.file_id, caption=message.caption)
                sent += 1
                time.sleep(0.5)
            except Exception:
                errors += 1
        bot.send_message(message.chat.id, f"✅ نێردرا بۆ {sent} بەکارهێنەر | شکستی هێنا بۆ {errors}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'howto':
        caption = "ئەم ڤیدیۆیە فێرکاری چۆنیەتی بەکارهێنانی بۆتەکەیە ✅"
        try:
            video_response = requests.get(TUTORIAL_VIDEO_URL, stream=True, timeout=60)
            if video_response.status_code == 200:
                bot.send_video(call.message.chat.id, video_response.content, caption=caption)
            else:
                bot.send_message(call.message.chat.id, "❌ نەتوانرا ڤیدیۆی ڕاهێنان باربکات.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ هەڵە لە ناردنی ڤیدیۆ: {str(e)}")

@bot.message_handler(commands=['download'])
def download_command(message):
    user_id = message.from_user.id
    if not is_member(user_id):
        bot.reply_to(message, f"ببورە، پێویستە سەرەتا جۆینی کەناڵەکەمان بکەیت:\n{CHANNEL}")
        return
    bot.send_message(message.chat.id, "تکایە لینکی یوتوب یان تیکتۆک بنێرە تاکو داونلۆدی بکەم بۆت")
    awaiting_link.add(user_id)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""

    if user_id in awaiting_link:
        awaiting_link.discard(user_id)
        if not (is_youtube_url(text) or is_tiktok_url(text)):
            bot.reply_to(message, "ببورە لینکەکە دروست نیە، تکایە دڵنیابەرەوە لە لینکەکەت پاشان بینێرە ❌")
            return
        now = time.time()
        last_time = user_last_download_time.get(user_id, 0)
        if now - last_time < 15:
            bot.reply_to(message, "تکایە ١٥ چرکە چاوەڕوانبە پاشان لینکێکی نوێ بنێرە 🚫")
            return
        user_last_download_time[user_id] = now
        stats['valid_links'] += 1
        if is_youtube_url(text):
            download_youtube(message, text)
        else:
            download_tiktok(message, text)
    else:
        if text.lower() in ['/start', 'سەرەکی']:
            send_welcome(message)
        elif text.lower() == '/download':
            download_command(message)
        else:
            bot.reply_to(message,
                         "بۆ گەڕانەوە بۆ لیستی سەرەکی /start بنێرە\n\n"
                         "بۆ داونلۆدکردنی ڤیدیۆی یوتوب یان تیکتۆک /download بنێرە\n")

def download_youtube(message, url):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ چاوەڕوانبە، ڤیدیۆکەت دابەزێنرێت...")
    # Use yt-dlp with playlist-aware output naming
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best/best',
        'outtmpl': 'downloads/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': False,
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # If playlist, send videos one by one
            if 'entries' in info:
                videos = info['entries']
            else:
                videos = [info]
            for idx, video in enumerate(videos, start=1):
                file_path = ydl.prepare_filename(video)
                if os.path.exists(file_path) and os.path.getsize(file_path) <= 50 * 1024 * 1024:
                    with open(file_path, 'rb') as f:
                        bot.send_video(chat_id, f, caption=f"✅ ڤیدیۆکەت بە سەرکەوتوویی داونلۆدکرا!\n{video.get('title', '')}")
                    os.remove(file_path)
                else:
                    bot.send_message(chat_id, f"❌ ڤیدیۆی ژمارە {idx} لە لیستەکە قەبارەیەکی زۆر گەورە هەیە یان نەدۆزرایەوە.")
            bot.delete_message(chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ هەڵە ڕوویدا لە داونلۆدکردن: {str(e)}", chat_id, msg.message_id)

def get_tiktok_api_links(tiktok_url):
    api_url = f"https://tikwm.com/api/?url={tiktok_url}"
    try:
        res = requests.get(api_url, timeout=30).json()
        if not res.get("data"):
            return []
        qualities = []
        for key in ['play', 'play_1080p', 'play_720p', 'play_480p', 'play_360p']:
            link = res["data"].get(key)
            if link:
                qualities.append(link)
        return qualities
    except Exception:
        return []

def download_tiktok(message, url):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ چاوەڕوانبە، ڤیدیۆکەت دابەزێنرێت...")
    qualities = get_tiktok_api_links(url)
    if not qualities:
        bot.edit_message_text("لینکەکەت هەڵەیە، تکایە دڵنیابەرەوە لە لینکەکەت پاشان بینێرە ❌", chat_id, msg.message_id)
        return
    for video_url in qualities:
        try:
            video_response = requests.get(video_url, timeout=60)
            if video_response.status_code == 200:
                file_size = len(video_response.content)
                if file_size <= 50 * 1024 * 1024:
                    caption = ("بەسەرکەوتوویی ڤیدیۆکە بە بەرزترین کوالیتی داونلۆدکرا ✅\n"
                               "بۆ ئەوەی چەندین بۆتی هاوشێوەت دەستکەوێ تکایە سەردانی @KurdishBots بکە")
                    bot.send_video(chat_id, video_response.content, caption=caption)
                    bot.delete_message(chat_id, msg.message_id)
                    return
        except Exception:
            continue
    bot.edit_message_text("قەبارەی ئەم ڤیدیۆیە لە 50MB زیاترە بۆیە داونلۆد ناکرێ:", chat_id, msg.message_id)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    bot.infinity_polling()