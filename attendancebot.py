import telebot
from telebot import types
import time
from datetime import datetime

# Yahan apna API TOKEN dalein
API_TOKEN = '8892935176:AAGvliwhNMZi33vfUAEiIJB74FUj7hxaIn4'
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

def get_time():
    return datetime.now().strftime("%I:%M %p") # 12-hour format (e.g., 01:20 AM)

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Start Work 🟢", callback_data='work_start'),
        types.InlineKeyboardButton("Off Work 🔴", callback_data='work_off'),
        types.InlineKeyboardButton("Break ☕", callback_data='break_start'),
        types.InlineKeyboardButton("Smoke Break 🚬", callback_data='smoke_start')
    )
    return markup

def back_menu(user_id):
    markup = types.InlineKeyboardMarkup()
    # Button ke callback_data mein user_id save kar rahe hain taake koi doosra banda aapka button click na kar sake
    markup.add(types.InlineKeyboardButton("Back to Seat 💺", callback_data=f'back_{user_id}'))
    return markup

# Is command se group mein menu open hoga
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "🏢 *Office Management System Active*\nApni activity update karne ke liye neeche diye gaye buttons use karein:", 
        reply_markup=main_menu(), 
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    name = call.from_user.first_name
    current_time = time.time()
    readable_time = get_time()

    if call.data == 'work_start':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🟢 *{name}* started work at *{readable_time}*", parse_mode="Markdown")

    elif call.data == 'work_off':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔴 *{name}* is OFF work at *{readable_time}*", parse_mode="Markdown")

    elif call.data in ['break_start', 'smoke_start']:
        break_type = "Break ☕" if call.data == 'break_start' else "Smoke Break 🚬"
        user_data[user_id] = current_time 
        
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id, 
            f"⏳ *{name}* went on *{break_type}* at *{readable_time}*", 
            reply_markup=back_menu(user_id), 
            parse_mode="Markdown"
        )

    elif call.data.startswith('back_'):
        # Jisne button dabaya kya yeh usi ki break thi?
        allowed_user_id = int(call.data.split('_')[1])
        
        if user_id != allowed_user_id:
            bot.answer_callback_query(call.id, "Yeh button aapke liye nahi hai! ❌", show_alert=True)
            return

        if user_id in user_data:
            start_time = user_data[user_id]
            duration = round((current_time - start_time) / 60, 2)
            del user_data[user_id]
            
            bot.answer_callback_query(call.id, "Welcome back!")
            bot.send_message(
                call.message.chat.id, 
                f"💺 *{name}* is back on seat at *{readable_time}*.\n⏱ Total duration: *{duration} minutes*.", 
                parse_mode="Markdown"
            )
            # Purane 'Back to seat' wale message ko delete kar dete hain taake group saaf rahe
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "Koi active timer nahi mila.", show_alert=True)

print("Bot group ke liye ready hai...")
bot.infinity_polling()
