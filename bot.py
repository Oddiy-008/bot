import datetime
import json
import random
import ssl
import threading
import time
import urllib.request

# Telefon uchun SSL xatoligini oldini olish
ssl._create_default_https_context = ssl._create_unverified_context

# Sizning ma'lumotlaringiz
Token = " 9152321709:AAHu6E6JTehh9-xtZwNTuuzU5SzlZpYwA90
ADMIN_ID = 8824238939
CHANNEL_ID = "@hammasi_yaxshi"

# 1. Qayg'uli va motivatsion so'zlar
QAYGULI_MOTIVATSIYA = [
    "Bugun yig'lagan bo'lsang, ertaga bundan-da kuchliroq bo'lasan.",
    "Yolg'izlik seni sindirmaydi, balki o'zingni topishingga yordam beradi.",
    "Har qorong'u kechaning albatta yorug' tongi bor, sabr qil.",
    "Og'riqlar vaqt o'tib unut bo'ladi, asosiysi taslim bo'lma.",
    "Taqdir sinovlari bizni chidamli qilish uchun beriladi.",
]

# 2. Chiroyli nasihatlar
NASIHATLAR = [
    "Ota-onangni qadrlang, ular abadiy yoningizda qolmaydi.",
    "Har kuningizni so'nggi kundek mazmunli yashang.",
    "Yaxshilik qiling va uni darhol unuting.",
    "Ilm olishdan aslo va aslo to'xtamang.",
    "Vaqt — eng qimmatbaho xazinadir.",
]

# 3. Videolar
VIDEOLAR = [
    "https://www.w3schools.com/html/mov_bbb.mp4",
]


# Telegramga So'rov yuborish funksiyasi
def send_telegram(method, data):
  url = f"https://api.telegram.org/bot{TOKEN}/{method}"
  req = urllib.request.Request(
      url,
      data=json.dumps(data).encode("utf-8"),
      headers={"Content-Type": "application/json"},
  )
  try:
    with urllib.request.urlopen(req, timeout=15) as response:
      return json.loads(response.read().decode("utf-8"))
  except Exception as e:
    print("Telegramga so'rov yuborishda xatolik:", e)
    return None


# Vaqtga mos kayfiyat
def get_time_greeting():
  hour = datetime.datetime.now().hour
  if 5 <= hour < 12:
    return "🌅 Ertalabki xayr! Kuningiz sokin va mazmunli o'tsin:"
  elif 12 <= hour < 18:
    return "☀️ Tushlik vaqti. Charchamayapsizmi, biroz nafas oling:"
  elif 18 <= hour < 23:
    return "🌙 Kechqurun muborak! Bugungi kunni sarhisob qiladigan payt:"
  else:
    return "🌌 Tun tinchligi va osoyishtaligi hamroh bo'lsin:"


# Matnni estetik uslubda bezash
def make_beautiful_text(raw_text):
  return (
      f"𓆩❤️𓆪 <b>{raw_text}</b>\n\n🖤 <i>«Hammasi Yaxshi» — Har bir lahzani"
      " qadrlang...</i>"
  )


pending_content = {"text": None, "type": None}


# Avtomatik jarayon (Har 2.5 soatda ruxsat so'rash)
def ask_admin_for_approval():
  global pending_content
  counter = 0

  while True:
    try:
      # 2.5 soat kutish
      time.sleep(2.5 * 3600)

      greeting = get_time_greeting()
      choice = counter % 3
      if choice == 0:
        text = random.choice(QAYGULI_MOTIVATSIYA)
        pending_content["text"] = f"{greeting}\n\n{make_beautiful_text(text)}"
        pending_content["type"] = "text"
        label = "Qayg'uli motivatsiya"
      elif choice == 1:
        text = random.choice(NASIHATLAR)
        pending_content["text"] = f"{greeting}\n\n{make_beautiful_text(text)}"
        pending_content["type"] = "text"
        label = "Chiroyli nasihat"
      else:
        pending_content["text"] = random.choice(VIDEOLAR)
        pending_content["type"] = "video"
        label = "Motivatsion video"

      counter += 1

      keyboard = {
          "inline_keyboard": [[
              {"text": "✅ Kanalga ruxsat berish", "callback_data": "approve"},
              {"text": "❌ Rad etish", "callback_data": "cancel"},
          ]]
      }

      msg_text = f"⚠️ <b>DIQQAT! Quyidagi {label} kanalga tashlanmoqchi. Ruxsat berasizmi?</b>\n\n{pending_content['text']}"
      send_telegram(
          "sendMessage",
          {
              "chat_id": ADMIN_ID,
              "text": msg_text,
              "parse_mode": "HTML",
              "reply_markup": keyboard,
          },
      )
    except Exception as e:
      print("Avtomatik poster xatoligi:", e)
      time.sleep(10)


