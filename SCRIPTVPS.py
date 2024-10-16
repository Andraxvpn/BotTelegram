import telebot
import requests
import base64
import re
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Token bot Telegram dan GitHub
TELEGRAM_TOKEN = '7681376852:AAHQ9Elz_1UgNR8KvJ9-8ktLH0NGwSE7q-A'
GITHUB_TOKEN = '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'
GITHUB_IP_URL = 'https://api.github.com/repos/Andraxvpn/Andrax-script/contents/izin'

# Inisialisasi bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Validasi format IP
def is_valid_ip(ip):
    pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return pattern.match(ip)

# Mengambil konten file dari GitHub
def fetch_github_file_content(url):
    try:
        response = requests.get(url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        response.raise_for_status()  # Raise an error for bad responses
        file_info = response.json()

        if 'content' in file_info:
            decoded_content = base64.b64decode(file_info['content']).decode('utf-8')
            logging.info("Konten berhasil diambil dari GitHub.")
            return decoded_content, file_info['sha']
        else:
            logging.error("Konten tidak ditemukan dalam respons GitHub.")
            return None, None
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Gagal mengambil konten: {str(e)}")
        return None, None

# Perbarui konten file di GitHub
def update_github_content(new_content, sha):
    try:
        updated_content_base64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        update_response = requests.put(
            GITHUB_IP_URL,
            json={
                'message': 'Memperbarui daftar IP',
                'content': updated_content_base64,
                'sha': sha
            },
            headers={'Authorization': f'token {GITHUB_TOKEN}'}
        )
        update_response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return False
    except Exception as e:
        logging.error(f"Gagal memperbarui konten: {str(e)}")
        return False

# Menu utama
@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("📝 DAFTAR IP", callback_data="IPVPS"))
    keyboard.add(telebot.types.InlineKeyboardButton("⚙️ SCRIPT VPS", callback_data="SCRIPT_VPS"))

    bot.send_message(message.chat.id,
                     "👋 **Selamat datang di Bot Manajemen IP!**\n"
                     "Silakan pilih opsi di bawah:",
                     reply_markup=keyboard)

# Opsi IPVPS
@bot.callback_query_handler(func=lambda call: call.data == "IPVPS")
def send_welcome(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🔗 Tambah IP", callback_data="add_ip_info"))
    keyboard.add(telebot.types.InlineKeyboardButton("📜 Lihat Daftar IP", callback_data="view_ip_list"))
    keyboard.add(telebot.types.InlineKeyboardButton("🗑️ Hapus IP", callback_data="delete_ip_info"))

    bot.reply_to(call.message,
                 "👋 **Selamat datang di IP Manager!**\n"
                 "Kelola alamat IP Anda dengan mudah dan cepat.\n\n"
                 "Silakan pilih opsi di bawah:",
                 reply_markup=keyboard)

# Tambah IP
@bot.callback_query_handler(func=lambda call: call.data == "add_ip_info")
def add_ip_info(call):
    bot.send_message(call.message.chat.id,
                     "💻 **Untuk menambahkan IP, gunakan format berikut:**\n"
                     "`/addip <tanggal_kedaluwarsa> <ip>`\n"
                     "Contoh: `/addip 2024-10-10 139.144.113.5`",
                     parse_mode='Markdown')

# Proses menambah IP
@bot.message_handler(commands=['addip'])
def handle_add_ip(message):
    try:
        # Memisahkan input menjadi argumen
        args = message.text.split()[1:]
        if len(args) != 2:
            raise ValueError("Format tidak valid. Pastikan Anda menggunakan format yang benar.")
        
        expiration, ip_address = args

        # Validasi format IP
        if not is_valid_ip(ip_address):
            bot.reply_to(message, "❌ **Alamat IP tidak valid.**")
            return

        # Ambil konten saat ini dari GitHub
        current_content, sha = fetch_github_file_content(GITHUB_IP_URL)
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        # Cek apakah IP sudah ada di daftar
        if ip_address in current_content:
            bot.reply_to(message, "❌ **IP sudah ada di daftar.**")
            return

        # Dapatkan username Telegram
        username = message.from_user.username or message.from_user.first_name

        # Format konten baru
        new_line = f"### {username} {expiration} {ip_address}\n"
        updated_content = current_content + new_line

        # Perbarui GitHub dengan konten baru
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **IP berhasil ditambahkan!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")
    except Exception as e:
        bot.reply_to(message, f"❌ **Terjadi kesalahan: {str(e)}**")

# Lihat daftar IP
@bot.callback_query_handler(func=lambda call: call.data == "view_ip_list")
def view_ip_list(call):
    current_content, _ = fetch_github_file_content(GITHUB_IP_URL)
    if current_content:
        ip_list = "📋 **Daftar IP Saat Ini:**\n\n"
       
        for line in current_content.splitlines():
            ip_list += line + "\n"

        if not ip_list.strip():
            ip_list = "❌ **Tidak ada IP yang tersedia.**"
       
        bot.send_message(call.message.chat.id, ip_list.strip(), parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, "❌ **Gagal mengambil daftar IP.**")

# Hapus IP
@bot.callback_query_handler(func=lambda call: call.data == "delete_ip_info")
def delete_ip_info(call):
    bot.send_message(call.message.chat.id,
                     "🗑️ **Untuk menghapus IP, gunakan format berikut:**\n"
                     "`/deleteip <ip>`\n"
                     "Contoh: `/deleteip 139.144.113.5`",
                     parse_mode='Markdown')

# Proses hapus IP
@bot.message_handler(commands=['deleteip'])
def handle_delete_ip(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 1:
            raise ValueError("Format tidak valid. Pastikan Anda menggunakan format yang benar.")

        ip_address = args[0]

        # Validasi IP
        if not is_valid_ip(ip_address):
            bot.reply_to(message, "❌ **Alamat IP tidak valid.**")
            return

        # Ambil konten saat ini dari GitHub
        current_content, sha = fetch_github_file_content(GITHUB_IP_URL)
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        # Hapus IP dari konten
        updated_content = "\n".join(line for line in current_content.splitlines() if ip_address not in line)

        # Perbarui GitHub dengan konten baru
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **IP berhasil dihapus!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")
    except Exception as e:
        bot.reply_to(message, f"❌ **Terjadi kesalahan: {str(e)}**")

# Jalankan bot
bot.polling(non_stop=True)
      
