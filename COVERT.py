import base64
import json
import yaml
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from io import BytesIO
import logging

# Mengaktifkan logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fungsi untuk mengonversi kode Vmess ke YAML sesuai format yang diminta
def convert_vmess_to_yaml(vmess_code: str) -> str:
    try:
        # Decode base64 dari Vmess URL
        decoded_data = base64.urlsafe_b64decode(vmess_code).decode('utf-8')
        # Parsing JSON dari hasil decode
        vmess_json = json.loads(decoded_data)

        # Ambil data dari JSON hasil decoding
        name = vmess_json.get("ps", "Unnamed")
        server = vmess_json.get("add", "server.com")
        port = int(vmess_json.get("port", 443))
        uuid = vmess_json.get("id", "")
        alterId = int(vmess_json.get("aid", 0))
        tls = vmess_json.get("tls", "none") == "tls"  # Cek apakah TLS diaktifkan
        network = vmess_json.get("net", "ws")
        path = vmess_json.get("path", "/")
        host = vmess_json.get("host", None)

        # Jika TLS aktif, gunakan host sebagai servername
        if tls:
            servername = host if host else server
        else:
            servername = None

        # Buat struktur YAML
        vmess_yaml = {
            "proxies": [
                {
                    "name": name,
                    "server": server,
                    "port": port,
                    "type": "vmess",
                    "uuid": uuid,
                    "alterId": alterId,
                    "cipher": "auto",
                    "tls": tls,
                    "skip-cert-verify": True,
                    "network": network,
                    "ws-opts": {
                        "path": path,
                        "headers": {
                            "Host": host if host else server
                        }
                    },
                    "udp": True
                }
            ]
        }

        # Tambahkan servername jika TLS aktif
        if tls and servername:
            vmess_yaml["proxies"][0]["servername"] = servername

        # Konversi hasil YAML
        yaml_data = yaml.dump(vmess_yaml, allow_unicode=True, default_flow_style=False)
        return yaml_data
    except Exception as e:
        return f"Error: {str(e)}"

# Fungsi untuk memulai bot dan menampilkan menu
async def start(update: Update, context) -> None:
    keyboard = [
        [InlineKeyboardButton("Konversi Kode Vmess", callback_data='convert')],
        [InlineKeyboardButton("Bantuan", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Selamat datang! Pilih menu di bawah:', reply_markup=reply_markup)

# Fungsi untuk menampilkan bantuan
async def help_command(update: Update, context) -> None:
    help_text = (
        "Cara menggunakan bot ini:\n"
        "1. Pilih menu 'Konversi Kode Vmess'.\n"
        "2. Kirim kode Vmess yang dimulai dengan 'vmess://'.\n"
        "3. Bot akan mengonversinya menjadi format YAML.\n"
        "4. Anda bisa mengunduh file hasil konversi atau menyalinnya langsung."
    )
    if update.callback_query:
        await update.callback_query.message.reply_text(help_text)
    else:
        await update.message.reply_text(help_text)

# Fungsi untuk menangani pilihan dari menu
async def menu_handler(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'convert':
        await query.message.reply_text('Silakan kirim kode Vmess yang ingin dikonversi.')
    elif query.data == 'help':
        await help_command(update, context)

# Fungsi untuk menangani input kode Vmess dari pengguna dan mengonversinya
async def convert(update: Update, context) -> None:
    # Ambil pesan dari pengguna
    vmess_codes = update.message.text.splitlines()  # Mendukung beberapa kode sekaligus
    yaml_results = []
    
    for vmess_code in vmess_codes:
        if vmess_code.startswith("vmess://"):
            # Hapus "vmess://" dari kode
            vmess_code = vmess_code[8:]
            yaml_results.append(convert_vmess_to_yaml(vmess_code))
        else:
            yaml_results.append("Kode tidak valid.")
    
    # Gabungkan hasil YAML
    yaml_output = "\n\n".join(yaml_results)
    
    # Buat file YAML dan kirim ke pengguna
    yaml_file = BytesIO(yaml_output.encode('utf-8'))
    yaml_file.name = 'vmess_config.yaml'
    
    await update.message.reply_document(document=yaml_file, filename='vmess_config.yaml', caption="Berikut hasil konversi YAML. Anda bisa menyalinnya dengan cepat.")
    
    # Logging aktivitas
    logger.info(f"User {update.message.from_user.username} mengirimkan kode.")

# Inisialisasi bot dengan token
def main():
    # Token bot yang diberikan
    application = Application.builder().token("7372547379:AAElSimtHMA0pr3cdPAvBRlkViZp08Qn7y0").build()

    # Tambahkan command /start
    application.add_handler(CommandHandler("start", start))
    
    # Tambahkan handler untuk callback dari menu
    application.add_handler(CallbackQueryHandler(menu_handler))
    
    # Tambahkan handler untuk command /help
    application.add_handler(CommandHandler("help", help_command))

    # Tambahkan handler untuk pesan teks (untuk input kode Vmess)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert))

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
      