# Botni ishga tushirish va uzluksiz himoya
def run_bot():
  offset = 0
  print("Bot muvaffaqiyatli ishga tushdi va himoyalandi!")
  while True:
    try:
      url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
      req = urllib.request.Request(url)
      with urllib.request.urlopen(req, timeout=35) as response:
        res = json.loads(response.read().decode("utf-8"))
        if res.get("ok"):
          for update in res.get("result", []):
            offset = update["update_id"] + 1

            if "callback_query" in update:
              cq = update["callback_query"]
              cq_id = cq["id"]
              data = cq["data"]
              chat_id = cq["message"]["chat"]["id"]
              msg_id = cq["message"]["message_id"]

              if data == "approve":
                if pending_content["type"] == "text":
                  send_telegram(
                      "sendMessage",
                      {
                          "chat_id": CHANNEL_ID,
                          "text": pending_content["text"],
                          "parse_mode": "HTML",
                      },
                  )
                elif pending_content["type"] == "video":
                  send_telegram(
                      "sendMessage",
                      {
                          "chat_id": CHANNEL_ID,
                          "text": (
                              "𓆩❤️𓆪 <b>Tavsiya qilingan"
                              f" video:</b>\n{pending_content['text']}"
                          ),
                          "parse_mode": "HTML",
                      },
                  )

                send_telegram(
                    "answerCallbackQuery",
                    {
                        "callback_query_id": cq_id,
                        "text": "Kanalga tashlandi!",
                    },
                )
                send_telegram(
                    "editMessageText",
                    {
                        "chat_id": chat_id,
                        "message_id": msg_id,
                        "text": "✅ Ruxsat berildi! Kontent kanalga tashlandi.",
                    },
                )
              elif data == "cancel":
                send_telegram(
                    "answerCallbackQuery",
                    {
                        "callback_query_id": cq_id,
                        "text": "Rad etildi.",
                    },
                )
                send_telegram(
                    "editMessageText",
                    {
                        "chat_id": chat_id,
                        "message_id": msg_id,
                        "text": (
                            "❌ Rad etildi. Kanalga hech narsa tashlanmadi."
                        ),
                    },
                )

            elif "message" in update:
              msg = update["message"]
              if "text" in msg:
                chat_id = msg["chat"]["id"]
                text = msg["text"]

                if chat_id == ADMIN_ID:
                  if text.startswith("/start"):
                    send_telegram(
                        "sendMessage",
                        {
                            "chat_id": ADMIN_ID,
                            "text": (
                                "Salom! Bot ishlayapti va 24/7 rejimga"
                                " tayyor. Menga istalgan matnni yozing, uni"
                                " siz so'ragan estetik uslubda bezab beraman."
                            ),
                        },
                    )
                  else:
                    styled = make_beautiful_text(text)
                    send_telegram(
                        "sendMessage",
                        {
                            "chat_id": ADMIN_ID,
                            "text": (
                                "✨ Mana siz yozgan matnning yangi"
                                f" ko'rinishi:\n\n{styled}"
                            ),
                            "parse_mode": "HTML",
                        },
                    )
    except Exception as e:
      print("Internet uzildi yoki xatolik, qayta ulanmoqda...", e)
      time.sleep(5)


if __name__ == "__main__":
  t = threading.Thread(target=ask_admin_for_approval)
  t.daemon = True
  t.start()

  run_bot()
