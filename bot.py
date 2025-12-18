import telebot
from telebot import types
import random
import requests
import pyotp

# আপনার বোট টোকেন এখানে বসান
API_TOKEN = '7308877263:AAEuz6pumYmjbeMyJ76GBYGJVvnDLXiubY4'
bot = telebot.TeleBot(API_TOKEN)

# ১০০+ USA নামের লিস্ট (সংক্ষিপ্ত করে দেখানো হলো, আপনি চাইলে আরও বাড়াতে পারেন)
usa_names = [
    "James Smith", "Michael Johnson", "Robert Williams", "David Brown", "Richard Jones",
    "Joseph Garcia", "Thomas Miller", "Charles Davis", "Christopher Rodriguez", "Daniel Martinez",
    "Matthew Hernandez", "Anthony Lopez", "Mark Gonzalez", "Donald Wilson", "Steven Anderson",
    "Paul Thomas", "Andrew Taylor", "Joshua Moore", "Kenneth Jackson", "Kevin Martin",
    "Brian Lee", "George Perez", "Edward Thompson", "Ronald White", "Timothy Harris",
    "Jason Clark", "Jeffrey Lewis", "Ryan Robinson", "Jacob Walker", "Gary Young",
    "Mary Smith", "Patricia Johnson", "Jennifer Williams", "Linda Brown", "Elizabeth Jones",
    "Barbara Garcia", "Susan Miller", "Jessica Davis", "Sarah Rodriguez", "Karen Martinez",
    "Nancy Hernandez", "Margaret Lopez", "Sandra Gonzalez", "Ashley Wilson", "Dorothy Anderson",
    "Kimberly Taylor", "Emily Thomas", "Donna Moore", "Michelle Jackson", "Carol Martin",
    "Amanda Lee", "Melissa Perez", "Deborah Thompson", "Stephanie White", "Rebecca Harris",
    "Laura Clark", "Sharon Lewis", "Cynthia Robinson", "Kathleen Walker", "Amy Young",
    "John Doe", "Alex Murphy", "Brian Connor", "Justin Case", "Will Power", "Ray Gunn"
    # এভাবে ১০০+ নাম লিস্টে রাখতে পারেন
]

# মেইন মেনু কিবোর্ড (ক্যাটাগরি)
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton('🔐 2FA Generator')
    item2 = types.KeyboardButton('📧 Temp Mail')
    item3 = types.KeyboardButton('🇺🇸 USA Name Generator')
    markup.add(item1, item2, item3)
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "বোটটি চালু হয়েছে! নিচের মেনু থেকে অপশন সিলেক্ট করুন:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_logic(message):
    chat_id = message.chat.id

    # --- 2FA Generator ---
    if message.text == '🔐 2FA Generator':
        msg = bot.send_message(chat_id, "আপনার 2FA Secret Key টি পাঠান (Example: JBSW...):")
        bot.register_next_step_handler(msg, generate_2fa)

    # --- Temp Mail ---
    elif message.text == '📧 Temp Mail':
        res = requests.get("https://www.1secmail.com/api/v1/?action=genEmail&count=1").json()
        email = res[0]
        user, domain = email.split('@')
        
        inbox_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        inbox_markup.add(types.KeyboardButton(f"📥 Check Inbox:{user}:{domain}"))
        inbox_markup.add(types.KeyboardButton("🔙 Back to Main Menu"))
        
        bot.send_message(chat_id, f"✅ আপনার ইমেইল: `{email}`", parse_mode="Markdown", reply_markup=inbox_markup)

    # --- Inbox Check ---
    elif "📥 Check Inbox" in message.text:
        try:
            _, user, domain = message.text.split(':')
            url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}"
            msgs = requests.get(url).json()
            if not msgs:
                bot.send_message(chat_id, "📭 ইনবক্স খালি।")
            else:
                for m in msgs[:2]:
                    c_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={user}&domain={domain}&id={m['id']}"
                    data = requests.get(c_url).json()
                    bot.send_message(chat_id, f"📩 *From:* {data['from']}\n*Subject:* {data['subject']}\n\n{data['textBody']}", parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "❌ ত্রুটি হয়েছে!")

    # --- USA Name Generator ---
    elif message.text == '🇺🇸 USA Name Generator':
        names = random.sample(usa_names, 15) # এক ক্লিকে ১৫টি নাম দিবে
        response = "🇺🇸 **USA Random Names:**\n\n" + "\n".join([f"• {n}" for n in names])
        bot.send_message(chat_id, response, parse_mode="Markdown")

    # --- Back Menu ---
    elif message.text == '🔙 Back to Main Menu':
        bot.send_message(chat_id, "মেইন মেনু:", reply_markup=main_menu())

def generate_2fa(message):
    try:
        secret = message.text.replace(" ", "").upper()
        totp = pyotp.TOTP(secret)
        bot.reply_to(message, f"🔐 আপনার 2FA কোড: `{totp.now()}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ ভুল সিক্রেট কী! আবার চেষ্টা করুন।")

bot.polling()
