import telebot
import requests
import base64
import re
import logging
import time
from datetime import datetime, timedelta
import schedule
import threading

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Token bot Telegram dan GitHub
TELEGRAM_TOKEN = '7699241259:AAFaXQjKdeL6u7Mci8U6UvogV4m-Hdu_5wM'
GITHUB_TOKEN = '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'
GITHUB_URL = 'https://api.github.com/repos/Andraxvpn/Andrax-script/contents/izin'

# Inisialisasi bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def is_valid_ip(ip):
    """Validasi format alamat IP."""
    pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return pattern.match(ip)

def fetch_current_content():
    """Ambil konten file dari GitHub."""
    try:
        response = requests.get(GITHUB_URL, headers={'Authorization': f'token {GITHUB_TOKEN}'})
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

def update_github_content(new_content, sha):
    """Perbarui konten file di GitHub."""
    try:
        updated_content_base64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        update_response = requests.put(
            GITHUB_URL,
            json={
                'message': 'Memperbarui daftar IP',
                'content': updated_content_base64,
                'sha': sha
            },
            headers={'Authorization': f'token {GITHUB_TOKEN}'}
        )
        update_response.raise_for_status()  # Raise an error for bad responses
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return False
    except Exception as e:
        logging.error(f"Gagal memperbarui konten: {str(e)}")
        return False

def send_reminders():
    """Kirim pengingat untuk IP yang mendekati kedaluwarsa."""
    current_content, _ = fetch_current_content()
    if current_content:
        for line in current_content.splitlines():
            parts = line.split(' ### ')
            if len(parts) == 2:
                user_info, ip_info = parts
                name, expiration, ip_address = ip_info.split(' ')
                expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
                if expiration_date - datetime.now() < timedelta(days=7):
                    # Kirim notifikasi kepada pengguna
                    bot.send_message(user_info, f"🔔 **Pengingat:** IP {ip_address} akan kedaluwarsa pada {expiration}.")

