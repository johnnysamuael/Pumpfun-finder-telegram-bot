import websocket
import json
from datetime import datetime
import telebot
import requests

def format_timestamp(timestamp):
    try:
        if timestamp:
            return datetime.utcfromtimestamp(int(str(timestamp)[:10])).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "Will never be king"
    except (ValueError, OSError):
        return "Invalid timestamp"

def getKnownUsers():
    BOT_TOKEN='7376596462:AAFGJBeCoaa0H2diFQ6qQ_N3qJ-PJn2uZYk'

    bot = telebot.TeleBot(BOT_TOKEN)

    # Collect user IDs
    known_users = set()
    updates = bot.get_updates()
    for update in updates:
      if update.message and update.message.from_user:
        known_users.add(update.message.from_user.id)
    print(known_users)

def create_token_info_template(token_name, token_address, created_at_timestamp, kingHillTimeStamp, marketcap_usd, total_replies, website="", twitter="", telegram="", pump_fun=""):
    created_at = format_timestamp(created_at_timestamp)
    king_time = format_timestamp(kingHillTimeStamp)

    template = f"""
    Token Address: `{token_address}`

    Token Name : {token_name}
    ├ 🕒 Created at: {created_at}
    ├ 💰 Marketcap in USD (Should be above 10k!): {marketcap_usd}
    ├ 💬 Total replies: {total_replies}

    👑 KING: {king_time}

    🔗 SOCIALS
    ├ 🌐 Website: {website}
    ├ 🐦 Twitter: {twitter}
    ├ 📱 Telegram: {telegram}
    └ 💊 Pump Fun: {pump_fun}
    """
    return template

def on_message(ws, message):
    if message.startswith('42'):
        data = json.loads(message[2:])
        event = data[0]
        payload = data[1]

        marketcap = payload["usd_market_cap"]

        if event == "tradeCreated" and payload["creator"] == payload["user"] and not payload["is_buy"]:
            mint = payload["mint"]
            token_info = create_token_info_template(
                token_name=payload["name"],
                token_address=payload["mint"],
                created_at_timestamp=payload["created_timestamp"],  # Access the value directly
                kingHillTimeStamp=payload["king_of_the_hill_timestamp"],  # Access the value directly
                marketcap_usd=payload["usd_market_cap"],  # Access the value directly
                total_replies=payload["reply_count"],  # Access the value directly
                website=payload["website"],
                twitter=payload["twitter"],
                telegram=payload["telegram"],
                pump_fun=f"https://pump.fun/{mint}"
            )
            print(token_info)

            for user_id in ['284355239', '6195978436', '7133260701']:
                BOT_TOKEN='7376596462:AAFGJBeCoaa0H2diFQ6qQ_N3qJ-PJn2uZYk'
                bot = telebot.TeleBot(BOT_TOKEN)

                try:
                    bot.send_photo(user_id, payload["image_uri"], caption=token_info)
                except Exception as e:
                    try:
                      bot.send_message(user_id, token_info)
                    except Exception as e:
                      print("Cant send message")

    elif message.startswith('2'):
        ws.send("3")

def on_error(ws, error):
    print(json.dumps({"error": str(error)}))

def on_close(ws, close_status_code, close_msg):
    print(json.dumps({"close_status": close_status_code, "close_msg": close_msg}))

def on_open(ws):
    ws.send("40")

if __name__ == "__main__":
    getKnownUsers()
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://frontend-api.pump.fun/socket.io/?EIO=4&transport=websocket",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
