import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inisialisasi bot dengan token
bot = telebot.TeleBot('7948488750:AAE3QcUF0TcXx43iTiNFG9n-9q4okxXZIbM')

# Fungsi untuk menampilkan menu utama sebagai inline keyboard
def send_main_menu(message):
    markup = InlineKeyboardMarkup()
    btn_xl = InlineKeyboardButton('XL', callback_data='XL')
    btn_telkomsel = InlineKeyboardButton('TELKOMSEL', callback_data='TELKOMSEL')
    btn_axis = InlineKeyboardButton('AXIS', callback_data='AXIS')
    btn_indosat = InlineKeyboardButton('INDOSAT', callback_data='INDOSAT')
    markup.add(btn_xl, btn_telkomsel, btn_axis, btn_indosat)
    
    bot.send_message(message.chat.id, "Pilih provider:", reply_markup=markup)

# Fungsi untuk mengambil dan menampilkan isi file dari URL
def get_file_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Gagal mengambil data dari file."

# Menangani pesan /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_main_menu(message)

# Menangani callback dari inline keyboard
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'XL':
        url = 'https://raw.githubusercontent.com/Andraxvpn/Andrax-script/main/DATA/XL.txt'
        file_content = get_file_content(url)
        bot.send_message(call.message.chat.id, f"Berikut data XL:\n\n{file_content}")
    elif call.data == 'TELKOMSEL':
        url = 'https://raw.githubusercontent.com/Andraxvpn/Andrax-script/main/DATA/TELKOMSEL.txt'
        file_content = get_file_content(url)
        bot.send_message(call.message.chat.id, f"Berikut data TELKOMSEL:\n\n{file_content}")
    elif call.data == 'AXIS':
        url = 'https://raw.githubusercontent.com/Andraxvpn/Andrax-script/main/DATA/AXIS.txt'
        file_content = get_file_content(url)
        bot.send_message(call.message.chat.id, f"Berikut data AXIS:\n\n{file_content}")
    elif call.data == 'INDOSAT':
        url = 'https://raw.githubusercontent.com/Andraxvpn/Andrax-script/main/DATA/INDOSAT.txt'
        file_content = get_file_content(url)
        bot.send_message(call.message.chat.id, f"Berikut data INDOSAT:\n\n{file_content}")

# Jalankan bot
bot.polling()
