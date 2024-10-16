from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler

# Token bot Anda
BOT_TOKEN = "7341627486:AAFd7TdIjxVdSx3lfkrhgAZpB2VMMU0WjuI"

# Ganti dengan username bot Anda yang lain
OTHER_BOT_URL = "https://t.me/scriptVPSS_bot"  # Link ke bot @scriptVPSS_bot
BUG_BOT_URL = "https://t.me/bug_PROVIDERE_bot"  # Link ke bot @bug_PROVIDERE_bot
CONVERT_BOT_URL = "https://t.me/convertBASE64_bot"  # Link ke bot @convertBASE64_bot
BOX_FOR_ROOT_BOT_URL = "https://t.me/boxforROOT_bot"  # Link ke bot @boxforROOT_bot

# Fungsi untuk menampilkan menu untuk member baru
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    welcome_text = f"👋 **Selamat datang di ANDRAX NETWORK, {user.first_name}!**\n\n" \
                   "Silakan pilih salah satu menu di bawah ini untuk melanjutkan."

    # Membuat tombol menu
    keyboard = [
        [InlineKeyboardButton("👤 PROFILE", callback_data="profile")],
        [InlineKeyboardButton("🛠️ BOT TOOLS", callback_data="bot_tools")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Mengirim pesan sambutan dengan menu
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# Fungsi untuk menangani callback dari tombol
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Menanggapi klik tombol

    if query.data == "profile":
        # Menampilkan profil pengguna
        user = query.from_user
        profile_text = f"📝 **PROFILE**\n" \
                       f"👤 Nama: {user.full_name}\n" \
                       f"💬 Username: @{user.username}\n" \
                       f"🆔 User ID: {user.id}\n" \
                       f"🌍 Lokasi: {user.language_code}"

        await query.edit_message_text(text=profile_text, parse_mode="Markdown")
    elif query.data == "bot_tools":
        # Membuat submenu untuk "BOT TOOLS"
        keyboard = [
            [InlineKeyboardButton("💻 SCRIPT VPS", url=OTHER_BOT_URL)],  # Mengarahkan ke bot lain
            [InlineKeyboardButton("🐞 BUG", url=BUG_BOT_URL)],  # Mengarahkan ke bot BUG
            [InlineKeyboardButton("🔄 CONVERT", url=CONVERT_BOT_URL)],  # Mengarahkan ke bot CONVERT
            [InlineKeyboardButton("📦 BOX FOR ROOT", url=BOX_FOR_ROOT_BOT_URL)],  # Mengarahkan ke bot BOX FOR ROOT
            [InlineKeyboardButton("🔙 Kembali", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="🔧 Anda memilih menu **BOT TOOLS**.\nPilih opsi berikut:", reply_markup=reply_markup, parse_mode="Markdown")
    elif query.data == "back":
        # Kembali ke menu utama
        keyboard = [
            [InlineKeyboardButton("👤 PROFILE", callback_data="profile")],
            [InlineKeyboardButton("🛠️ BOT TOOLS", callback_data="bot_tools")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="🔙 Kembali ke menu utama.", reply_markup=reply_markup, parse_mode="Markdown")

# Fungsi untuk menangani pesan baru dari member
async def new_member(update: Update, context: CallbackContext):
    member = update.message.new_chat_members[0]
    if member:
        await update.message.reply_text(f"👋 Selamat datang, {member.full_name}!\nKami senang menyambut Anda di ANDRAX NETWORK!",
                                       parse_mode="Markdown")

# Fungsi utama untuk menjalankan bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Menambahkan handler untuk command /start dan member baru
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    application.add_handler(CallbackQueryHandler(button))

    # Memulai bot dengan polling
    application.run_polling()

if __name__ == "__main__":
    main()
  