def schedule_reminders():
    """Jadwalkan pengingat harian."""
    schedule.every().day.at("10:00").do(send_reminders)  # Ganti waktu sesuai kebutuhan

    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("📝 DAFTAR IP", callback_data="IPVPS"))
    keyboard.add(telebot.types.InlineKeyboardButton("📜 SCRIPT VPS", callback_data="script_vps"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔒 VPN", callback_data="vpn"))

    bot.send_message(message.chat.id,
                     "👋 **Selamat datang di Bot Manajemen IP!**\n"
                     "Silakan pilih opsi di bawah:",
                     reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "IPVPS")
def send_welcome(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🔗 Tambah IP", callback_data="add_ip_info"))
    keyboard.add(telebot.types.InlineKeyboardButton("📜 Lihat Daftar IP", callback_data="view_ip_list"))
    keyboard.add(telebot.types.InlineKeyboardButton("🗑️ Hapus IP", callback_data="delete_ip_info"))
    keyboard.add(telebot.types.InlineKeyboardButton("📥 Ekspor IP", callback_data="export_ip"))
    keyboard.add(telebot.types.InlineKeyboardButton("📤 Impor IP", callback_data="import_ip"))
    keyboard.add(telebot.types.InlineKeyboardButton("ℹ️ Bantuan", callback_data="help"))

    bot.reply_to(call.message,
                 "👋 **Selamat datang di IP Manager!**\n"
                 "Kelola alamat IP Anda dengan mudah dan cepat.\n\n"
                 "Silakan pilih opsi di bawah:",
                 reply_markup=keyboard, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "script_vps")
def script_vps(call):
    bot.send_message(call.message.chat.id, 
                     "📜 **Ini adalah menu SCRIPT VPS.**\n"
                     "Silakan kunjungi repositori kami di [GitHub](https://github.com/Andraxvpn/Andrax-script).",
                     parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "vpn")
def vpn(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🔑 VPN PREMIUM", callback_data="vpn_premium"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔓 VPN FREE", callback_data="vpn_free"))
    
    bot.send_message(call.message.chat.id, "🔒 **Ini adalah menu VPN.**", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "vpn_premium")
def vpn_premium(call):
    try:
        with open("promosi.txt", "r") as file:
            promosi_content = file.read()
        bot.send_message(call.message.chat.id, "🔑 **Anda memilih VPN PREMIUM.**\n" + promosi_content)
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, "❌ **File promosi.txt tidak ditemukan.**")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ **Terjadi kesalahan: {str(e)}**")

@bot.callback_query_handler(func=lambda call: call.data == "vpn_free")
def vpn_free(call):
    bot.send_message(call.message.chat.id, "🔓 **Anda memilih VPN FREE.**\nSilakan pilih opsi atau layanan yang tersedia.")

@bot.callback_query_handler(func=lambda call: call.data == "add_ip_info")
def add_ip_info(call):
    bot.send_message(call.message.chat.id,
                     "💻 **Untuk menambahkan IP, gunakan format berikut:**\n"
                     "`/addip <tanggal_kedaluwarsa> <ip>`\n"
                     "Contoh: `/addip 2100-10-10 139.144.113.5`",
                     parse_mode='Markdown')

@bot.message_handler(commands=['addip'])
def handle_add_ip(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 2:
            raise ValueError("Format tidak valid. Pastikan Anda menggunakan format yang benar.")
       
        expiration, ip_address = args

        # Validasi IP
        if not is_valid_ip(ip_address):
            bot.reply_to(message, "❌ **Alamat IP tidak valid.**")
            return

        # Ambil konten saat ini
        current_content, sha = fetch_current_content()
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        # Dapatkan username Telegram
        username = message.from_user.username or message.from_user.first_name

        # Format konten baru
        new_line = f"### {username} {expiration} {ip_address}\n"
        updated_content = current_content + new_line

        # Perbarui GitHub
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **IP berhasil ditambahkan!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")
    except Exception as e:
        bot.reply_to(message, f"❌ **Terjadi kesalahan: {str(e)}**")

@bot.callback_query_handler(func=lambda call: call.data == "view_ip_list")
def view_ip_list(call):
    current_content, _ = fetch_current_content()
    if current_content:
        ip_list = "📜 **Daftar IP:**\n" + current_content
        bot.send_message(call.message.chat.id, ip_list)
    else:
        bot.send_message(call.message.chat.id, "❌ **Daftar IP kosong atau gagal diambil.**")

@bot.callback_query_handler(func=lambda call: call.data == "delete_ip_info")
def delete_ip_info(call):
    bot.send_message(call.message.chat.id,
                     "🗑️ **Untuk menghapus IP, gunakan format berikut:**\n"
                     "`/deleteip <ip>`\n"
                     "Contoh: `/deleteip 139.144.113.5`",
                     parse_mode='Markdown')

@bot.message_handler(commands=['deleteip'])
def handle_delete_ip(message):
    try:
        ip_address = message.text.split()[1]

        # Validasi IP
        if not is_valid_ip(ip_address):
            bot.reply_to(message, "❌ **Alamat IP tidak valid.**")
            return

        # Ambil konten saat ini
        current_content, sha = fetch_current_content()
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        # Hapus IP dari konten
        updated_content = "\n".join(line for line in current_content.splitlines() if ip_address not in line)

        # Perbarui GitHub
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **IP berhasil dihapus!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")
    except Exception as e:
        bot.reply_to(message, f"❌ **Terjadi kesalahan: {str(e)}**")

@bot.callback_query_handler(func=lambda call: call.data == "export_ip")
def export_ip(call):
    current_content, _ = fetch_current_content()
    if current_content:
        with open("daftar_ip.txt", "w") as file:
            file.write(current_content)
        with open("daftar_ip.txt", "rb") as file:
            bot.send_document(call.message.chat.id, file)
        bot.send_message(call.message.chat.id, "📥 **Daftar IP berhasil diekspor!**")
    else:
        bot.send_message(call.message.chat.id, "❌ **Gagal mengambil daftar IP untuk diekspor.**")

@bot.callback_query_handler(func=lambda call: call.data == "import_ip")
def import_ip(call):
    bot.send_message(call.message.chat.id, "📤 **Silakan kirim file daftar IP yang ingin diimpor.**")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type == "text/plain":
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        content = downloaded_file.decode('utf-8')
        current_content, sha = fetch_current_content()
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        updated_content = current_content + content
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **Daftar IP berhasil diimpor!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_command(call):
    bot.send_message(call.message.chat.id,
                     "ℹ️ **Bantuan:**\n"
                     "- Gunakan `/addip` untuk menambahkan IP baru.\n"
                     "- Gunakan `/deleteip` untuk menghapus IP.\n"
                     "- Gunakan `/export_ip` untuk mengekspor daftar IP.\n"
                     "- Gunakan `/import_ip` untuk mengimpor daftar IP.\n"
                     "- Gunakan tombol di bawah untuk mengakses fitur lainnya.")

# Jalankan thread untuk pengingat
reminder_thread = threading.Thread(target=schedule_reminders)
reminder_thread.start()

# Mulai bot
bot.polling()import telebot
import requests
import base64
import re
import logging
import time
from datetime import datetime, timedelta
import schedule
import threading

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Token bot Telegram dan GitHub
TELEGRAM_TOKEN = '7699241259:AAFaXQjKdeL6u7Mci8U6UvogV4m-Hdu_5wM'
GITHUB_TOKEN = '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'
GITHUB_URL = 'https://api.github.com/repos/Andraxvpn/Andrax-script/contents/izin'

# Inisialisasi bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def is_valid_ip(ip):
    """Validasi format alamat IP."""
    pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return pattern.match(ip)

def fetch_current_content():
    """Ambil konten file dari GitHub."""
    try:
        response = requests.get(GITHUB_URL, headers={'Authorization': f'token {GITHUB_TOKEN}'})
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

def update_github_content(new_content, sha):
    """Perbarui konten file di GitHub."""
    try:
        updated_content_base64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        update_response = requests.put(
            GITHUB_URL,
            json={
                'message': 'Memperbarui daftar IP',
                'content': updated_content_base64,
                'sha': sha
            },
            headers={'Authorization': f'token {GITHUB_TOKEN}'}
        )
        update_response.raise_for_status()  # Raise an error for bad responses
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return False
    except Exception as e:
        logging.error(f"Gagal memperbarui konten: {str(e)}")
        return False

def send_reminders():
    """Kirim pengingat untuk IP yang mendekati kedaluwarsa."""
    current_content, _ = fetch_current_content()
    if current_content:
        for line in current_content.splitlines():
            parts = line.split(' ### ')
            if len(parts) == 2:
                user_info, ip_info = parts
                name, expiration, ip_address = ip_info.split(' ')
                expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
                if expiration_date - datetime.now() < timedelta(days=7):
                    # Kirim notifikasi kepada pengguna
                    bot.send_message(user_info, f"🔔 **Pengingat:** IP {ip_address} akan kedaluwarsa pada {expiration}.")

def schedule_reminders():
    """Jadwalkan pengingat harian."""
    schedule.every().day.at("10:00").do(send_reminders)  # Ganti waktu sesuai kebutuhan

    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("📝 DAFTAR IP", callback_data="IPVPS"))
    keyboard.add(telebot.types.InlineKeyboardButton("📜 SCRIPT VPS", callback_data="script_vps"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔒 VPN", callback_data="vpn"))

    bot.send_message(message.chat.id,
                     "👋 **Selamat datang di Bot Manajemen IP!**\n"
                     "Silakan pilih opsi di bawah:",
                     reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "IPVPS")
def send_welcome(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🔗 Tambah IP", callback_data="add_ip_info"))
    keyboard.add(telebot.types.InlineKeyboardButton("📜 Lihat Daftar IP", callback_data="view_ip_list"))
    keyboard.add(telebot.types.InlineKeyboardButton("🗑️ Hapus IP", callback_data="delete_ip_info"))
    keyboard.add(telebot.types.InlineKeyboardButton("📥 Ekspor IP", callback_data="export_ip"))
    keyboard.add(telebot.types.InlineKeyboardButton("📤 Impor IP", callback_data="import_ip"))
    keyboard.add(telebot.types.InlineKeyboardButton("ℹ️ Bantuan", callback_data="help"))

    bot.reply_to(call.message,
                 "👋 **Selamat datang di IP Manager!**\n"
                 "Kelola alamat IP Anda dengan mudah dan cepat.\n\n"
                 "Silakan pilih opsi di bawah:",
                 reply_markup=keyboard, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "script_vps")
def script_vps(call):
    bot.send_message(call.message.chat.id, 
                     "📜 **Ini adalah menu SCRIPT VPS.**\n"
                     "Silakan kunjungi repositori kami di [GitHub](https://github.com/Andraxvpn/Andrax-script).",
                     parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "vpn")
def vpn(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🔑 VPN PREMIUM", callback_data="vpn_premium"))
    keyboard.add(telebot.types.InlineKeyboardButton("🔓 VPN FREE", callback_data="vpn_free"))
    
    bot.send_message(call.message.chat.id, "🔒 **Ini adalah menu VPN.**", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "vpn_premium")
def vpn_premium(call):
    try:
        with open("promosi.txt", "r") as file:
            promosi_content = file.read()
        bot.send_message(call.message.chat.id, "🔑 **Anda memilih VPN PREMIUM.**\n" + promosi_content)
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, "❌ **File promosi.txt tidak ditemukan.**")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ **Terjadi kesalahan: {str(e)}**")

@bot.callback_query_handler(func=lambda call: call.data == "vpn_free")
def vpn_free(call):
    bot.send_message(call.message.chat.id, "🔓 **Anda memilih VPN FREE.**\nSilakan pilih opsi atau layanan yang tersedia.")

@bot.callback_query_handler(func=lambda call: call.data == "add_ip_info")
def add_ip_info(call):
    bot.send_message(call.message.chat.id,
                     "💻 **Untuk menambahkan IP, gunakan format berikut:**\n"
                     "`/addip <tanggal_kedaluwarsa> <ip>`\n"
                     "Contoh: `/addip 2100-10-10 139.144.113.5`",
                     parse_mode='Markdown')

@bot.message_handler(commands=['addip'])
def handle_add_ip(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 2:
            raise ValueError("Format tidak valid. Pastikan Anda menggunakan format yang benar.")
       
        expiration, ip_address = args

        # Validasi IP
        if not is_valid_ip(ip_address):
            bot.reply_to(message, "❌ **Alamat IP tidak valid.**")
            return

        # Ambil konten saat ini
        current_content, sha = fetch_current_content()
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        # Dapatkan username Telegram
        username = message.from_user.username or message.from_user.first_name

        # Format konten baru
        new_line = f"### {username} {expiration} {ip_address}\n"
        updated_content = current_content + new_line

        # Perbarui GitHub
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **IP berhasil ditambahkan!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")
    except Exception as e:
        bot.reply_to(message, f"❌ **Terjadi kesalahan: {str(e)}**")

@bot.callback_query_handler(func=lambda call: call.data == "view_ip_list")
def view_ip_list(call):
    current_content, _ = fetch_current_content()
    if current_content:
        ip_list = "📜 **Daftar IP:**\n" + current_content
        bot.send_message(call.message.chat.id, ip_list)
    else:
        bot.send_message(call.message.chat.id, "❌ **Daftar IP kosong atau gagal diambil.**")

@bot.callback_query_handler(func=lambda call: call.data == "delete_ip_info")
def delete_ip_info(call):
    bot.send_message(call.message.chat.id,
                     "🗑️ **Untuk menghapus IP, gunakan format berikut:**\n"
                     "`/deleteip <ip>`\n"
                     "Contoh: `/deleteip 139.144.113.5`",
                     parse_mode='Markdown')

@bot.message_handler(commands=['deleteip'])
def handle_delete_ip(message):
    try:
        ip_address = message.text.split()[1]

        # Validasi IP
        if not is_valid_ip(ip_address):
            bot.reply_to(message, "❌ **Alamat IP tidak valid.**")
            return

        # Ambil konten saat ini
        current_content, sha = fetch_current_content()
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        # Hapus IP dari konten
        updated_content = "\n".join(line for line in current_content.splitlines() if ip_address not in line)

        # Perbarui GitHub
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **IP berhasil dihapus!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")
    except Exception as e:
        bot.reply_to(message, f"❌ **Terjadi kesalahan: {str(e)}**")

@bot.callback_query_handler(func=lambda call: call.data == "export_ip")
def export_ip(call):
    current_content, _ = fetch_current_content()
    if current_content:
        with open("daftar_ip.txt", "w") as file:
            file.write(current_content)
        with open("daftar_ip.txt", "rb") as file:
            bot.send_document(call.message.chat.id, file)
        bot.send_message(call.message.chat.id, "📥 **Daftar IP berhasil diekspor!**")
    else:
        bot.send_message(call.message.chat.id, "❌ **Gagal mengambil daftar IP untuk diekspor.**")

@bot.callback_query_handler(func=lambda call: call.data == "import_ip")
def import_ip(call):
    bot.send_message(call.message.chat.id, "📤 **Silakan kirim file daftar IP yang ingin diimpor.**")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type == "text/plain":
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        content = downloaded_file.decode('utf-8')
        current_content, sha = fetch_current_content()
        if current_content is None:
            bot.reply_to(message, "❌ **Gagal mengambil konten file dari GitHub.**")
            return

        updated_content = current_content + content
        if update_github_content(updated_content, sha):
            bot.reply_to(message, "✅ **Daftar IP berhasil diimpor!**")
        else:
            bot.reply_to(message, "❌ **Gagal memperbarui konten di GitHub.**")

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_command(call):
    bot.send_message(call.message.chat.id,
                     "ℹ️ **Bantuan:**\n"
                     "- Gunakan `/addip` untuk menambahkan IP baru.\n"
                     "- Gunakan `/deleteip` untuk menghapus IP.\n"
                     "- Gunakan `/export_ip` untuk mengekspor daftar IP.\n"
                     "- Gunakan `/import_ip` untuk mengimpor daftar IP.\n"
                     "- Gunakan tombol di bawah untuk mengakses fitur lainnya.")

# Jalankan thread untuk pengingat
reminder_thread = threading.Thread(target=schedule_reminders)
reminder_thread.start()

# Mulai bot
bot.polling()
