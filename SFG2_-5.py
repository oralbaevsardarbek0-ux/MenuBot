import json
import os
import logging
import asyncio
import uuid
import time
import ast
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand,
    LinkPreviewOptions,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError, Forbidden, BadRequest


# =========================================================
# SOZLAMALAR
# =========================================================

BOT_TOKEN = "8813084323:AAEHkx8Ey0SlA5-XPTXp926smW86MWtWWhM"
ADMIN_ID = 6981334917

DATA_FILE = "data.json"

RATE_LIMIT_SECONDS = 1


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================================================
# TILLAR
# =========================================================

LANGUAGES = {
    "uz": "🇺🇿 O‘zbekcha",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский"
}


# =========================================================
# TARJIMALAR
# =========================================================

T = {

    # =========================================================
    # 🇺🇿 O'ZBEKCHA
    # =========================================================
    "uz": {

        "admins": "👤 Adminlar",
        "add_admin": "➕ Admin qo‘shish",
        "delete_admin": "🗑 Adminni o‘chirish",
        "admin_list": "👤 <b>Adminlar ro‘yxati</b>\n\n",
        "no_admins": "❌ Hozircha adminlar mavjud emas.",

        "admin_add_prompt":
            "➕ <b>Admin qo‘shish</b>\n\n"
            "<i>• Admin qilmoqchi bo‘lgan foydalanuvchining Telegram ID sini yuboring.</i>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>123456789</code>\n\n"
            "⚠️ ID ni aniqlash uchun @userinfobot dan foydalanishingiz mumkin.",

        "admin_added":
            "✅ <b>Admin muvaffaqiyatli qo‘shildi!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "admin_already": "⚠️ Bu foydalanuvchi allaqachon admin.",
        "admin_invalid_id": "❌ ID noto‘g‘ri. Faqat raqam yuboring.",
        "admin_cannot_delete_self": "❌ O‘zingizni adminlar ro‘yxatidan o‘chira olmaysiz!",
        "admin_cannot_delete_main": "❌ Asosiy adminni o‘chirish mumkin emas.",

        "admin_deleted":
            "✅ <b>Admin o‘chirildi!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "select_delete_admin": "🗑 <b>O‘chiriladigan adminni tanlang:</b>",
        "unknown_user": "Noma’lum",

        # ---------------- BROADCAST ----------------

        "broadcast_menu":
            "📢 <b>Broadcast turlari</b>\n\n"
            "<blockquote>"
            "○ <b>📝 Oddiy xabar</b> — Barcha foydalanuvchilarga oddiy xabar yuborish\n"
            "○ <b>↩️ Forward xabar</b> — Kanal yoki chatdan xabarni forward qilish\n"
            "○ <b>📎 Media xabar</b> — Rasm, video, fayl, audio yoki voice yuborish\n"
            "○ <b>👤 Bitta foydalanuvchiga</b> — ID orqali bitta foydalanuvchiga yuborish\n"
            "○ <b>✨ Shaxsiy xabar</b> — Foydalanuvchi ma’lumotlari bilan xabar yuborish\n"
            "○ <b>🔘 Inline tugmali xabar</b> — URL tugmalari bilan xabar yuborish"
            "</blockquote>\n\n"
            "<i>👇 • Kerakli turni tanlang:</i>",

        "broadcast_simple": "📝 Oddiy xabar",
        "broadcast_forward": "↩️ Forward xabar",
        "broadcast_media": "📎 Media xabar",
        "broadcast_single": "👤 Bitta foydalanuvchiga",
        "broadcast_personalized": "✨ Shaxsiy xabar",
        "broadcast_with_button": "🔘 Inline tugmali xabar",

        "broadcast_simple_prompt":
            "📝 <b>Oddiy xabar</b>\n\n"
            "<i>• Yuboriladigan xabar matnini kiriting:</i>\n\n"
            "<b>💬 Xabar barcha foydalanuvchilarga yuboriladi.</b>",

        "broadcast_forward_prompt":
            "↩️ <b>Forward xabar</b>\n\n"
            "<i>• Kanal yoki chatdan bitta xabarni forward qiling.</i>\n\n"
            "⚠️ Faqat bitta xabar yuboring.",

        "broadcast_media_prompt":
            "📎 <b>Media xabar</b>\n\n"
            "Rasm, video, fayl, audio yoki voice yuboring.\n\n"
            "✏️ Istasangiz caption ham qo‘shishingiz mumkin.",

        "broadcast_single_prompt":
            "👤 <b>Bitta foydalanuvchiga xabar</b>\n\n"
            "Format:\n"
            "<code>USER_ID | Xabar matni</code>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>123456789 | Salom!</code>",

        "broadcast_personalized_prompt":
            "✨ <b>Shaxsiy xabar</b>\n\n"
            "<b>💬 Xabar matnini kiriting</b>\n"
            "Quyidagi o‘zgaruvchilardan foydalanishingiz mumkin:\n\n"
            "<code>$firstname</code> — ism\n"
            "<code>$lastname</code> — familiya\n"
            "<code>$username</code> — username\n"
            "<code>$id</code> — Telegram ID\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>Salom $firstname! Sizning ID: $id</code>",

        "broadcast_button_prompt":
            "🔘 <b>Inline tugmali xabar</b>\n\n"
            "1️⃣ Avval xabar matnini kiriting.\n"
            "2️⃣ Keyin tugma nomi va URL manzilini kiriting.",

        "broadcast_text_step": "1️⃣ <b>Xabar matnini kiriting:</b>",
        "broadcast_button_name_step": "2️⃣ <b>Inline tugma nomini kiriting:</b>",
        "broadcast_button_url_step": "3️⃣ <b>Inline tugma URL manzilini kiriting:</b>",

        "broadcast_button_added":
            "✅ <b>Tugma qo‘shildi!</b>\n\n"
            "<i>• Yana tugma qo‘shishingiz yoki yuborishni boshlashingiz mumkin.</i>",

        "broadcast_add_more_button": "➕ Yana tugma qo‘shish",
        "broadcast_start_send": "🚀 Yuborishni boshlash",

        "broadcast_single_invalid":
            "❌ Format noto‘g‘ri.\n\n"
            "Kerakli format: <code>USER_ID | MATN</code>",

        "broadcast_single_sent":
            "✅ <b>Xabar yuborildi!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "broadcast_single_failed":
            "❌ <b>Xabar yuborilmadi!</b>\n\n"
            "<b>Sabab:</b> Foydalanuvchi botni bloklagan yoki ID noto‘g‘ri.",

        "broadcast_cancel": "❌ Bekor qilish",
        "broadcast_cancelled": "❌ <b>Broadcast bekor qilindi.</b>",

        "broadcast_progress":
            "📊 <b>Xabarlar yuborilmoqda...</b>\n\n"
            "✅ Yuborildi: <b>{sent}</b>\n"
            "❌ Xatolar: <b>{failed}</b>\n"
            "📈 Jami: <b>{total}</b>\n"
            "⏳ Qoldi: <b>{remaining}</b>",

        "broadcast_button_url_error":
            "❌ URL noto‘g‘ri.\n\n"
            "URL <code>https://</code> bilan boshlanishi kerak.",

        "broadcast_empty_text": "❌ Xabar matni bo‘sh bo‘lishi mumkin emas.",

        # ---------------- LANGUAGE ----------------

        "choose_language": "🌐 <b>Tilni tanlang</b>\n\n<i>Kerakli tilni tanlang:</i>",
        "language_changed": "✅ <b>Til muvaffaqiyatli o‘zgartirildi!</b>",

        # ---------------- STATISTICS ----------------

        "stats_title": "📊 <b>STATISTIKA</b>",
        "stats_users": "👥 Foydalanuvchilar",
        "stats_channels": "📢 Majburiy kanallar",
        "stats_buttons": "🔘 Tugmalar",
        "stats_admins": "👑 Adminlar",
        "stats_total": "📈 Jami",
        "stats_online": "🟢 Bugun qo‘shilganlar",
        "stats_week": "📅 Shu hafta",
        "stats_top_buttons": "🔥 Eng ko‘p ishlatilgan tugmalar",
        "stats_footer": "🕐 Yangilangan: {time}",
        "stats_refresh": "🔄 Yangilash",

        # ---------------- USER ----------------

        "hello":
            "👋 Salom, <b>{name}</b>!\n\n"
            "<i>• Botimizga xush kelibsiz!</i>\n\n"
            "<blockquote>☑️ Ushbu bot orqali turli xil ilova va o‘yinlarning mod versiyalarini tez va qulay yuklab olishingiz mumkin.</blockquote>\n\n"
            "<i>⚠️ Biz zararli ilovalarni joylashtirmaslikka harakat qilamiz.</i>",

        "main_menu":
            "🖥️ <b>Asosiy menyu</b>\n\n"
            "<i>👇 Kerakli bo‘limni tanlang:</i>",

        "change_language": "🌐 Tilni almashtirish",

        # ---------------- SETTINGS ----------------

        "settings_title": "⚙️ <b>BOT SOZLAMALARI</b>",
        "settings": "⚙️ Sozlamalar",
        "bot_status": "🤖 Bot holati",

        "setting_on": "🟢 ON",
        "setting_off": "🔴 OFF",

        "maintenance_enabled": "🔴 Yoqilgan",
        "maintenance_disabled": "🟢 O‘chirilgan",

        "maintenance_text_setting": "✏️ Holat matni",
        "view_logs": "📜 Loglarni ko‘rish",
        "clear_logs": "🗑 Loglarni tozalash",
        "logs_title": "📜 <b>BOT LOGLARI</b>",
        "logs_empty": "📭 Hozircha loglar mavjud emas.",

        "code_button": "🧩 Kod orqali tugma",

        "code_button_prompt":
            "🧩 <b>Kod orqali tugma qo‘shish</b>\n\n"
            "<b>☑️ Misol:</b>\n"
            "<code>{&quot;language&quot;:&quot;uz&quot;,&quot;name&quot;:&quot;📱 Test&quot;,&quot;type&quot;:&quot;text&quot;,&quot;content&quot;:&quot;&lt;b&gt;Salom!&lt;/b&gt;&quot;,&quot;style&quot;:&quot;primary&quot;}</code>\n\n"
            "<b>type:</b> text, url, photo, video, document, audio, voice\n\n"
            "🏷 HTML teglardan <b>content</b> yoki <b>caption</b> ichida foydalanish mumkin.",

        "code_button_added": "✅ <b>Tugma muvaffaqiyatli qo‘shildi!</b>",
        "code_button_error": "❌ Format noto‘g‘ri. JSON yoki Python dict yuboring.",

        "maintenance_text_prompt":
            "✏️ <b>Bot holati matni</b>\n\n"
            "🌐 Hozirgi til: <b>{language}</b>\n"
            "🏷 HTML teglardan foydalanishingiz mumkin.\n\n"
            "📝 Yangi matnni yuboring:",

        # ---------------- SUBSCRIPTION ----------------

        "required_subscription": "📢 Majburiy obuna",

        "subscription_text":
            "🔒 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling.</b>\n\n"
            "✅ Obuna bo‘lgach, <b>«Tekshirish»</b> tugmasini bosing.",

        "check_subscription": "🔄 Tekshirish",

        "subscription_ok":
            "✅ <b>Obuna tasdiqlandi!</b>\n\n"
            "<i>• Endi botdan foydalanishingiz mumkin.</i>\n\n"
            "🔄 <b>Botni yangilash 👉</b> /start",

        # ---------------- ADMIN PANEL ----------------

        "admin_panel":
            "👑 <b>ADMIN PANEL</b>\n\n"
            "<i>• Bu yerdan botni to‘liq boshqarishingiz mumkin.</i>\n\n"
            "👇 <b>Kerakli bo‘limni tanlang:</b>",

        "admin_language": "🌐 <b>Admin panel tilini tanlang:</b>",
        "admin_language_changed": "✅ <b>Admin panel tili o‘zgartirildi!</b>",

        # ---------------- CHANNELS ----------------

        "channels": "📢 Majburiy obuna",
        "public_channels": "🌐 Ommaviy kanallar",
        "private_channels": "🔐 Maxfiy kanallar",
        "channel_settings": "⚙️ Kanal sozlamalari",

        "channel_menu_title":
            "📢 <b>KANALLAR BO‘LIMI</b>\n\n"
            "<blockquote>"
            "<b>┣ 🌐 Ommaviy kanal</b> — Hammaga ko‘rinadigan kanal qo‘shish\n"
            "<b>┣ 🔐 Maxfiy kanal</b> — Zayavka bilan ishlaydigan maxfiy kanal qo‘shish\n"
            "<b>┗ ⚙️ Sozlamalar</b> — Majburiy obuna sozlamalarini boshqarish"
            "</blockquote>\n\n"
            "<i>👇 Kerakli bo‘limni tanlang:</i>",

        "public_channel_menu":
            "🌐 <b>Ommaviy kanallar</b>\n"
            "──────────────────────\n\n"
            "<blockquote>"
            "○ @username orqali boshqariladi.\n"
            "○ ⚠️ Bot kanalga administrator qilib qo‘yilishi kerak."
            "</blockquote>\n\n"
            "<i>👇 Kerakli amalni tanlang:</i>",

        "private_channel_menu":
            "🔐 <b>Maxfiy kanallar</b>\n"
            "──────────────────────\n\n"
            "<blockquote>"
            "○ Taklif havolasi orqali boshqariladi.\n"
            "○ ⚠️ Bot kanalga administrator qilib qo‘yilishi kerak."
            "</blockquote>\n\n"
            "<i>👇 Kerakli amalni tanlang:</i>",

        "add_public_channel": "➕ Ommaviy kanal qo‘shish",
        "add_private_channel": "➕ Maxfiy kanal qo‘shish",
        "channel_list": "📋 Kanallar ro‘yxati",

        "channel_settings_text":
            "⚙️ <b>KANAL SOZLAMALARI</b>\n\n"
            "<blockquote>"
            "• <b>🔐 Tasdiqdan so‘ng o‘tkazish</b> — Foydalanuvchini zayavkasi admin tomonidan tasdiqlangandan keyin botga o‘tkazish.\n\n"
            "• <b>⚡ Tasdiqni kutmasdan o‘tkazish</b> — Foydalanuvchi zayavka yuborishi bilan botdan foydalanishga ruxsat berish.\n\n"
            "• <b>🤖 Avto zayavka</b> — Zayavkalarni avtomatik qabul qilish. Bu funksiya «Tasdiqdan so‘ng o‘tkazish» bilan birga yoqilishi kerak.\n\n"
            "• <b>✏️ Obuna matni</b> — Majburiy obuna xabarini o‘zgartirish.\n\n"
            "• <b>🎨 Kanal tugma style</b> — Kanal tugmalarining ko‘rinishini o‘zgartirish.\n\n"
            "• <b>🧹 Zayavkalarni tozalash</b> — Saqlangan zayavka ma’lumotlarini tozalash."
            "</blockquote>",

        "approval_required_setting": "🔐 Tasdiqdan so‘ng o‘tkazish",
        "allow_pending_setting": "⚡ Tasdiqni kutmasdan o‘tkazish",
        "auto_accept_setting": "🤖 Avto zayavka",
        "subscription_text_setting": "✏️ Obuna matni",
        "channel_style_setting": "🎨 Kanal tugma style",

        "subscription_text_prompt":
            "✏️ <b>Majburiy obuna matnini yuboring.</b>\n\n"
            "🏷 HTML formatidan foydalanishingiz mumkin.\n\n"
            "⚠️ Faqat matn yuboring.",

        "subscription_text_saved":
            "✅ <b>Majburiy obuna matni saqlandi!</b>",

        "channel_style_prompt":
            "🎨 <b>Kanal tugma style</b>\n\n"
            "Hozirgi style: <b>{style}</b>\n\n"
            "👇 Kerakli style'ni tanlang:",

        "style_primary": "🔵 Primary",
        "style_success": "🟢 Success",
        "style_danger": "🔴 Danger",
        "style_default": "⚪ Oddiy",

        "join_requests_clear": "🧹 Zayavkalarni tozalash",
        "join_requests_cleared": "✅ <b>Saqlangan zayavkalar tozalandi!</b>",

        "public_channel_format":
            "➕ <b>Ommaviy kanal qo‘shish</b>\n\n"
            "Format:\n"
            "<code>@username | Kanal nomi</code>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>@mychannel | Mening kanal</code>\n\n"
            "⚠️ Bot kanalga administrator bo‘lishi kerak.",

        "private_channel_format":
            "🔐 <b>Maxfiy kanal qo‘shish</b>\n\n"
            "Format:\n"
            "<code>-1001234567890 | Kanal nomi | https://t.me/+INVITE</code>\n\n"
            "⚠️ Bot maxfiy kanalga administrator bo‘lishi kerak.\n"
            "🔗 Invite link aynan shu kanalga tegishli bo‘lishi kerak.",

        "private_channel_added":
            "✅ <b>Maxfiy kanal qo‘shildi!</b>\n\n"
            "🔐 {name}\n"
            "🔗 {url}",

        "private_channel_error":
            "❌ <b>Maxfiy kanalni qo‘shib bo‘lmadi.</b>\n\n"
            "Chat ID, kanal nomi va invite linkni tekshiring.",

        "channel_type_public": "🌐 Ommaviy",
        "channel_type_private": "🔐 Maxfiy",

        # ---------------- BUTTONS ----------------

        "buttons": "🔘 Tugmalar",
        "statistics": "📊 Statistika",
        "broadcast": "📢 Broadcast",

        "add_channel": "➕ Kanal qo‘shish",
        "delete_channel": "🗑 Kanalni o‘chirish",

        "add_button": "➕ Tugma qo‘shish",
        "delete_button": "🗑 Tugmani o‘chirish",
        "edit_button": "✏️ Tugmani tahrirlash",

        "back": "🔙 Orqaga",
        "admin_back": "👑 Admin panel",

        "no_channels": "❌ Hozircha majburiy kanal qo‘shilmagan.",
        "no_buttons": "❌ Bu til uchun hali tugmalar qo‘shilmagan.",

        "channel_format":
            "➕ <b>Kanal qo‘shish</b>\n\n"
            "Format:\n"
            "<code>@username | Kanal nomi</code>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>@mychannel | Mening kanal</code>\n\n"
            "⚠️ Bot kanalga administrator bo‘lishi kerak.",

        "channel_added":
            "✅ <b>Kanal muvaffaqiyatli qo‘shildi!</b>\n\n"
            "📢 {name}\n"
            "🔗 {url}",

        "channel_already": "⚠️ Bu kanal allaqachon qo‘shilgan.",

        "channel_error":
            "❌ <b>Kanalni qo‘shib bo‘lmadi.</b>\n\n"
            "Format:\n"
            "<code>@kanal | Kanal nomi</code>",

        "bot_not_admin": "❌ Bot ushbu kanalda administrator emas!",

        "select_delete_channel":
            "🗑 <b>O‘chiriladigan kanalni tanlang:</b>",

        "channel_deleted":
            "✅ <b>Kanal o‘chirildi!</b>\n\n"
            "📢 {name}",

        "select_language_buttons":
            "🔘 <b>Qaysi til tugmalarini boshqarasiz?</b>",

        "button_name":
            "➕ <b>Tugma qo‘shish</b>\n\n"
            "1️⃣ Tugma nomini yuboring.\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>🎬 Videolar</code>",

        "button_content":
            "2️⃣ <b>Tugma bosilganda yuboriladigan kontentni yuboring.</b>\n\n"
            "◉ 📝 Matn\n"
            "◉ 🖼 Rasm\n"
            "◉ 🎥 Video\n"
            "◉ 📄 Fayl\n"
            "◉ 🎵 Audio\n"
            "◉ 🎤 Voice\n\n"
            "<i>🏷 HTML teglardan foydalanish mumkin.</i>",

        "button_added":
            "✅ <b>Tugma muvaffaqiyatli qo‘shildi!</b>\n\n"
            "🌐 Til: <b>{language}</b>\n"
            "🔘 Nomi: {name}\n\n"
            "<i>⚙️ Tugmani «Tugmalar» bo‘limidan boshqarishingiz mumkin.</i>",

        "button_deleted":
            "✅ <b>Tugma o‘chirildi!</b>\n\n"
            "🔘 {name}",

        "select_delete_button":
            "🗑 <b>O‘chiriladigan tugmani tanlang:</b>",

        "name_too_long":
            "❌ Tugma nomi 50 belgidan oshmasligi kerak.",

        "admin_only": "❌ Sizda admin huquqi mavjud emas.",

        "bot_ready":
            "🖥️ <b>Foydalanuvchi paneli</b>\n\n"
            "<i>• Admin panelga qaytish 👉 /start</i>",

        "unsupported_media": "❌ Bu turdagi fayl qo‘llab-quvvatlanmaydi.",

        # ---------------- INLINE ----------------

        "inline_button": "➕ Inline tugma qo‘shish",
        "delete_inline": "🗑 Inline tugmani o‘chirish",

        "inline_added":
            "✅ <b>Inline tugma qo‘shildi!</b>\n\n"
            "🔘 {name}",

        "inline_deleted":
            "✅ <b>Inline tugma o‘chirildi!</b>\n\n"
            "🔘 {name}",

        "inline_type":
            "2️⃣ <b>Inline tugma turini tanlang:</b>",

        "inline_name_prompt":
            "➕ <b>Inline tugma qo‘shish</b>\n\n"
            "1️⃣ Tugma nomini yuboring.\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>📸 Instagram</code>",

        "inline_url_prompt":
            "🔗 <b>URL manzilni yuboring:</b>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>https://instagram.com</code>",

        "inline_text_prompt":
            "📝 <b>Tugma bosilganda chiqadigan matnni yuboring:</b>",

        "inline_url_error":
            "❌ URL noto‘g‘ri.\n\n"
            "<b>Masalan:</b>\n"
            "https://instagram.com",

        "inline_name_too_long":
            "❌ Inline tugma nomi 50 belgidan oshmasligi kerak.",

        # ---------------- ICHKI TUGMALAR ----------------

        "reply_child": "📂 Ichki tugma qo‘shish",
        "delete_reply_child": "🗑 Ichki tugmani o‘chirish",

        "reply_child_added":
            "✅ <b>Ichki tugma qo‘shildi!</b>\n\n"
            "📂 {name}",

        "reply_child_deleted":
            "✅ <b>Ichki tugma o‘chirildi!</b>\n\n"
            "📂 {name}",

        "reply_child_type":
            "2️⃣ <b>Ichki tugma turini tanlang:</b>",

        "reply_child_name_prompt":
            "📂 <b>Ichki tugma qo‘shish</b>\n\n"
            "1️⃣ Ichki tugma nomini yuboring.\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>🎮 Free Fire</code>",

        "reply_child_url_prompt":
            "🔗 <b>Ichki tugma URL manzilini yuboring:</b>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>https://instagram.com</code>",

        "reply_child_text_prompt":
            "📝 <b>Ichki tugma bosilganda chiqadigan matnni yuboring:</b>",

        "reply_child_url_error":
            "❌ URL noto‘g‘ri.\n\n"
            "<b>Masalan:</b>\n"
            "https://instagram.com",

        "reply_child_name_too_long":
            "❌ Ichki tugma nomi 50 belgidan oshmasligi kerak.",

        "select_delete_reply_child":
            "🗑 <b>O‘chiriladigan ichki tugmani tanlang:</b>",

        # ---------------- EDIT ----------------

        "edit_button_name": "✏️ <b>Tugmaning yangi nomini yuboring:</b>",

        "button_renamed":
            "✅ <b>Tugma nomi o‘zgartirildi!</b>\n\n"
            "Eski: {old}\n"
            "Yangi: {new}",

        # ---------------- STATS ----------------

        "stats_text":
            "📊 <b>STATISTIKA</b>\n\n"
            "👥 Foydalanuvchilar: <b>{users}</b>\n"
            "📢 Kanallar: <b>{channels}</b>\n"
            "🔘 Tugmalar:\n"
            "  🇺🇿 UZ: <b>{uz}</b>\n"
            "  🇬🇧 EN: <b>{en}</b>\n"
            "  🇷🇺 RU: <b>{ru}</b>\n\n"
            "🕐 {time}",

        "broadcast_prompt":
            "📢 <b>Broadcast</b>\n\n"
            "Yuboriladigan xabarni kiriting.\n\n"
            "⚠️ Xabar barcha foydalanuvchilarga yuboriladi.",

        "broadcast_started": "📢 <b>Broadcast boshlandi...</b>",

        "broadcast_done":
            "✅ <b>Broadcast yakunlandi!</b>\n\n"
            "✅ Yuborildi: <b>{sent}</b>\n"
            "❌ Xato: <b>{failed}</b>",

        "invalid_action": "❌ Noto‘g‘ri amal.",
        "error_occurred": "❌ Xatolik yuz berdi. Qaytadan urinib ko‘ring.",

        "manage_button": "⚙️ Boshqarish",
        "preview_button": "👁 Ko‘rish",
        "rename_button": "✏️ Nomini o‘zgartirish",

        "confirm_delete":
            "⚠️ <b>Haqiqatan ham o‘chirmoqchimisiz?</b>",

        "yes_delete": "✅ Ha, o‘chirish",
        "no_cancel": "❌ Bekor qilish",
        "cancelled": "❌ Amal bekor qilindi.",

        "send_content_update":
            "📝 <b>Yangi kontentni yuboring:</b>\n\n"
            "(Matn, rasm, video, fayl, audio yoki voice)",

        "content_updated": "✅ <b>Kontent muvaffaqiyatli yangilandi!</b>",

        "reply_child_media_prompt": "📎 <b>Faylni yuboring:</b>",

        "reply_child_inline_name_prompt":
            "🔘 <b>Inline tugma nomini yuboring:</b>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>📸 Instagram</code>",

        "reply_child_inline_url_prompt":
            "🔗 <b>Inline tugma URL manzilini yuboring:</b>\n\n"
            "<b>☑️ Masalan:</b>\n"
            "<code>https://instagram.com</code>",

        "choose_type": "2️⃣ <b>Tugma turini tanlang:</b>",

        "type_text": "📝 Matn",
        "type_url": "🔗 URL",
        "type_photo": "🖼 Rasm",
        "type_video": "🎥 Video",
        "type_document": "📄 Fayl",
        "type_audio": "🎵 Audio",
        "type_voice": "🎤 Voice",
        "type_inline": "🔘 Inline tugma qo‘shish",

        "select_section": "📂 <b>Kerakli bo‘limni tanlang:</b>",
    },


    # =========================================================
    # 🇬🇧 ENGLISH
    # =========================================================
    "en": {

        "admins": "👤 Admins",
        "add_admin": "➕ Add admin",
        "delete_admin": "🗑 Delete admin",
        "admin_list": "👤 <b>Admin list</b>\n\n",
        "no_admins": "❌ No admins found.",

        "admin_add_prompt":
            "➕ <b>Add admin</b>\n\n"
            "<i>• Send the Telegram ID of the user you want to make an admin.</i>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>123456789</code>\n\n"
            "⚠️ You can use @userinfobot to find a Telegram ID.",

        "admin_added":
            "✅ <b>Admin added successfully!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "admin_already": "⚠️ This user is already an admin.",
        "admin_invalid_id": "❌ Invalid ID. Please send numbers only.",
        "admin_cannot_delete_self": "❌ You cannot remove yourself from the admin list.",
        "admin_cannot_delete_main": "❌ The main admin cannot be removed.",

        "admin_deleted":
            "✅ <b>Admin removed!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "select_delete_admin": "🗑 <b>Select the admin to remove:</b>",
        "unknown_user": "Unknown",

        # ---------------- BROADCAST ----------------

        "broadcast_menu":
            "📢 <b>Broadcast types</b>\n\n"
            "<blockquote>"
            "○ <b>📝 Simple message</b> — Send a regular message to all users\n"
            "○ <b>↩️ Forward message</b> — Forward a message from a channel or chat\n"
            "○ <b>📎 Media message</b> — Send a photo, video, file, audio or voice\n"
            "○ <b>👤 Single user</b> — Send a message to one user by ID\n"
            "○ <b>✨ Personalized message</b> — Send a message using user data\n"
            "○ <b>🔘 Inline button</b> — Send a message with URL buttons"
            "</blockquote>\n\n"
            "<i>👇 • Choose a type:</i>",

        "broadcast_simple": "📝 Simple message",
        "broadcast_forward": "↩️ Forward message",
        "broadcast_media": "📎 Media message",
        "broadcast_single": "👤 Single user",
        "broadcast_personalized": "✨ Personalized message",
        "broadcast_with_button": "🔘 Message with inline button",

        "broadcast_simple_prompt":
            "📝 <b>Simple message</b>\n\n"
            "<i>• Enter the message you want to send:</i>\n\n"
            "<b>💬 The message will be sent to all users.</b>",

        "broadcast_forward_prompt":
            "↩️ <b>Forward message</b>\n\n"
            "<i>• Forward one message from a channel or chat.</i>\n\n"
            "⚠️ Send only one message.",

        "broadcast_media_prompt":
            "📎 <b>Media message</b>\n\n"
            "Send a photo, video, file, audio or voice.\n\n"
            "✏️ You can also add a caption.",

        "broadcast_single_prompt":
            "👤 <b>Message to one user</b>\n\n"
            "Format:\n"
            "<code>USER_ID | Message text</code>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>123456789 | Hello!</code>",

        "broadcast_personalized_prompt":
            "✨ <b>Personalized message</b>\n\n"
            "<b>💬 Enter your message</b>\n"
            "You can use these variables:\n\n"
            "<code>$firstname</code> — first name\n"
            "<code>$lastname</code> — last name\n"
            "<code>$username</code> — username\n"
            "<code>$id</code> — Telegram ID\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>Hello $firstname! Your ID: $id</code>",

        "broadcast_button_prompt":
            "🔘 <b>Message with inline button</b>\n\n"
            "1️⃣ First enter the message text.\n"
            "2️⃣ Then enter the button name and URL.",

        "broadcast_text_step": "1️⃣ <b>Enter the message text:</b>",
        "broadcast_button_name_step": "2️⃣ <b>Enter the inline button name:</b>",
        "broadcast_button_url_step": "3️⃣ <b>Enter the inline button URL:</b>",

        "broadcast_button_added":
            "✅ <b>Button added!</b>\n\n"
            "<i>• Add another button or start sending.</i>",

        "broadcast_add_more_button": "➕ Add another button",
        "broadcast_start_send": "🚀 Start sending",

        "broadcast_single_invalid":
            "❌ Invalid format.\n\n"
            "Required format: <code>USER_ID | TEXT</code>",

        "broadcast_single_sent":
            "✅ <b>Message sent!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "broadcast_single_failed":
            "❌ <b>Message could not be sent!</b>\n\n"
            "<b>Reason:</b> The user blocked the bot or the ID is invalid.",

        "broadcast_cancel": "❌ Cancel",
        "broadcast_cancelled": "❌ <b>Broadcast cancelled.</b>",

        "broadcast_progress":
            "📊 <b>Sending messages...</b>\n\n"
            "✅ Sent: <b>{sent}</b>\n"
            "❌ Errors: <b>{failed}</b>\n"
            "📈 Total: <b>{total}</b>\n"
            "⏳ Remaining: <b>{remaining}</b>",

        "broadcast_button_url_error":
            "❌ Invalid URL.\n\n"
            "The URL must start with <code>https://</code>.",

        "broadcast_empty_text": "❌ Message text cannot be empty.",

        # ---------------- LANGUAGE ----------------

        "choose_language":
            "🌐 <b>Choose your language</b>\n\n"
            "<i>Select your preferred language:</i>",

        "language_changed": "✅ <b>Language changed successfully!</b>",

        # ---------------- STATISTICS ----------------

        "stats_title": "📊 <b>STATISTICS</b>",
        "stats_users": "👥 Users",
        "stats_channels": "📢 Required channels",
        "stats_buttons": "🔘 Buttons",
        "stats_admins": "👑 Admins",
        "stats_total": "📈 Total",
        "stats_online": "🟢 Joined today",
        "stats_week": "📅 This week",
        "stats_top_buttons": "🔥 Most used buttons",
        "stats_footer": "🕐 Updated: {time}",
        "stats_refresh": "🔄 Refresh",

        # ---------------- USER ----------------

        "hello":
            "👋 Hello, <b>{name}</b>!\n\n"
            "<i>• Welcome to our bot!</i>\n\n"
            "<blockquote>☑️ With this bot, you can quickly and easily download various modded versions of apps and games.</blockquote>\n\n"
            "<i>⚠️ We try not to add harmful applications.</i>",

        "main_menu":
            "🖥️ <b>Main menu</b>\n\n"
            "<i>👇 Choose the section you need:</i>",

        "change_language": "🌐 Change language",

        # ---------------- SETTINGS ----------------

        "settings_title": "⚙️ <b>BOT SETTINGS</b>",
        "settings": "⚙️ Settings",
        "bot_status": "🤖 Bot status",

        "setting_on": "🟢 ON",
        "setting_off": "🔴 OFF",

        "maintenance_enabled": "🔴 Enabled",
        "maintenance_disabled": "🟢 Disabled",

        "maintenance_text_setting": "✏️ Status message",
        "view_logs": "📜 View logs",
        "clear_logs": "🗑 Clear logs",
        "logs_title": "📜 <b>BOT LOGS</b>",
        "logs_empty": "📭 No logs available yet.",

        "code_button": "🧩 Add button by code",

        "code_button_prompt":
            "🧩 <b>Add button by code</b>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>{&quot;language&quot;:&quot;en&quot;,&quot;name&quot;:&quot;📱 Test&quot;,&quot;type&quot;:&quot;text&quot;,&quot;content&quot;:&quot;&lt;b&gt;Hello!&lt;/b&gt;&quot;,&quot;style&quot;:&quot;primary&quot;}</code>\n\n"
            "<b>type:</b> text, url, photo, video, document, audio, voice\n\n"
            "🏷 HTML tags can be used inside <b>content</b> or <b>caption</b>.",

        "code_button_added": "✅ <b>Button added successfully!</b>",
        "code_button_error": "❌ Invalid format. Send JSON or a Python dict.",

        "maintenance_text_prompt":
            "✏️ <b>Bot status message</b>\n\n"
            "🌐 Current language: <b>{language}</b>\n"
            "🏷 HTML tags are supported.\n\n"
            "📝 Send the new message:",

        # ---------------- SUBSCRIPTION ----------------

        "required_subscription": "📢 Required subscription",

        "subscription_text":
            "🔒 <b>Subscribe to the following channels to use the bot.</b>\n\n"
            "✅ After subscribing, press <b>«Check»</b>.",

        "check_subscription": "🔄 Check",

        "subscription_ok":
            "✅ <b>Subscription confirmed!</b>\n\n"
            "<i>• You can now use the bot.</i>\n\n"
            "🔄 <b>Refresh the bot 👉</b> /start",

        # ---------------- ADMIN PANEL ----------------

        "admin_panel":
            "👑 <b>ADMIN PANEL</b>\n\n"
            "<i>• Manage the bot completely from this panel.</i>\n\n"
            "👇 <b>Choose the section you need:</b>",

        "admin_language": "🌐 <b>Choose the admin panel language:</b>",
        "admin_language_changed": "✅ <b>Admin panel language changed!</b>",

        # ---------------- CHANNELS ----------------

        "channels": "📢 Required subscription",
        "public_channels": "🌐 Public channels",
        "private_channels": "🔐 Private channels",
        "channel_settings": "⚙️ Channel settings",

        "channel_menu_title":
            "📢 <b>CHANNELS</b>\n\n"
            "<blockquote>"
            "<b>┣ 🌐 Public channel</b> — Add a channel visible to everyone\n"
            "<b>┣ 🔐 Private channel</b> — Add a private channel with join requests\n"
            "<b>┗ ⚙️ Settings</b> — Manage required subscription settings"
            "</blockquote>\n\n"
            "<i>👇 Choose the section you need:</i>",

        "public_channel_menu":
            "🌐 <b>Public channels</b>\n"
            "──────────────────────\n\n"
            "<blockquote>"
            "○ Managed using @username.\n"
            "○ ⚠️ The bot must be an administrator in the channel."
            "</blockquote>\n\n"
            "<i>👇 Choose an action:</i>",

        "private_channel_menu":
            "🔐 <b>Private channels</b>\n"
            "──────────────────────\n\n"
            "<blockquote>"
            "○ Managed using an invite link.\n"
            "○ ⚠️ The bot must be an administrator in the channel."
            "</blockquote>\n\n"
            "<i>👇 Choose an action:</i>",

        "add_public_channel": "➕ Add public channel",
        "add_private_channel": "➕ Add private channel",
        "channel_list": "📋 Channel list",

        "channel_settings_text":
            "⚙️ <b>CHANNEL SETTINGS</b>\n\n"
            "<blockquote>"
            "• <b>🔐 Allow after approval</b> — Allow the user to access the bot only after their join request is approved by an admin.\n\n"
            "• <b>⚡ Allow without waiting</b> — Allow the user to access the bot immediately after sending a join request.\n\n"
            "• <b>🤖 Auto-accept requests</b> — Automatically approve join requests. This must be enabled together with «Allow after approval».\n\n"
            "• <b>✏️ Subscription text</b> — Change the required subscription message.\n\n"
            "• <b>🎨 Channel button style</b> — Change the appearance of channel buttons.\n\n"
            "• <b>🧹 Clear join requests</b> — Clear saved join-request data."
            "</blockquote>",

        "approval_required_setting": "🔐 Allow after approval",
        "allow_pending_setting": "⚡ Allow without waiting",
        "auto_accept_setting": "🤖 Auto-accept requests",
        "subscription_text_setting": "✏️ Subscription text",
        "channel_style_setting": "🎨 Channel button style",

        "subscription_text_prompt":
            "✏️ <b>Send the required subscription message.</b>\n\n"
            "🏷 HTML formatting is supported.\n\n"
            "⚠️ Send text only.",

        "subscription_text_saved":
            "✅ <b>Required subscription message saved!</b>",

        "channel_style_prompt":
            "🎨 <b>Channel button style</b>\n\n"
            "Current style: <b>{style}</b>\n\n"
            "👇 Choose a style:",

        "style_primary": "🔵 Primary",
        "style_success": "🟢 Success",
        "style_danger": "🔴 Danger",
        "style_default": "⚪ Default",

        "join_requests_clear": "🧹 Clear join requests",
        "join_requests_cleared": "✅ <b>Saved join requests cleared!</b>",

        "public_channel_format":
            "➕ <b>Add public channel</b>\n\n"
            "Format:\n"
            "<code>@username | Channel name</code>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>@mychannel | My channel</code>\n\n"
            "⚠️ The bot must be an administrator in the channel.",

        "private_channel_format":
            "🔐 <b>Add private channel</b>\n\n"
            "Format:\n"
            "<code>-1001234567890 | Channel name | https://t.me/+INVITE</code>\n\n"
            "⚠️ The bot must be an administrator in the private channel.\n"
            "🔗 The invite link must belong to this exact channel.",

        "private_channel_added":
            "✅ <b>Private channel added!</b>\n\n"
            "🔐 {name}\n"
            "🔗 {url}",

        "private_channel_error":
            "❌ <b>Could not add the private channel.</b>\n\n"
            "Check the chat ID, channel name and invite link.",

        "channel_type_public": "🌐 Public",
        "channel_type_private": "🔐 Private",

        # ---------------- BUTTONS ----------------

        "buttons": "🔘 Buttons",
        "statistics": "📊 Statistics",
        "broadcast": "📢 Broadcast",

        "add_channel": "➕ Add channel",
        "delete_channel": "🗑 Delete channel",

        "add_button": "➕ Add button",
        "delete_button": "🗑 Delete button",
        "edit_button": "✏️ Edit button",

        "back": "🔙 Back",
        "admin_back": "👑 Admin panel",

        "no_channels": "❌ No required channels have been added yet.",
        "no_buttons": "❌ No buttons have been added for this language yet.",

        "channel_format":
            "➕ <b>Add channel</b>\n\n"
            "Format:\n"
            "<code>@username | Channel name</code>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>@mychannel | My channel</code>\n\n"
            "⚠️ The bot must be an administrator in the channel.",

        "channel_added":
            "✅ <b>Channel added successfully!</b>\n\n"
            "📢 {name}\n"
            "🔗 {url}",

        "channel_already": "⚠️ This channel has already been added.",

        "channel_error":
            "❌ <b>Could not add the channel.</b>\n\n"
            "Format:\n"
            "<code>@channel | Channel name</code>",

        "bot_not_admin": "❌ The bot is not an administrator in this channel!",

        "select_delete_channel":
            "🗑 <b>Select the channel to delete:</b>",

        "channel_deleted":
            "✅ <b>Channel deleted!</b>\n\n"
            "📢 {name}",

        "select_language_buttons":
            "🔘 <b>Which language's buttons do you want to manage?</b>",

        "button_name":
            "➕ <b>Add button</b>\n\n"
            "1️⃣ Send the button name.\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>🎬 Videos</code>",

        "button_content":
            "2️⃣ <b>Send the content that should be displayed when the button is pressed.</b>\n\n"
            "◉ 📝 Text\n"
            "◉ 🖼 Photo\n"
            "◉ 🎥 Video\n"
            "◉ 📄 File\n"
            "◉ 🎵 Audio\n"
            "◉ 🎤 Voice\n\n"
            "<i>🏷 HTML tags are supported.</i>",

        "button_added":
            "✅ <b>Button added successfully!</b>\n\n"
            "🌐 Language: <b>{language}</b>\n"
            "🔘 Name: {name}\n\n"
            "<i>⚙️ You can manage this button from the «Buttons» section.</i>",

        "button_deleted":
            "✅ <b>Button deleted!</b>\n\n"
            "🔘 {name}",

        "select_delete_button":
            "🗑 <b>Select the button to delete:</b>",

        "name_too_long":
            "❌ Button name must not exceed 50 characters.",

        "admin_only": "❌ You do not have admin permissions.",

        "bot_ready":
            "🖥️ <b>User panel</b>\n\n"
            "<i>• Return to the admin panel 👉 /start</i>",

        "unsupported_media": "❌ This type of file is not supported.",

        # ---------------- INLINE ----------------

        "inline_button": "➕ Add inline button",
        "delete_inline": "🗑 Delete inline button",

        "inline_added":
            "✅ <b>Inline button added!</b>\n\n"
            "🔘 {name}",

        "inline_deleted":
            "✅ <b>Inline button deleted!</b>\n\n"
            "🔘 {name}",

        "inline_type":
            "2️⃣ <b>Choose the inline button type:</b>",

        "inline_name_prompt":
            "➕ <b>Add inline button</b>\n\n"
            "1️⃣ Send the button name.\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>📸 Instagram</code>",

        "inline_url_prompt":
            "🔗 <b>Send the URL:</b>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>https://instagram.com</code>",

        "inline_text_prompt":
            "📝 <b>Send the text that should appear when the button is pressed:</b>",

        "inline_url_error":
            "❌ Invalid URL.\n\n"
            "<b>Example:</b>\n"
            "https://instagram.com",

        "inline_name_too_long":
            "❌ Inline button name must not exceed 50 characters.",

        # ---------------- INNER BUTTONS ----------------

        "reply_child": "📂 Add inner button",
        "delete_reply_child": "🗑 Delete inner button",

        "reply_child_added":
            "✅ <b>Inner button added!</b>\n\n"
            "📂 {name}",

        "reply_child_deleted":
            "✅ <b>Inner button deleted!</b>\n\n"
            "📂 {name}",

        "reply_child_type":
            "2️⃣ <b>Choose the inner button type:</b>",

        "reply_child_name_prompt":
            "📂 <b>Add inner button</b>\n\n"
            "1️⃣ Send the inner button name.\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>🎮 Free Fire</code>",

        "reply_child_url_prompt":
            "🔗 <b>Send the inner button URL:</b>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>https://instagram.com</code>",

        "reply_child_text_prompt":
            "📝 <b>Send the text that should appear when the inner button is pressed:</b>",

        "reply_child_url_error":
            "❌ Invalid URL.\n\n"
            "<b>Example:</b>\n"
            "https://instagram.com",

        "reply_child_name_too_long":
            "❌ Inner button name must not exceed 50 characters.",

        "select_delete_reply_child":
            "🗑 <b>Select the inner button to delete:</b>",

        # ---------------- EDIT ----------------

        "edit_button_name": "✏️ <b>Send the new button name:</b>",

        "button_renamed":
            "✅ <b>Button name changed!</b>\n\n"
            "Old: {old}\n"
            "New: {new}",

        "stats_text":
            "📊 <b>STATISTICS</b>\n\n"
            "👥 Users: <b>{users}</b>\n"
            "📢 Channels: <b>{channels}</b>\n"
            "🔘 Buttons:\n"
            "  🇺🇿 UZ: <b>{uz}</b>\n"
            "  🇬🇧 EN: <b>{en}</b>\n"
            "  🇷🇺 RU: <b>{ru}</b>\n\n"
            "🕐 {time}",

        "broadcast_prompt":
            "📢 <b>Broadcast</b>\n\n"
            "Enter the message you want to send.\n\n"
            "⚠️ The message will be sent to all users.",

        "broadcast_started": "📢 <b>Broadcast started...</b>",

        "broadcast_done":
            "✅ <b>Broadcast completed!</b>\n\n"
            "✅ Sent: <b>{sent}</b>\n"
            "❌ Failed: <b>{failed}</b>",

        "invalid_action": "❌ Invalid action.",
        "error_occurred": "❌ An error occurred. Please try again.",

        "manage_button": "⚙️ Manage",
        "preview_button": "👁 Preview",
        "rename_button": "✏️ Rename",

        "confirm_delete":
            "⚠️ <b>Are you sure you want to delete this?</b>",

        "yes_delete": "✅ Yes, delete",
        "no_cancel": "❌ Cancel",
        "cancelled": "❌ Action cancelled.",

        "send_content_update":
            "📝 <b>Send the new content:</b>\n\n"
            "(Text, photo, video, file, audio or voice)",

        "content_updated":
            "✅ <b>Content updated successfully!</b>",

        "reply_child_media_prompt": "📎 <b>Send the file:</b>",

        "reply_child_inline_name_prompt":
            "🔘 <b>Send the inline button name:</b>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>📸 Instagram</code>",

        "reply_child_inline_url_prompt":
            "🔗 <b>Send the inline button URL:</b>\n\n"
            "<b>☑️ Example:</b>\n"
            "<code>https://instagram.com</code>",

        "choose_type": "2️⃣ <b>Choose the button type:</b>",

        "type_text": "📝 Text",
        "type_url": "🔗 URL",
        "type_photo": "🖼 Photo",
        "type_video": "🎥 Video",
        "type_document": "📄 File",
        "type_audio": "🎵 Audio",
        "type_voice": "🎤 Voice",
        "type_inline": "🔘 Add inline button",

        "select_section": "📂 <b>Select the section you need:</b>",
    },


    # =========================================================
    # 🇷🇺 РУССКИЙ
    # =========================================================
    "ru": {

        "admins": "👤 Администраторы",
        "add_admin": "➕ Добавить администратора",
        "delete_admin": "🗑 Удалить администратора",
        "admin_list": "👤 <b>Список администраторов</b>\n\n",
        "no_admins": "❌ Администраторы пока отсутствуют.",

        "admin_add_prompt":
            "➕ <b>Добавить администратора</b>\n\n"
            "<i>• Отправьте Telegram ID пользователя, которого хотите сделать администратором.</i>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>123456789</code>\n\n"
            "⚠️ Для получения ID можно использовать @userinfobot.",

        "admin_added":
            "✅ <b>Администратор успешно добавлен!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "admin_already": "⚠️ Этот пользователь уже является администратором.",
        "admin_invalid_id": "❌ Неверный ID. Отправьте только цифры.",
        "admin_cannot_delete_self": "❌ Вы не можете удалить себя из списка администраторов.",
        "admin_cannot_delete_main": "❌ Главного администратора удалить нельзя.",

        "admin_deleted":
            "✅ <b>Администратор удалён!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "select_delete_admin":
            "🗑 <b>Выберите администратора для удаления:</b>",

        "unknown_user": "Неизвестно",

        # ---------------- BROADCAST ----------------

        "broadcast_menu":
            "📢 <b>Типы рассылки</b>\n\n"
            "<blockquote>"
            "○ <b>📝 Обычное сообщение</b> — Отправить обычное сообщение всем пользователям\n"
            "○ <b>↩️ Пересланное сообщение</b> — Переслать сообщение из канала или чата\n"
            "○ <b>📎 Медиа-сообщение</b> — Отправить фото, видео, файл, аудио или voice\n"
            "○ <b>👤 Одному пользователю</b> — Отправить сообщение одному пользователю по ID\n"
            "○ <b>✨ Персональное сообщение</b> — Отправить сообщение с данными пользователя\n"
            "○ <b>🔘 Сообщение с inline-кнопкой</b> — Отправить сообщение с URL-кнопками"
            "</blockquote>\n\n"
            "<i>👇 • Выберите нужный тип:</i>",

        "broadcast_simple": "📝 Обычное сообщение",
        "broadcast_forward": "↩️ Пересланное сообщение",
        "broadcast_media": "📎 Медиа-сообщение",
        "broadcast_single": "👤 Одному пользователю",
        "broadcast_personalized": "✨ Персональное сообщение",
        "broadcast_with_button": "🔘 Сообщение с inline-кнопкой",

        "broadcast_simple_prompt":
            "📝 <b>Обычное сообщение</b>\n\n"
            "<i>• Введите текст сообщения:</i>\n\n"
            "<b>💬 Сообщение будет отправлено всем пользователям.</b>",

        "broadcast_forward_prompt":
            "↩️ <b>Пересланное сообщение</b>\n\n"
            "<i>• Перешлите одно сообщение из канала или чата.</i>\n\n"
            "⚠️ Отправьте только одно сообщение.",

        "broadcast_media_prompt":
            "📎 <b>Медиа-сообщение</b>\n\n"
            "Отправьте фото, видео, файл, аудио или voice.\n\n"
            "✏️ При желании можно добавить подпись.",

        "broadcast_single_prompt":
            "👤 <b>Сообщение одному пользователю</b>\n\n"
            "Формат:\n"
            "<code>USER_ID | Текст сообщения</code>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>123456789 | Привет!</code>",

        "broadcast_personalized_prompt":
            "✨ <b>Персональное сообщение</b>\n\n"
            "<b>💬 Введите текст сообщения</b>\n"
            "Можно использовать следующие переменные:\n\n"
            "<code>$firstname</code> — имя\n"
            "<code>$lastname</code> — фамилия\n"
            "<code>$username</code> — username\n"
            "<code>$id</code> — Telegram ID\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>Привет, $firstname! Твой ID: $id</code>",

        "broadcast_button_prompt":
            "🔘 <b>Сообщение с inline-кнопкой</b>\n\n"
            "1️⃣ Сначала введите текст сообщения.\n"
            "2️⃣ Затем укажите название кнопки и URL.",

        "broadcast_text_step":
            "1️⃣ <b>Введите текст сообщения:</b>",

        "broadcast_button_name_step":
            "2️⃣ <b>Введите название inline-кнопки:</b>",

        "broadcast_button_url_step":
            "3️⃣ <b>Введите URL inline-кнопки:</b>",

        "broadcast_button_added":
            "✅ <b>Кнопка добавлена!</b>\n\n"
            "<i>• Добавьте ещё кнопку или начните отправку.</i>",

        "broadcast_add_more_button": "➕ Добавить ещё кнопку",
        "broadcast_start_send": "🚀 Начать отправку",

        "broadcast_single_invalid":
            "❌ Неверный формат.\n\n"
            "Используйте: <code>USER_ID | ТЕКСТ</code>",

        "broadcast_single_sent":
            "✅ <b>Сообщение отправлено!</b>\n\n"
            "👤 ID: <code>{user_id}</code>",

        "broadcast_single_failed":
            "❌ <b>Не удалось отправить сообщение!</b>\n\n"
            "<b>Причина:</b> Пользователь заблокировал бота или ID указан неверно.",

        "broadcast_cancel": "❌ Отмена",
        "broadcast_cancelled": "❌ <b>Рассылка отменена.</b>",

        "broadcast_progress":
            "📊 <b>Отправка сообщений...</b>\n\n"
            "✅ Отправлено: <b>{sent}</b>\n"
            "❌ Ошибок: <b>{failed}</b>\n"
            "📈 Всего: <b>{total}</b>\n"
            "⏳ Осталось: <b>{remaining}</b>",

        "broadcast_button_url_error":
            "❌ Неверный URL.\n\n"
            "URL должен начинаться с <code>https://</code>.",

        "broadcast_empty_text":
            "❌ Текст сообщения не может быть пустым.",

        # ---------------- LANGUAGE ----------------

        "choose_language":
            "🌐 <b>Выберите язык</b>\n\n"
            "<i>Выберите предпочитаемый язык:</i>",

        "language_changed":
            "✅ <b>Язык успешно изменён!</b>",

        # ---------------- STATISTICS ----------------

        "stats_title": "📊 <b>СТАТИСТИКА</b>",
        "stats_users": "👥 Пользователи",
        "stats_channels": "📢 Обязательные каналы",
        "stats_buttons": "🔘 Кнопки",
        "stats_admins": "👑 Администраторы",
        "stats_total": "📈 Всего",
        "stats_online": "🟢 За сегодня",
        "stats_week": "📅 За эту неделю",
        "stats_top_buttons": "🔥 Самые используемые кнопки",
        "stats_footer": "🕐 Обновлено: {time}",
        "stats_refresh": "🔄 Обновить",

        # ---------------- USER ----------------

        "hello":
            "👋 Здравствуйте, <b>{name}</b>!\n\n"
            "<i>• Добро пожаловать в наш бот!</i>\n\n"
            "<blockquote>☑️ С помощью этого бота вы можете быстро и удобно скачивать различные модифицированные версии приложений и игр.</blockquote>\n\n"
            "<i>⚠️ Мы стараемся не добавлять вредоносные приложения.</i>",

        "main_menu":
            "🖥️ <b>Главное меню</b>\n\n"
            "<i>👇 Выберите нужный раздел:</i>",

        "change_language": "🌐 Сменить язык",

        # ---------------- SETTINGS ----------------

        "settings_title": "⚙️ <b>НАСТРОЙКИ БОТА</b>",
        "settings": "⚙️ Настройки",
        "bot_status": "🤖 Состояние бота",

        "setting_on": "🟢 ON",
        "setting_off": "🔴 OFF",

        "maintenance_enabled": "🔴 Включено",
        "maintenance_disabled": "🟢 Выключено",

        "maintenance_text_setting": "✏️ Текст состояния",
        "view_logs": "📜 Просмотр логов",
        "clear_logs": "🗑 Очистить логи",
        "logs_title": "📜 <b>ЛОГИ БОТА</b>",
        "logs_empty": "📭 Логов пока нет.",

        "code_button": "🧩 Добавить кнопку через код",

        "code_button_prompt":
            "🧩 <b>Добавить кнопку через код</b>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>{&quot;language&quot;:&quot;ru&quot;,&quot;name&quot;:&quot;📱 Тест&quot;,&quot;type&quot;:&quot;text&quot;,&quot;content&quot;:&quot;&lt;b&gt;Привет!&lt;/b&gt;&quot;,&quot;style&quot;:&quot;primary&quot;}</code>\n\n"
            "<b>type:</b> text, url, photo, video, document, audio, voice\n\n"
            "🏷 HTML-теги можно использовать внутри <b>content</b> или <b>caption</b>.",

        "code_button_added":
            "✅ <b>Кнопка успешно добавлена!</b>",

        "code_button_error":
            "❌ Неверный формат. Отправьте JSON или Python dict.",

        "maintenance_text_prompt":
            "✏️ <b>Текст состояния бота</b>\n\n"
            "🌐 Текущий язык: <b>{language}</b>\n"
            "🏷 Поддерживаются HTML-теги.\n\n"
            "📝 Отправьте новый текст:",

        # ---------------- SUBSCRIPTION ----------------

        "required_subscription": "📢 Обязательная подписка",

        "subscription_text":
            "🔒 <b>Чтобы пользоваться ботом, подпишитесь на следующие каналы.</b>\n\n"
            "✅ После подписки нажмите <b>«Проверить»</b>.",

        "check_subscription": "🔄 Проверить",

        "subscription_ok":
            "✅ <b>Подписка подтверждена!</b>\n\n"
            "<i>• Теперь вы можете пользоваться ботом.</i>\n\n"
            "🔄 <b>Обновить бота 👉</b> /start",

        # ---------------- ADMIN PANEL ----------------

        "admin_panel":
            "👑 <b>ПАНЕЛЬ АДМИНИСТРАТОРА</b>\n\n"
            "<i>• Здесь вы можете полностью управлять ботом.</i>\n\n"
            "👇 <b>Выберите нужный раздел:</b>",

        "admin_language":
            "🌐 <b>Выберите язык панели администратора:</b>",

        "admin_language_changed":
            "✅ <b>Язык панели администратора изменён!</b>",

        # ---------------- CHANNELS ----------------

        "channels": "📢 Обязательная подписка",
        "public_channels": "🌐 Публичные каналы",
        "private_channels": "🔐 Приватные каналы",
        "channel_settings": "⚙️ Настройки каналов",

        "channel_menu_title":
            "📢 <b>РАЗДЕЛ КАНАЛОВ</b>\n\n"
            "<blockquote>"
            "<b>┣ 🌐 Публичный канал</b> — Добавить канал, видимый всем\n"
            "<b>┣ 🔐 Приватный канал</b> — Добавить приватный канал с заявками\n"
            "<b>┗ ⚙️ Настройки</b> — Управлять обязательной подпиской"
            "</blockquote>\n\n"
            "<i>👇 Выберите нужный раздел:</i>",

        "public_channel_menu":
            "🌐 <b>Публичные каналы</b>\n"
            "──────────────────────\n\n"
            "<blockquote>"
            "○ Управление через @username.\n"
            "○ ⚠️ Бот должен быть администратором канала."
            "</blockquote>\n\n"
            "<i>👇 Выберите действие:</i>",

        "private_channel_menu":
            "🔐 <b>Приватные каналы</b>\n"
            "──────────────────────\n\n"
            "<blockquote>"
            "○ Управление через invite-ссылку.\n"
            "○ ⚠️ Бот должен быть администратором канала."
            "</blockquote>\n\n"
            "<i>👇 Выберите действие:</i>",

        "add_public_channel": "➕ Добавить публичный канал",
        "add_private_channel": "➕ Добавить приватный канал",
        "channel_list": "📋 Список каналов",

        "channel_settings_text":
            "⚙️ <b>НАСТРОЙКИ КАНАЛОВ</b>\n\n"
            "<blockquote>"
            "• <b>🔐 Пропускать после одобрения</b> — Разрешать пользователю доступ к боту только после одобрения заявки администратором.\n\n"
            "• <b>⚡ Пропускать без ожидания</b> — Разрешать доступ сразу после отправки заявки.\n\n"
            "• <b>🤖 Автопринятие заявок</b> — Автоматически принимать заявки. Функция должна быть включена вместе с «Пропускать после одобрения».\n\n"
            "• <b>✏️ Текст подписки</b> — Изменить сообщение обязательной подписки.\n\n"
            "• <b>🎨 Стиль кнопок каналов</b> — Изменить внешний вид кнопок каналов.\n\n"
            "• <b>🧹 Очистить заявки</b> — Очистить сохранённые данные заявок."
            "</blockquote>",

        "approval_required_setting": "🔐 Пропускать после одобрения",
        "allow_pending_setting": "⚡ Пропускать без ожидания",
        "auto_accept_setting": "🤖 Автопринятие заявок",
        "subscription_text_setting": "✏️ Текст подписки",
        "channel_style_setting": "🎨 Стиль кнопок каналов",

        "subscription_text_prompt":
            "✏️ <b>Отправьте текст обязательной подписки.</b>\n\n"
            "🏷 Поддерживается HTML-форматирование.\n\n"
            "⚠️ Отправьте только текст.",

        "subscription_text_saved":
            "✅ <b>Текст обязательной подписки сохранён!</b>",

        "channel_style_prompt":
            "🎨 <b>Стиль кнопок каналов</b>\n\n"
            "Текущий стиль: <b>{style}</b>\n\n"
            "👇 Выберите стиль:",

        "style_primary": "🔵 Primary",
        "style_success": "🟢 Success",
        "style_danger": "🔴 Danger",
        "style_default": "⚪ Обычный",

        "join_requests_clear": "🧹 Очистить заявки",
        "join_requests_cleared":
            "✅ <b>Сохранённые заявки очищены!</b>",

        "public_channel_format":
            "➕ <b>Добавить публичный канал</b>\n\n"
            "Формат:\n"
            "<code>@username | Название канала</code>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>@mychannel | Мой канал</code>\n\n"
            "⚠️ Бот должен быть администратором канала.",

        "private_channel_format":
            "🔐 <b>Добавить приватный канал</b>\n\n"
            "Формат:\n"
            "<code>-1001234567890 | Название канала | https://t.me/+INVITE</code>\n\n"
            "⚠️ Бот должен быть администратором приватного канала.\n"
            "🔗 Invite-ссылка должна принадлежать именно этому каналу.",

        "private_channel_added":
            "✅ <b>Приватный канал добавлен!</b>\n\n"
            "🔐 {name}\n"
            "🔗 {url}",

        "private_channel_error":
            "❌ <b>Не удалось добавить приватный канал.</b>\n\n"
            "Проверьте ID чата, название канала и invite-ссылку.",

        "channel_type_public": "🌐 Публичный",
        "channel_type_private": "🔐 Приватный",

        # ---------------- BUTTONS ----------------

        "buttons": "🔘 Кнопки",
        "statistics": "📊 Статистика",
        "broadcast": "📢 Рассылка",

        "add_channel": "➕ Добавить канал",
        "delete_channel": "🗑 Удалить канал",

        "add_button": "➕ Добавить кнопку",
        "delete_button": "🗑 Удалить кнопку",
        "edit_button": "✏️ Редактировать кнопку",

        "back": "🔙 Назад",
        "admin_back": "👑 Панель администратора",

        "no_channels":
            "❌ Обязательные каналы пока не добавлены.",

        "no_buttons":
            "❌ Для этого языка кнопки пока не добавлены.",

        "channel_format":
            "➕ <b>Добавить канал</b>\n\n"
            "Формат:\n"
            "<code>@username | Название канала</code>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>@mychannel | Мой канал</code>\n\n"
            "⚠️ Бот должен быть администратором канала.",

        "channel_added":
            "✅ <b>Канал успешно добавлен!</b>\n\n"
            "📢 {name}\n"
            "🔗 {url}",

        "channel_already":
            "⚠️ Этот канал уже добавлен.",

        "channel_error":
            "❌ <b>Не удалось добавить канал.</b>\n\n"
            "Формат:\n"
            "<code>@channel | Название канала</code>",

        "bot_not_admin":
            "❌ Бот не является администратором этого канала!",

        "select_delete_channel":
            "🗑 <b>Выберите канал для удаления:</b>",

        "channel_deleted":
            "✅ <b>Канал удалён!</b>\n\n"
            "📢 {name}",

        "select_language_buttons":
            "🔘 <b>Кнопки какого языка вы хотите настроить?</b>",

        "button_name":
            "➕ <b>Добавить кнопку</b>\n\n"
            "1️⃣ Отправьте название кнопки.\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>🎬 Видео</code>",

        "button_content":
            "2️⃣ <b>Отправьте контент, который будет отображаться при нажатии на кнопку.</b>\n\n"
            "◉ 📝 Текст\n"
            "◉ 🖼 Фото\n"
            "◉ 🎥 Видео\n"
            "◉ 📄 Файл\n"
            "◉ 🎵 Аудио\n"
            "◉ 🎤 Voice\n\n"
            "<i>🏷 HTML-теги поддерживаются.</i>",

        "button_added":
            "✅ <b>Кнопка успешно добавлена!</b>\n\n"
            "🌐 Язык: <b>{language}</b>\n"
            "🔘 Название: {name}\n\n"
            "<i>⚙️ Управлять кнопкой можно в разделе «Кнопки».</i>",

        "button_deleted":
            "✅ <b>Кнопка удалена!</b>\n\n"
            "🔘 {name}",

        "select_delete_button":
            "🗑 <b>Выберите кнопку для удаления:</b>",

        "name_too_long":
            "❌ Название кнопки не должно превышать 50 символов.",

        "admin_only":
            "❌ У вас нет прав администратора.",

        "bot_ready":
            "🖥️ <b>Панель пользователя</b>\n\n"
            "<i>• Вернуться в панель администратора 👉 /start</i>",

        "unsupported_media":
            "❌ Этот тип файла не поддерживается.",

        # ---------------- INLINE ----------------

        "inline_button": "➕ Добавить inline-кнопку",
        "delete_inline": "🗑 Удалить inline-кнопку",

        "inline_added":
            "✅ <b>Inline-кнопка добавлена!</b>\n\n"
            "🔘 {name}",

        "inline_deleted":
            "✅ <b>Inline-кнопка удалена!</b>\n\n"
            "🔘 {name}",

        "inline_type":
            "2️⃣ <b>Выберите тип inline-кнопки:</b>",

        "inline_name_prompt":
            "➕ <b>Добавить inline-кнопку</b>\n\n"
            "1️⃣ Отправьте название кнопки.\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>📸 Instagram</code>",

        "inline_url_prompt":
            "🔗 <b>Отправьте URL:</b>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>https://instagram.com</code>",

        "inline_text_prompt":
            "📝 <b>Отправьте текст, который появится при нажатии на кнопку:</b>",

        "inline_url_error":
            "❌ Неверный URL.\n\n"
            "<b>Пример:</b>\n"
            "https://instagram.com",

        "inline_name_too_long":
            "❌ Название inline-кнопки не должно превышать 50 символов.",

        # ---------------- INNER BUTTONS ----------------

        "reply_child": "📂 Добавить внутреннюю кнопку",
        "delete_reply_child": "🗑 Удалить внутреннюю кнопку",

        "reply_child_added":
            "✅ <b>Внутренняя кнопка добавлена!</b>\n\n"
            "📂 {name}",

        "reply_child_deleted":
            "✅ <b>Внутренняя кнопка удалена!</b>\n\n"
            "📂 {name}",

        "reply_child_type":
            "2️⃣ <b>Выберите тип внутренней кнопки:</b>",

        "reply_child_name_prompt":
            "📂 <b>Добавить внутреннюю кнопку</b>\n\n"
            "1️⃣ Отправьте название внутренней кнопки.\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>🎮 Free Fire</code>",

        "reply_child_url_prompt":
            "🔗 <b>Отправьте URL внутренней кнопки:</b>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>https://instagram.com</code>",

        "reply_child_text_prompt":
            "📝 <b>Отправьте текст, который появится при нажатии на внутреннюю кнопку:</b>",

        "reply_child_url_error":
            "❌ Неверный URL.\n\n"
            "<b>Пример:</b>\n"
            "https://instagram.com",

        "reply_child_name_too_long":
            "❌ Название внутренней кнопки не должно превышать 50 символов.",

        "select_delete_reply_child":
            "🗑 <b>Выберите внутреннюю кнопку для удаления:</b>",

        # ---------------- EDIT ----------------

        "edit_button_name":
            "✏️ <b>Отправьте новое название кнопки:</b>",

        "button_renamed":
            "✅ <b>Название кнопки изменено!</b>\n\n"
            "Старое: {old}\n"
            "Новое: {new}",

        "stats_text":
            "📊 <b>СТАТИСТИКА</b>\n\n"
            "👥 Пользователи: <b>{users}</b>\n"
            "📢 Каналы: <b>{channels}</b>\n"
            "🔘 Кнопки:\n"
            "  🇺🇿 UZ: <b>{uz}</b>\n"
            "  🇬🇧 EN: <b>{en}</b>\n"
            "  🇷🇺 RU: <b>{ru}</b>\n\n"
            "🕐 {time}",

        "broadcast_prompt":
            "📢 <b>Рассылка</b>\n\n"
            "Введите сообщение, которое хотите отправить.\n\n"
            "⚠️ Сообщение будет отправлено всем пользователям.",

        "broadcast_started":
            "📢 <b>Рассылка началась...</b>",

        "broadcast_done":
            "✅ <b>Рассылка завершена!</b>\n\n"
            "✅ Отправлено: <b>{sent}</b>\n"
            "❌ Ошибок: <b>{failed}</b>",

        "invalid_action": "❌ Неверное действие.",
        "error_occurred": "❌ Произошла ошибка. Попробуйте ещё раз.",

        "manage_button": "⚙️ Управление",
        "preview_button": "👁 Просмотр",
        "rename_button": "✏️ Переименовать",

        "confirm_delete":
            "⚠️ <b>Вы действительно хотите удалить это?</b>",

        "yes_delete": "✅ Да, удалить",
        "no_cancel": "❌ Отмена",
        "cancelled": "❌ Действие отменено.",

        "send_content_update":
            "📝 <b>Отправьте новый контент:</b>\n\n"
            "(Текст, фото, видео, файл, аудио или voice)",

        "content_updated":
            "✅ <b>Контент успешно обновлён!</b>",

        "reply_child_media_prompt":
            "📎 <b>Отправьте файл:</b>",

        "reply_child_inline_name_prompt":
            "🔘 <b>Отправьте название inline-кнопки:</b>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>📸 Instagram</code>",

        "reply_child_inline_url_prompt":
            "🔗 <b>Отправьте URL inline-кнопки:</b>\n\n"
            "<b>☑️ Пример:</b>\n"
            "<code>https://instagram.com</code>",

        "choose_type":
            "2️⃣ <b>Выберите тип кнопки:</b>",

        "type_text": "📝 Текст",
        "type_url": "🔗 URL",
        "type_photo": "🖼 Фото",
        "type_video": "🎥 Видео",
        "type_document": "📄 Файл",
        "type_audio": "🎵 Аудио",
        "type_voice": "🎤 Voice",
        "type_inline": "🔘 Добавить inline-кнопку",

        "select_section":
            "📂 <b>Выберите нужный раздел:</b>",
    }
}


# =========================================================
# DATABASE
# =========================================================

def default_data():

    return {
        "channels": [],

        "buttons": {
            "uz": [],
            "en": [],
            "ru": []
        },

        "users": [],

        "admins": [
            ADMIN_ID
        ],

        "reactions": {},

        "start_messages": {
            "uz": "",
            "en": "",
            "ru": ""
        },

        "join_requests": {},

        "subscription_settings": {
            "approval_required": True,
            "allow_pending": False,
            "auto_accept": False,
            "text": {
                "uz": "",
                "en": "",
                "ru": ""
            },
            "channel_style": "primary"
        },

        "layouts": {
            "uz": {"main": "default"},
            "en": {"main": "default"},
            "ru": {"main": "default"}
        },
        "bot_settings": {
            "maintenance": False,
            "maintenance_text": {
                "uz": "🛠 <b>Texnik ishlar olib borilmoqda.</b>\n\nIltimos, birozdan so‘ng qayta urinib ko‘ring.",
                "en": "🛠 <b>Maintenance is in progress.</b>\n\nPlease try again later.",
                "ru": "🛠 <b>Проводятся технические работы.</b>\n\nПожалуйста, попробуйте позже."
            },
            "logs": []
        }
    }


def save_data(data):

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        logger.error(
            f"Save data error: {e}"
        )


# =========================================================
# BUTTON NORMALIZATION
# =========================================================

def normalize_buttons(buttons):

    if not isinstance(buttons, list):
        return

    for button in buttons:

        if not isinstance(button, dict):
            continue

        if "uid" not in button:

            button["uid"] = uuid.uuid4().hex[:10]

        # Eski INLINE tugmalar
        if "children" not in button:

            button["children"] = []

        # Yangi REPLY / ICHKI tugmalar
        if "reply_children" not in button:

            button["reply_children"] = []

        normalize_buttons(
            button.get(
                "children",
                []
            )
        )

        normalize_buttons(
            button.get(
                "reply_children",
                []
            )
        )


# =========================================================
# BUTTON STYLE + LAYOUT HELPERS
# =========================================================

BUTTON_STYLES = {
    "default": None,
    "primary": "primary",
    "success": "success",
    "danger": "danger",
}


def make_reply_button(text, style=None):
    try:
        return KeyboardButton(
            text=text,
            style=BUTTON_STYLES.get(style, None)
        )
    except TypeError:
        # Eski PTB versiyasida ham raw Bot API field orqali yuborishga urinib ko'ramiz.
        if style in BUTTON_STYLES and BUTTON_STYLES.get(style):
            try:
                return KeyboardButton(
                    text=text,
                    api_kwargs={"style": BUTTON_STYLES[style]}
                )
            except TypeError:
                return KeyboardButton(text=text)
        return KeyboardButton(text=text)


def make_inline_button(text, callback_data=None, url=None, style=None):
    kwargs = {"text": text}
    if callback_data is not None:
        kwargs["callback_data"] = callback_data
    if url is not None:
        kwargs["url"] = url
    try:
        kwargs["style"] = BUTTON_STYLES.get(style, None)
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("style", None)
        if style in BUTTON_STYLES and BUTTON_STYLES.get(style):
            try:
                kwargs["api_kwargs"] = {"style": BUTTON_STYLES[style]}
                return InlineKeyboardButton(**kwargs)
            except TypeError:
                kwargs.pop("api_kwargs", None)
        return InlineKeyboardButton(**kwargs)


def build_button_rows(items, mode="default", manual_rows=None):
    """items -> (text, button_object). Auto: uzunlar alohida, qisqalar 2 tadan."""
    if not items:
        return []

    if mode == "auto":
        rows, row = [], []
        for text, obj in items:
            if len(str(text)) >= 18:
                if row:
                    rows.append(row)
                    row = []
                rows.append([obj])
            else:
                row.append(obj)
                if len(row) == 2:
                    rows.append(row)
                    row = []
        if row:
            rows.append(row)
        return rows

    if mode == "manual" and isinstance(manual_rows, list) and manual_rows:
        rows, pos = [], 0
        for width in manual_rows:
            try:
                width = max(1, int(width))
            except (TypeError, ValueError):
                continue
            part = [obj for _, obj in items[pos:pos + width]]
            if part:
                rows.append(part)
            pos += width
        if pos < len(items):
            rows.append([obj for _, obj in items[pos:]])
        return rows

    rows, row = [], []
    for _, obj in items:
        row.append(obj)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


def find_any_button_node(buttons, uid):
    """Find any main/inline/inner button recursively by uid."""
    for button in buttons or []:
        if button.get("uid") == uid:
            return button
        found = find_any_button_node(button.get("children", []), uid)
        if found:
            return found
        found = find_any_button_node(button.get("reply_children", []), uid)
        if found:
            return found
    return None


def get_node_contents(node):
    """Backward compatible: old single content -> one-item list."""
    contents = node.get("contents")
    if isinstance(contents, list) and contents:
        return contents
    if node.get("content") not in (None, ""):
        return [{
            "type": node.get("type", "text"),
            "content": node.get("content", ""),
            "caption": node.get("caption", "")
        }]
    return []


def append_node_content(node, content_type, content, caption=""):
    items = get_node_contents(node)
    items.append({
        "type": content_type,
        "content": content,
        "caption": caption or ""
    })
    node["contents"] = items
    if not node.get("content"):
        node["type"] = content_type
        node["content"] = content
        node["caption"] = caption or ""


def get_start_message(language, first_name=""):
    custom = data.get("start_messages", {}).get(language, "")
    if custom:
        try:
            return custom.format(name=first_name)
        except Exception:
            return custom
    return T[language]["hello"].format(name=first_name)


def admin_style_button(text, callback_data, style="default"):
    return make_inline_button(text, callback_data=callback_data, style=style)


def parse_manual_layout(text):
    try:
        values = [int(x.strip()) for x in text.split(",") if x.strip()]
        if not values or any(x < 1 or x > 5 for x in values):
            return None
        return values
    except ValueError:
        return None


def style_keyboard(prefix, cancel_callback=None):
    rows = [
        [InlineKeyboardButton("🔵 Primary", callback_data=f"{prefix}_primary")],
        [InlineKeyboardButton("🟢 Success", callback_data=f"{prefix}_success")],
        [InlineKeyboardButton("🔴 Danger", callback_data=f"{prefix}_danger")],
        [InlineKeyboardButton("⚪ Oddiy", callback_data=f"{prefix}_default")],
    ]
    if cancel_callback:
        rows.append([InlineKeyboardButton("❌ Bekor qilish", callback_data=cancel_callback)])
    return InlineKeyboardMarkup(rows)


# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    if not os.path.exists(DATA_FILE):

        data = default_data()

        save_data(data)

        return data

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if "users" not in data:

            data["users"] = []

        if "admins" not in data:

            data["admins"] = [
                ADMIN_ID
            ]

        # =============================================
        # REACTIONS TEKSHIRUVI (to'g'ri joyda)
        # =============================================

        if "reactions" not in data:

            data["reactions"] = {}

        if "start_messages" not in data or not isinstance(data["start_messages"], dict):
            data["start_messages"] = {}
        for _lang in LANGUAGES:
            data["start_messages"].setdefault(_lang, "")

        if "join_requests" not in data or not isinstance(data["join_requests"], dict):
            data["join_requests"] = {}

        if "subscription_settings" not in data or not isinstance(data["subscription_settings"], dict):
            data["subscription_settings"] = {}
        sub_settings = data["subscription_settings"]
        sub_settings.setdefault("approval_required", True)
        sub_settings.setdefault("allow_pending", False)
        sub_settings.setdefault("auto_accept", False)
        sub_settings.setdefault("channel_style", "primary")
        if not isinstance(sub_settings.get("text"), dict):
            sub_settings["text"] = {}
        for _lang in LANGUAGES:
            sub_settings["text"].setdefault(_lang, "")

        if "layouts" not in data or not isinstance(data["layouts"], dict):
            data["layouts"] = {}
        for _lang in LANGUAGES:
            data["layouts"].setdefault(_lang, {"main": "default"})
            data["layouts"][_lang].setdefault("main", "default")

        if not isinstance(
            data["reactions"],
            dict
        ):

            data["reactions"] = {}

        old_channels = data.get(
            "channels"
        )

        if isinstance(
            old_channels,
            dict
        ):

            new_channels = []

            for lang in LANGUAGES:

                lang_channels = old_channels.get(
                    lang,
                    []
                )

                if not isinstance(
                    lang_channels,
                    list
                ):
                    continue

                for channel in lang_channels:

                    if not isinstance(
                        channel,
                        dict
                    ):
                        continue

                    chat_id = channel.get(
                        "chat_id"
                    )

                    if chat_id is None:
                        continue

                    already_exists = any(
                        c.get("chat_id") == chat_id
                        for c in new_channels
                    )

                    if not already_exists:

                        new_channels.append(
                            channel
                        )

            data["channels"] = new_channels

        elif not isinstance(
            old_channels,
            list
        ):

            data["channels"] = []

        # Kanal formatini yagona ko‘rinishga keltirish.
        # Eski @username kanallar public, qolganlari private sifatida belgilanadi.
        for _channel in data.get("channels", []):
            if not isinstance(_channel, dict):
                continue
            if _channel.get("type") not in ("public", "private"):
                _channel["type"] = "public" if _channel.get("username") else "private"
            if _channel.get("type") == "private":
                _channel.setdefault("invite_link", _channel.get("url", ""))
            else:
                _channel.setdefault("invite_link", "")

        if not isinstance(
            data.get("buttons"),
            dict
        ):

            data["buttons"] = {
                "uz": [],
                "en": [],
                "ru": []
            }

        for lang in LANGUAGES:

            if lang not in data["buttons"]:

                data["buttons"][lang] = []

            if not isinstance(
                data["buttons"][lang],
                list
            ):

                data["buttons"][lang] = []

            normalize_buttons(
                data["buttons"][lang]
            )

        for user in data["users"]:

            if "language" not in user:

                user["language"] = None

        settings = data.setdefault("bot_settings", {})
        settings.setdefault("maintenance", False)
        settings.setdefault("maintenance_text", {"uz": "", "en": "", "ru": ""})
        for _lang in ("uz", "en", "ru"):
            settings["maintenance_text"].setdefault(_lang, "")
        settings.setdefault("logs", [])
        if not isinstance(settings["logs"], list):
            settings["logs"] = []
        settings["logs"] = settings["logs"][-300:]

        save_data(data)

        return data

    except Exception as e:

        logger.error(
            f"Database xatosi: {e}"
        )

        data = default_data()

        save_data(data)

        return data


data = load_data()


# =========================================================
# ADMIN
# =========================================================

def is_admin(user_id):

    return user_id in data.get(
        "admins",
        [ADMIN_ID]
    )


def get_admin_language():

    for user in data["users"]:

        if user["id"] == ADMIN_ID:

            return user.get(
                "admin_language",
                "uz"
            )

    return "uz"


def set_admin_language(language):

    for user in data["users"]:

        if user["id"] == ADMIN_ID:

            user["admin_language"] = language

            save_data(data)

            return

    data["users"].append({

        "id": ADMIN_ID,

        "username": "",

        "first_name": "Admin",

        "language": None,

        "admin_language": language

    })

    save_data(data)


# =========================================================
# USER
# =========================================================

def save_user(user):

    for u in data["users"]:

        if u["id"] == user.id:

            u["username"] = (
                user.username or ""
            )

            u["first_name"] = (
                user.first_name or ""
            )

            if "language" not in u:

                u["language"] = None

            save_data(data)

            return

    data["users"].append({

        "id": user.id,

        "username": user.username or "",

        "first_name": user.first_name or "",

        "language": None,

        "admin_language":
            "uz"
            if user.id == ADMIN_ID
            else None,

        "joined_at":
            datetime.now().isoformat()
    })

    save_data(data)


def get_user_language(user_id):

    for user in data["users"]:

        if user["id"] == user_id:

            return user.get(
                "language"
            )

    return None


def set_user_language(
    user_id,
    language
):

    for user in data["users"]:

        if user["id"] == user_id:

            user["language"] = language

            save_data(data)

            return


# =========================================================
# RATE LIMIT
# =========================================================

rate_limit_cache = {}


def is_rate_limited(user_id):

    now = time.time()

    last = rate_limit_cache.get(
        user_id,
        0
    )

    if (
        now - last
        < RATE_LIMIT_SECONDS
    ):

        return True

    rate_limit_cache[user_id] = now

    return False


# =========================================================
# KEYBOARDS
# =========================================================

def language_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🇺🇿 O‘zbekcha",
                callback_data="lang_uz"
            )
        ],

        [
            InlineKeyboardButton(
                "🇬🇧 English",
                callback_data="lang_en"
            )
        ],

        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="lang_ru"
            )
        ]

    ])


def admin_language_keyboard():

    language = get_admin_language()

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🇺🇿 O‘zbekcha",
                callback_data="adminlang_uz"
            )
        ],

        [
            InlineKeyboardButton(
                "🇬🇧 English",
                callback_data="adminlang_en"
            )
        ],

        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="adminlang_ru"
            )
        ],

        [
            InlineKeyboardButton(
                T[language]["admin_back"],
                callback_data="admin_back"
            )
        ]

    ])


# =========================================================
# USER REPLY KEYBOARD
# =========================================================

def user_keyboard(
    language,
    buttons=None,
    show_back=False,
    layout_mode=None,
    manual_rows=None
):

    if buttons is None:
        buttons = data["buttons"].get(language, [])
        layout_info = data.get("layouts", {}).get(language, {})
        layout_mode = layout_mode or layout_info.get("main", "default")
        manual_rows = manual_rows or layout_info.get("main_rows", [])
    else:
        layout_mode = layout_mode or "default"

    items = []
    for button in buttons:
        button_name = button.get("name", "Button")
        style = button.get("style", "default")

        if button.get("type") == "reaction":
            reaction_uid = button.get("reaction_uid", button.get("uid", ""))
            reaction_data = data.get("reactions", {}).get(reaction_uid, {})
            raw_users = reaction_data.get("users", [])
            users = []
            for uid in raw_users:
                try:
                    uid = int(uid)
                except (TypeError, ValueError):
                    continue
                if uid not in users:
                    users.append(uid)
            count = len(users)
            if reaction_data:
                reaction_data["users"] = users
                reaction_data["count"] = count
                data.setdefault("reactions", {})[reaction_uid] = reaction_data
            button_name = f"{button_name} ({count})"

        items.append((button_name, make_reply_button(button_name, style)))

    rows = build_button_rows(items, layout_mode, manual_rows)

    if show_back:
        rows.append([make_reply_button("↩️ Orqaga", "default")])
    else:
        rows.append([make_reply_button(T[language]["change_language"], "default")])

    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


# =========================================================
# INLINE FIND
# =========================================================

def find_inline_button_by_uid(
    buttons,
    uid
):

    for button in buttons:

        if button.get("uid") == uid:

            return button

        children = button.get(
            "children",
            []
        )

        found = find_inline_button_by_uid(
            children,
            uid
        )

        if found:

            return found

    return None


def find_reaction_node(buttons, reaction_uid):
    for button in buttons:
        if button.get("reaction_uid") == reaction_uid:
            return button
        for key in ("children", "reply_children"):
            found = find_reaction_node(button.get(key, []), reaction_uid)
            if found:
                return found
    return None


def find_reply_button_by_uid(
    buttons,
    uid
):

    for button in buttons:

        if button.get("uid") == uid:

            return button

        children = button.get(
            "reply_children",
            []
        )

        found = find_reply_button_by_uid(
            children,
            uid
        )

        if found:

            return found

    return None


def find_parent_reply_button(
    buttons,
    uid,
    parent=None
):

    for button in buttons:

        if button.get("uid") == uid:

            return parent

        children = button.get(
            "reply_children",
            []
        )

        found = find_parent_reply_button(
            children,
            uid,
            button
        )

        if found:

            return found

    return None
    
    
def get_stats_data():
    """Statistika uchun ma'lumotlarni yig'ish"""
    from datetime import timedelta
    
    users = data.get("users", [])
    buttons = data.get("buttons", {})
    channels = data.get("channels", [])
    admins = data.get("admins", [ADMIN_ID])
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    today_count = 0
    week_count = 0
    
    for user in users:
        joined = user.get("joined_at")
        if joined:
            try:
                joined_dt = datetime.fromisoformat(joined)
                if joined_dt >= today_start:
                    today_count += 1
                if joined_dt >= week_start:
                    week_count += 1
            except (ValueError, TypeError):
                pass
    
    return {
        "total_users": len(users),
        "today_users": today_count,
        "week_users": week_count,
        "channels": len(channels),
        "admins": len(admins),
        "buttons_uz": len(buttons.get("uz", [])),
        "buttons_en": len(buttons.get("en", [])),
        "buttons_ru": len(buttons.get("ru", [])),
        "buttons_total": (
            len(buttons.get("uz", [])) +
            len(buttons.get("en", [])) +
            len(buttons.get("ru", []))
        ),
    }


def build_stats_text(language):
    """Chiroyli statistika matnini yaratish"""
    stats = get_stats_data()
    
    total_buttons = stats["buttons_total"]
    
    text = (
        f"{T[language]['stats_title']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        f"{T[language]['stats_users']}\n"
        f"├ Jami: <b>{stats['total_users']}</b>\n"
        f"├ {T[language]['stats_online']}: <b>{stats['today_users']}</b>\n"
        f"└ {T[language]['stats_week']}: <b>{stats['week_users']}</b>\n\n"
        
        f"{T[language]['stats_channels']}: <b>{stats['channels']}</b>\n"
        f"{T[language]['stats_admins']}: <b>{stats['admins']}</b>\n\n"
        
        f"{T[language]['stats_buttons']} ({T[language]['stats_total']}: <b>{total_buttons}</b>)\n"
        f"├ 🇺🇿 UZ: <b>{stats['buttons_uz']}</b>\n"
        f"├ 🇬🇧 EN: <b>{stats['buttons_en']}</b>\n"
        f"└ 🇷🇺 RU: <b>{stats['buttons_ru']}</b>\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{T[language]['stats_footer'].format(time=datetime.now().strftime('%H:%M:%S'))}"
    )
    
    return text


def stats_keyboard(language):
    """Statistika klaviaturasi"""
    return InlineKeyboardMarkup([
        [admin_style_button(T[language]["stats_refresh"], "stats", "success")],
        [admin_style_button(T[language]["back"], "admin_back", "default")]
    ])


# =========================================================
# BOT SETTINGS / LOGS
# =========================================================

def bot_maintenance_enabled():
    return bool(data.get("bot_settings", {}).get("maintenance", False))

def add_admin_log(action, user_id=None, details=""):
    settings = data.setdefault("bot_settings", {})
    logs = settings.setdefault("logs", [])
    logs.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": str(action), "user_id": user_id, "details": str(details or "")})
    settings["logs"] = logs[-300:]
    save_data(data)

def maintenance_text(language):
    texts = data.get("bot_settings", {}).get("maintenance_text", {})
    return texts.get(language) or T[language].get("maintenance_text", "🛠 <b>Texnik ishlar olib borilmoqda.</b>")

def settings_text(language):
    enabled = bot_maintenance_enabled()
    state = T[language]["maintenance_enabled"] if enabled else T[language]["maintenance_disabled"]
    return f"{T[language]['settings_title']}\n\n🛠 <b>{T[language]['bot_status']}</b>: {state}\n✏️ {T[language]['maintenance_text_setting']}\n📜 {T[language]['view_logs']}\n🧩 {T[language]['code_button']}"

def settings_keyboard(language):
    enabled = bot_maintenance_enabled()
    return InlineKeyboardMarkup([
        [admin_style_button(T[language]["setting_on"] if enabled else T[language]["setting_off"], "settings_bot_status", "danger" if enabled else "success")],
        [admin_style_button(T[language]["maintenance_text_setting"], "settings_maintenance_text", "primary")],
        [admin_style_button(T[language]["view_logs"], "settings_logs", "default")],
        [admin_style_button(T[language]["clear_logs"], "settings_clear_logs", "danger")],
        [admin_style_button(T[language]["code_button"], "settings_code_button", "success")],
        [admin_style_button(T[language]["back"], "admin_back", "default")]
    ])

def logs_text(language):
    logs = data.get("bot_settings", {}).get("logs", [])
    if not logs: return f"{T[language]['logs_title']}\n\n{T[language]['logs_empty']}"
    out=[T[language]["logs_title"], ""]
    for x in reversed(logs[-50:]):
        line=f"🕐 <code>{x.get('time','-')}</code>\n• <b>{x.get('action','-')}</b>\n• ID: <code>{x.get('user_id','-')}</code>"
        if x.get("details"): line += f"\n• {x['details']}"
        out.append(line)
    return "\n\n".join(out)


# =========================================================
# ADMIN KEYBOARD
# =========================================================

def admin_keyboard():
    language = get_admin_language()
    return InlineKeyboardMarkup([
        [
            admin_style_button(T[language]["channels"], "channel_list", "primary"),
            admin_style_button(T[language]["buttons"], "button_list", "primary")
        ],
        [
            admin_style_button(T[language]["statistics"], "stats", "success"),
            admin_style_button(T[language]["broadcast"], "broadcast", "primary")
        ],
        [
            admin_style_button(T[language]["admins"], "admin_manage", "default"),
            admin_style_button("✏️ Start xabari", "start_message", "success")
        ],
        [
            admin_style_button(T[language]["settings"], "settings", "default"),
            admin_style_button(T[language]["change_language"], "admin_language", "default")
        ]
    ])
def broadcast_menu_keyboard():

    language = get_admin_language()

    return InlineKeyboardMarkup([

        [admin_style_button(T[language]["broadcast_simple"], "bc_simple", "primary"),
         admin_style_button(T[language]["broadcast_forward"], "bc_forward", "primary")],

        [admin_style_button(T[language]["broadcast_media"], "bc_media", "primary"),
         admin_style_button(T[language]["broadcast_single"], "bc_single", "default")],

        [admin_style_button(T[language]["broadcast_personalized"], "bc_personalized", "default"),
         admin_style_button(T[language]["broadcast_with_button"], "bc_with_button", "success")],

        [
            InlineKeyboardButton(
                T[language]["back"],
                callback_data="admin_back"
            )
        ]

    ])


def admin_manage_keyboard():

    language = get_admin_language()

    return InlineKeyboardMarkup([
        [admin_style_button(T[language]["add_admin"], "add_admin", "success")],
        [admin_style_button(T[language]["delete_admin"], "delete_admin", "danger")],
        [admin_style_button(T[language]["back"], "admin_back", "default")]
    ])


def channel_manage_keyboard(section="main"):
    language = get_admin_language()

    if section == "main":
        return InlineKeyboardMarkup([
            [
                admin_style_button(T[language]["public_channels"], "public_channels", "primary"),
                admin_style_button(T[language]["private_channels"], "private_channels", "primary")
            ],
            [admin_style_button(T[language]["channel_settings"], "channel_settings", "default")],
            [admin_style_button(T[language]["back"], "admin_back", "danger")]
        ])

    if section == "public":
        return InlineKeyboardMarkup([
            [admin_style_button(T[language]["add_public_channel"], "add_public_channel", "success")],
            [admin_style_button(T[language]["channel_list"], "public_channel_list", "primary")],
            [admin_style_button(T[language]["delete_channel"], "delete_public_channel", "danger")],
            [admin_style_button(T[language]["back"], "channel_list", "default")]
        ])

    if section == "private":
        return InlineKeyboardMarkup([
            [admin_style_button(T[language]["add_private_channel"], "add_private_channel", "success")],
            [admin_style_button(T[language]["channel_list"], "private_channel_list", "primary")],
            [admin_style_button(T[language]["delete_channel"], "delete_private_channel", "danger")],
            [admin_style_button(T[language]["back"], "channel_list", "default")]
        ])

    settings = data.setdefault("subscription_settings", {})
    approval_required = bool(settings.get("approval_required", True))
    allow_pending = bool(settings.get("allow_pending", False))
    auto_accept = bool(settings.get("auto_accept", False))

    def state(value):
        return T[language]["setting_on"] if value else T[language]["setting_off"]

    return InlineKeyboardMarkup([
        [admin_style_button(f'{T[language]["approval_required_setting"]}: {state(approval_required)}', "sub_setting_approval", "success" if approval_required else "danger")],
        [admin_style_button(f'{T[language]["allow_pending_setting"]}: {state(allow_pending)}', "sub_setting_pending", "success" if allow_pending else "danger")],
        [admin_style_button(f'{T[language]["auto_accept_setting"]}: {state(auto_accept)}', "sub_setting_auto", "success" if auto_accept else "danger")],
        [admin_style_button(T[language]["subscription_text_setting"], "sub_setting_text", "primary")],
        [admin_style_button(T[language]["channel_style_setting"], "sub_setting_style", "default")],
        [admin_style_button(T[language]["join_requests_clear"], "clear_join_requests", "danger")],
        [admin_style_button(T[language]["back"], "channel_list", "default")]
    ])


def buttons_language_keyboard():

    lang = get_admin_language()

    return InlineKeyboardMarkup([
        [
            admin_style_button("🇺🇿 O‘zbekcha", "buttons_uz", "primary"),
            admin_style_button("🇬🇧 English", "buttons_en", "primary")
        ],
        [admin_style_button("🇷🇺 Русский", "buttons_ru", "primary")],
        [admin_style_button(T[lang]["admin_back"], "admin_back", "default")]
    ])


# =========================================================
# SUBSCRIPTION CHECK
# =========================================================

async def check_subscription(
    user_id,
    bot
):
    """Telegram API orqali kanallarni tekshiradi va zayavka sozlamalarini hisobga oladi."""
    not_subscribed = []
    settings = data.get("subscription_settings", {})
    approval_required = bool(settings.get("approval_required", True))
    allow_pending = bool(settings.get("allow_pending", False))

    for channel in data.get("channels", []):
        try:
            chat_id = channel.get("chat_id")
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            status = str(member.status).lower()
            subscribed = status in {"member", "administrator", "creator", "owner"}
            if status == "restricted" and getattr(member, "is_member", False):
                subscribed = True

            pending_ids = data.get("join_requests", {}).get(str(chat_id), [])
            is_pending = user_id in pending_ids

            if not subscribed and is_pending and (allow_pending or not approval_required):
                subscribed = True

            if not subscribed:
                item = dict(channel)
                item["join_request_pending"] = is_pending
                not_subscribed.append(item)

        except Exception as e:
            logger.error(f"Subscription error for {channel.get('chat_id')}: {e}")
            item = dict(channel)
            item["join_request_pending"] = user_id in data.get("join_requests", {}).get(str(channel.get("chat_id")), [])
            not_subscribed.append(item)

    return not_subscribed


# =========================================================
# SUBSCRIPTION MESSAGE
# =========================================================

async def subscription_message(
    update,
    context,
    language
):
    user_id = update.effective_user.id
    not_subscribed = await check_subscription(user_id, context.bot)

    if not not_subscribed:
        return False

    buttons = []
    channel_style = data.get("subscription_settings", {}).get("channel_style", "primary")
    if channel_style not in BUTTON_STYLES:
        channel_style = "primary"

    for channel in not_subscribed:
        channel_url = channel.get("url", "")
        if channel.get("type") == "private":
            channel_url = channel.get("invite_link") or channel_url

        if channel_url:
            prefix = "⏳ " if channel.get("join_request_pending") else ("🔐 " if channel.get("type") == "private" else "📢 ")
            buttons.append([make_inline_button(prefix + channel.get("name", "Kanal"), url=channel_url, style=channel_style)])

    buttons.append([
        admin_style_button(T[language]["check_subscription"], "check_subscription", "success")
    ])

    custom_text = data.get("subscription_settings", {}).get("text", {}).get(language, "")
    # Maxsus matn bo‘lsa, aynan o‘sha matn yuboriladi. Avtomatik sarlavha qo‘shilmaydi.
    text = custom_text or T[language]["subscription_text"]

    preview_options = LinkPreviewOptions(is_disabled=True)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(
                text, parse_mode="HTML", link_preview_options=preview_options,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except BadRequest:
            await update.callback_query.message.reply_text(
                text, parse_mode="HTML", link_preview_options=preview_options,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    else:
        await update.message.reply_text(
            text, parse_mode="HTML", link_preview_options=preview_options,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    return True


# =========================================================
# SEND INLINE BUTTON CONTENT
# =========================================================

async def send_button_content(message, button, language):
    """Send a button's content(s) and its inline/inner keyboards."""
    inline_buttons = button.get("children", [])
    reply_children = button.get("reply_children", [])
    inline_keyboard = None

    if inline_buttons:
        flat_items = []
        for child_index, child in enumerate(inline_buttons):
            child_name = child.get("name", "Button")
            child_type = child.get("type", "text")
            if child_type == "url":
                obj = make_inline_button(child_name, url=child.get("content", ""), style=child.get("style", "default"))
            elif child_type == "reaction":
                reaction_uid = child.get("reaction_uid", child.get("uid", ""))
                reaction_data = data.get("reactions", {}).get(reaction_uid, {})
                users = []
                for uid in reaction_data.get("users", []):
                    try: uid = int(uid)
                    except (TypeError, ValueError): continue
                    if uid not in users: users.append(uid)
                reaction_data["users"] = users
                reaction_data["count"] = len(users)
                data.setdefault("reactions", {})[reaction_uid] = reaction_data
                obj = make_inline_button(f"{child_name} ({len(users)})", callback_data=f"reaction_{reaction_uid}", style=child.get("style", "default"))
            else:
                obj = make_inline_button(child_name, callback_data=f"child_{child_index}_{button.get('uid')}", style=child.get("style", "default"))
            flat_items.append((getattr(obj, "text", child_name), obj))
        if flat_items:
            mode = button.get("inline_layout", "default")
            rows = build_button_rows(flat_items, mode, button.get("inline_rows", []))
            inline_keyboard = InlineKeyboardMarkup(rows)

    contents = get_node_contents(button)
    if not contents and inline_keyboard:
        contents = [{"type": "text", "content": "👇", "caption": ""}]

    for idx, item in enumerate(contents):
        ctype = item.get("type", "text")
        content = item.get("content", "")
        caption = item.get("caption", "")
        # Keep the inline keyboard on the last message so one button does not create duplicate keyboards.
        markup = inline_keyboard if idx == len(contents) - 1 else None
        if ctype == "text":
            await message.reply_text(content or "👇", parse_mode="HTML", reply_markup=markup)
        elif ctype == "photo":
            await message.reply_photo(photo=content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype == "video":
            await message.reply_video(video=content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype == "document":
            await message.reply_document(document=content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype == "audio":
            await message.reply_audio(audio=content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype == "voice":
            await message.reply_voice(voice=content, caption=caption or None, reply_markup=markup)
        elif ctype == "url":
            await message.reply_text(f'🔗 <a href="{content}">Havolani ochish</a>', parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=markup)

    if reply_children:
        await message.reply_text(
            T[language]["select_section"], parse_mode="HTML",
            reply_markup=user_keyboard(language, reply_children, show_back=True,
                                      layout_mode=button.get("reply_layout", "default"),
                                      manual_rows=button.get("reply_rows", []))
        )


# =========================================================
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    save_user(user)

    context.user_data.clear()

    if bot_maintenance_enabled() and not is_admin(user.id):
        await update.message.reply_text(maintenance_text(get_user_language(user.id) or "uz"), parse_mode="HTML")
        return

    if is_admin(user.id):

        await update.message.reply_text(

            T[get_admin_language()]["admin_panel"],

            parse_mode="HTML",

            reply_markup=ReplyKeyboardMarkup(
                [
                    ["👑 Admin panel"],
                    ["👥 Foydalanuvchilar"]
                ],
                resize_keyboard=True
            )
        )

        return

    language = get_user_language(
        user.id
    )

    if not language:

        await update.message.reply_text(

            T["uz"]["choose_language"],

            parse_mode="HTML",

            reply_markup=language_keyboard()
        )

        return

    blocked = await subscription_message(
        update,
        context,
        language
    )

    if blocked:

        return

    await update.message.reply_text(
        get_start_message(language, user.first_name),
        parse_mode="HTML",
        reply_markup=user_keyboard(language)
    )


# =========================================================
# ADMIN PANEL
# =========================================================

async def admin_panel(
    update,
    context
):

    if not is_admin(
        update.effective_user.id
    ):

        await update.message.reply_text(
            T["uz"]["admin_only"]
        )

        return

    context.user_data.clear()

    language = get_admin_language()

    await update.message.reply_text(

        T[language]["admin_panel"],

        parse_mode="HTML",

        reply_markup=admin_keyboard()
    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def callback_handler(
    update,
    context
):

    query = update.callback_query

    user_id = query.from_user.id

    # Maintenance holatida oddiy foydalanuvchini shu yerda to‘xtatamiz.
    if bot_maintenance_enabled() and not is_admin(user_id):
        await query.answer(maintenance_text(get_user_language(user_id) or "uz"), show_alert=True)
        return

    # Reaction callbacki keyin show_alert bilan javob beradi.
    if not query.data.startswith("reaction_"):
        await query.answer()

    admin_lang = get_admin_language()

    try:

        # =================================================
        # BOT SETTINGS
        # =================================================
        if query.data == "settings":
            await query.message.edit_text(settings_text(admin_lang), parse_mode="HTML", reply_markup=settings_keyboard(admin_lang))
            return
        if query.data == "settings_bot_status":
            state = not bot_maintenance_enabled()
            data.setdefault("bot_settings", {})["maintenance"] = state
            save_data(data); add_admin_log("BOT_STATUS", user_id, "maintenance=" + str(state))
            await query.message.edit_text(settings_text(admin_lang), parse_mode="HTML", reply_markup=settings_keyboard(admin_lang))
            return
        if query.data == "settings_maintenance_text":
            context.user_data["editing_maintenance_text"] = get_admin_language()
            await query.message.edit_text(T[admin_lang]["maintenance_text_prompt"].format(language=LANGUAGES[get_admin_language()]), parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["back"], "settings", "default")]]))
            return
        if query.data == "settings_logs":
            await query.message.edit_text(logs_text(admin_lang), parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["back"], "settings", "default")]]))
            return
        if query.data == "settings_clear_logs":
            data.setdefault("bot_settings", {})["logs"] = []
            save_data(data)
            await query.message.edit_text(logs_text(admin_lang), parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["back"], "settings", "default")]]))
            return
        if query.data == "settings_code_button":
            context.user_data["adding_button_by_code"] = True
            await query.message.edit_text(T[admin_lang]["code_button_prompt"], parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["back"], "settings", "default")]]))
            return

        # =================================================
        # USER LANGUAGE
        # =================================================

        if query.data.startswith("lang_"):

            language = query.data.replace(
                "lang_",
                ""
            )

            if language not in LANGUAGES:

                return

            set_user_language(
                user_id,
                language
            )

            try:

                await query.message.delete()

            except BadRequest:

                pass

            blocked = await subscription_message(
                update,
                context,
                language
            )

            if blocked:

                return

            await query.message.reply_text(

                T[language]["language_changed"],

                reply_markup=user_keyboard(
                    language
                )
            )

            return

        # =================================================
        # REACTION TYPE SELECTION
        # =================================================

        if query.data == "child_type_reaction":

            context.user_data["child_type"] = "reaction"
            context.user_data["child_step"] = 2.5

            await query.message.edit_text(
                "🎨 <b>Inline reaksiya rangini tanlang:</b>",
                parse_mode="HTML",
                reply_markup=style_keyboard("child_style", f"cancel_child_{context.user_data.get('child_parent_index')}")
            )
            return

        if query.data == "reply_child_type_reaction":

            context.user_data["reply_child_type"] = "reaction"
            context.user_data["reply_child_step"] = 2.5

            await query.message.edit_text(
                "🎨 <b>Ichki reaksiya rangini tanlang:</b>",
                parse_mode="HTML",
                reply_markup=style_keyboard("reply_child_style", f"cancel_reply_child_{context.user_data.get('reply_child_parent_index')}")
            )
            return

        # =================================================
        # REACTION CLICK (Foydalanuvchi reaksiya bosganda)
        # =================================================

        if query.data.startswith("reaction_"):

            reaction_uid = query.data.replace("reaction_", "")

            language = get_user_language(user_id) or "uz"

            # MUHIM: to'g'ridan-to'g'ri data dan olish
            if "reactions" not in data:
                data["reactions"] = {}

            if reaction_uid not in data["reactions"]:
                # Eski yoki noto'g'ri saqlangan tugma bo'lsa, tugmaning o'zidan
                # reaction yozuvini tiklab olamiz.
                found = find_reaction_node(
                    data["buttons"].get(language, []), reaction_uid
                )
                if found and found.get("type") == "reaction":
                    data["reactions"][reaction_uid] = {
                        "users": [],
                        "count": 0,
                        "sticker": found.get("content", ""),
                        "name": found.get("name", "Reaksiya")
                    }
                    save_data(data)
                else:
                    await query.answer(
                        "❌ Reaksiya topilmadi.",
                        show_alert=True
                    )
                    return

            reaction_data = data["reactions"][reaction_uid]

            # Sticker ni ko'rsatish
            if reaction_data.get("sticker"):
                try:
                    await query.message.reply_sticker(
                        sticker=reaction_data["sticker"]
                    )
                except Exception:
                    pass

            # Foydalanuvchilar ro'yxatini int ID + unique holatga keltiramiz.
            raw_users = reaction_data.get("users", [])
            users_list = []
            for uid in raw_users:
                try:
                    uid = int(uid)
                except (TypeError, ValueError):
                    continue
                if uid not in users_list:
                    users_list.append(uid)

            if user_id in users_list:
                # Ikkinchi bosishda reaksiya olib tashlanadi.
                users_list.remove(user_id)
                reaction_data["users"] = users_list
                reaction_data["count"] = len(users_list)
                data["reactions"][reaction_uid] = reaction_data
                save_data(data)

                await query.answer(
                    f"❌ Reaksiya bekor qilindi.\n"
                    f"👥 Jami: {reaction_data['count']}",
                    show_alert=True
                )
            else:
                # Bir foydalanuvchi faqat bir marta qo'shiladi.
                users_list.append(user_id)
                reaction_data["users"] = users_list
                reaction_data["count"] = len(users_list)
                data["reactions"][reaction_uid] = reaction_data
                save_data(data)

                await query.answer(
                    f"❤️ Reaksiya qoldirdingiz, rahmat!\n"
                    f"👥 Jami: {reaction_data['count']}",
                    show_alert=True
                )

            # Tugma matnini yangilash
            try:
                button_name = reaction_data.get("name", "Reaksiya")

                new_text = f"{button_name} ({reaction_data['count']})"

                keyboard = query.message.reply_markup.inline_keyboard
                new_keyboard = []

                for row in keyboard:
                    new_row = []
                    for btn in row:
                        if btn.callback_data == query.data:
                            new_row.append(
                                InlineKeyboardButton(
                                    new_text,
                                    callback_data=query.data,
                                    style=btn.style
                                )
                            )
                        else:
                            new_row.append(btn)
                    new_keyboard.append(new_row)

                await query.message.edit_reply_markup(
                    InlineKeyboardMarkup(new_keyboard)
                )
            except Exception:
                pass

            return

        # =================================================
        # CHECK SUBSCRIPTION
        # =================================================

        if query.data == "check_subscription":

            language = get_user_language(
                user_id
            ) or "uz"

            not_subscribed = await check_subscription(
                user_id,
                context.bot
            )

            if not not_subscribed:

                try:

                    await query.message.edit_text(

                        T[language]["subscription_ok"],

                        parse_mode="HTML",

                        link_preview_options=LinkPreviewOptions(
                            is_disabled=True
                        )
                    )

                except BadRequest:

                    pass

                await query.message.reply_text(

                    T[language]["main_menu"],

                    parse_mode="HTML",

                    reply_markup=user_keyboard(
                        language
                    )
                )

            else:

                await subscription_message(
                    update,
                    context,
                    language
                )

            return

        # =================================================
        # OLD INLINE BUTTON (main button children)
        # =================================================

        if (
            query.data.startswith("child_")
            and not query.data.startswith(
                "child_type_"
            )
            and not query.data.startswith(
                "child_index_"
            )
        ):

            parts = query.data.split("_")

            if len(parts) < 3:

                return

            try:

                child_index = int(
                    parts[1]
                )

            except ValueError:

                return

            language = get_user_language(
                user_id
            ) or "uz"

            parent_uid = "_".join(
                parts[2:]
            )

            parent_button = None

            for button in data["buttons"].get(
                language,
                []
            ):

                if button.get(
                    "uid"
                ) == parent_uid:

                    parent_button = button

                    break

            if not parent_button:

                await query.answer(
                    "❌ Tugma topilmadi.",
                    show_alert=True
                )

                return

            inline_buttons = parent_button.get(
                "children",
                []
            )

            if not (
                0 <= child_index
                < len(inline_buttons)
            ):

                await query.answer(
                    "❌ Inline tugma topilmadi.",
                    show_alert=True
                )

                return

            child = inline_buttons[
                child_index
            ]

            if child.get(
                "type"
            ) == "url":

                return

            content = child.get(
                "content",
                ""
            )

            await query.message.reply_text(
                content,
                parse_mode="HTML"
            )

            return

        # =================================================
        # NEW: REPLY CHILD INLINE BUTTON
        # (ichki tugma ichidagi inline tugma)
        # =================================================

        if query.data.startswith("rchild_"):

            parts = query.data.split("_")

            if len(parts) < 3:

                return

            try:

                child_index = int(
                    parts[1]
                )

            except ValueError:

                return

            language = get_user_language(
                user_id
            ) or "uz"

            parent_uid = "_".join(
                parts[2:]
            )

            parent_button = find_reply_button_by_uid(
                data["buttons"].get(
                    language,
                    []
                ),
                parent_uid
            )

            if not parent_button:

                await query.answer(
                    "❌ Tugma topilmadi.",
                    show_alert=True
                )

                return

            inline_buttons = parent_button.get(
                "children",
                []
            )

            if not (
                0 <= child_index
                < len(inline_buttons)
            ):

                await query.answer(
                    "❌ Inline tugma topilmadi.",
                    show_alert=True
                )

                return

            child = inline_buttons[
                child_index
            ]

            if child.get(
                "type"
            ) == "url":

                return

            content = child.get(
                "content",
                ""
            )

            await query.message.reply_text(
                content,
                parse_mode="HTML"
            )

            return

        # =================================================
        # ADMIN CHECK
        # =================================================

        if not is_admin(user_id):

            return

        # =================================================
        # ADMIN MANAGEMENT
        # =================================================

        if query.data == "admin_manage":

            admins = data.get("admins", [ADMIN_ID])

            text = T[admin_lang]["admin_list"]

            if not admins:
                text += T[admin_lang]["no_admins"]
            else:
                for i, admin_id in enumerate(admins, 1):
                    admin_info = None
                    for u in data["users"]:
                        if u["id"] == admin_id:
                            admin_info = u
                            break

                    if admin_info:
                        name = admin_info.get("first_name") or T[admin_lang]["unknown_user"]
                        username = admin_info.get("username", "")
                        username_text = f" (@{username})" if username else ""
                    else:
                        name = T[admin_lang]["unknown_user"]
                        username_text = ""

                    marker = " 👑" if admin_id == ADMIN_ID else ""
                    text += f"{i}. <b>{name}</b>{username_text}{marker}\n"
                    text += f"   🆔 <code>{admin_id}</code>\n\n"

            await query.message.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=admin_manage_keyboard()
            )

            return

        if query.data == "add_admin":

            context.user_data["adding_admin"] = True

            await query.message.edit_text(
                T[admin_lang]["admin_add_prompt"],
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            T[admin_lang]["no_cancel"],
                            callback_data="admin_manage"
                        )
                    ]
                ])
            )

            return

        if query.data == "delete_admin":

            admins = data.get("admins", [ADMIN_ID])

            deletable = [
                a for a in admins
                if a != user_id and a != ADMIN_ID
            ]

            if not deletable:

                await query.answer(
                    "❌ O'chiriladigan admin yo'q!",
                    show_alert=True
                )

                return

            keyboard = []

            for admin_id in deletable:

                admin_info = None
                for u in data["users"]:
                    if u["id"] == admin_id:
                        admin_info = u
                        break

                if admin_info:
                    name = admin_info.get("first_name") or T[admin_lang]["unknown_user"]
                    username = admin_info.get("username", "")
                    display = f"{name} (@{username})" if username else name
                else:
                    display = str(admin_id)

                keyboard.append([
                    InlineKeyboardButton(
                        f"🗑 {display}",
                        callback_data=f"remove_admin_{admin_id}"
                    )
                ])

            keyboard.append([
                InlineKeyboardButton(
                    T[admin_lang]["back"],
                    callback_data="admin_manage"
                )
            ])

            await query.message.edit_text(
                T[admin_lang]["select_delete_admin"],
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return

        if query.data.startswith("remove_admin_"):

            try:
                target_id = int(
                    query.data.replace("remove_admin_", "")
                )
            except ValueError:
                return

            if target_id == user_id:

                await query.answer(
                    T[admin_lang]["admin_cannot_delete_self"],
                    show_alert=True
                )

                return

            if target_id == ADMIN_ID:

                await query.answer(
                    T[admin_lang]["admin_cannot_delete_main"],
                    show_alert=True
                )

                return

            admins = data.get("admins", [ADMIN_ID])

            if target_id in admins:

                admins.remove(target_id)

                save_data(data)

                await query.message.edit_text(
                    T[admin_lang]["admin_deleted"].format(
                        user_id=target_id
                    ),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                T[admin_lang]["admins"],
                                callback_data="admin_manage"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                T[admin_lang]["admin_back"],
                                callback_data="admin_back"
                            )
                        ]
                    ])
                )

            return

        # =================================================
        # ADMIN BACK
        # =================================================

        if query.data == "admin_back":

            context.user_data.clear()

            await query.message.edit_text(

                T[admin_lang]["admin_panel"],

                parse_mode="HTML",

                reply_markup=admin_keyboard()
            )

            return

        # =================================================
        # ADMIN LANGUAGE
        # =================================================

        if query.data == "admin_language":

            await query.message.edit_text(

                T[admin_lang]["admin_language"],

                parse_mode="HTML",

                reply_markup=admin_language_keyboard()
            )

            return

        if query.data.startswith(
            "adminlang_"
        ):

            new_language = query.data.replace(
                "adminlang_",
                ""
            )

            if new_language not in LANGUAGES:

                return

            set_admin_language(
                new_language
            )

            await query.message.edit_text(

                T[new_language][
                    "admin_language_changed"
                ],

                parse_mode="HTML",

                reply_markup=admin_keyboard()
            )

            return

        # =================================================
        # STATISTICS
        # =================================================

        if query.data == "stats":

            text = build_stats_text(admin_lang)

            try:

                await query.message.edit_text(

                    text,

                    parse_mode="HTML",

                    reply_markup=stats_keyboard(admin_lang)
                )

            except BadRequest:

                await query.message.reply_text(

                    text,

                    parse_mode="HTML",

                    reply_markup=stats_keyboard(admin_lang)
                )

            return

        # =================================================
        # START MESSAGE EDITOR
        # =================================================
        if query.data == "start_message":
            await query.message.edit_text(
                "✏️ <b>Start xabarini o‘zgartirish</b>\n\n"
                "Tilni tanlang. Keyin yangi xabar matnini yuboring.\n"
                "<code>{name}</code> — foydalanuvchi ismi.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [admin_style_button("🇺🇿 O‘zbekcha", "startmsg_uz", "primary"),
                     admin_style_button("🇬🇧 English", "startmsg_en", "primary")],
                    [admin_style_button("🇷🇺 Русский", "startmsg_ru", "primary")],
                    [admin_style_button(T[admin_lang]["back"], "admin_back", "default")]
                ])
            )
            return

        if query.data.startswith("startmsg_"):
            language = query.data.replace("startmsg_", "")
            if language not in LANGUAGES:
                return
            context.user_data["editing_start_message"] = language
            current = data.get("start_messages", {}).get(language, "")
            await query.message.edit_text(
                "📝 <b>Yangi start xabarini yuboring.</b>\n\n"
                "<code>{name}</code> — ismni avtomatik qo‘yadi.\n\n"
                "Hozirgi xabar:\n" + (current or "<i>Standart xabar ishlatilmoqda.</i>"),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["back"], "start_message", "default")]])
            )
            return

        # =================================================
        # BROADCAST
        # =================================================

        if query.data == "broadcast":
            context.user_data.clear()
            await query.message.edit_text(
                "🌐 <b>Broadcast uchun tilni tanlang:</b>\n\n"
                "Qaysi tilni tanlasangiz, xabar faqat shu tildagi foydalanuvchilarga yuboriladi.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [admin_style_button("🇺🇿 O‘zbekcha", "bc_lang_uz", "primary"),
                     admin_style_button("🇬🇧 English", "bc_lang_en", "primary")],
                    [admin_style_button("🇷🇺 Русский", "bc_lang_ru", "primary"),
                     admin_style_button("🌍 Barchasi", "bc_lang_all", "success")],
                    [admin_style_button(T[admin_lang]["back"], "admin_back", "default")]
                ])
            )
            return

        if query.data.startswith("bc_lang_"):
            selected = query.data.replace("bc_lang_", "")
            context.user_data["bc_language"] = selected
            await query.message.edit_text(
                T[admin_lang]["broadcast_menu"],
                parse_mode="HTML",
                reply_markup=broadcast_menu_keyboard()
            )
            return

        # =================================================
        # BROADCAST - SIMPLE
        # =================================================

        if query.data == "bc_simple":

            context.user_data["bc_type"] = "simple"

            await query.message.edit_text(

                T[admin_lang]["broadcast_simple_prompt"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["broadcast_cancel"],
                            callback_data="bc_cancel"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - FORWARD
        # =================================================

        if query.data == "bc_forward":

            context.user_data["bc_type"] = "forward"

            await query.message.edit_text(

                T[admin_lang]["broadcast_forward_prompt"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["broadcast_cancel"],
                            callback_data="bc_cancel"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - MEDIA
        # =================================================

        if query.data == "bc_media":

            context.user_data["bc_type"] = "media"

            await query.message.edit_text(

                T[admin_lang]["broadcast_media_prompt"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["broadcast_cancel"],
                            callback_data="bc_cancel"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - SINGLE USER
        # =================================================

        if query.data == "bc_single":

            context.user_data["bc_type"] = "single"

            await query.message.edit_text(

                T[admin_lang]["broadcast_single_prompt"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["broadcast_cancel"],
                            callback_data="bc_cancel"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - PERSONALIZED
        # =================================================

        if query.data == "bc_personalized":

            context.user_data["bc_type"] = "personalized"

            await query.message.edit_text(

                T[admin_lang]["broadcast_personalized_prompt"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["broadcast_cancel"],
                            callback_data="bc_cancel"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - WITH INLINE BUTTON
        # =================================================

        if query.data == "bc_with_button":

            context.user_data["bc_type"] = "with_button"

            context.user_data["bc_step"] = "text"

            context.user_data["bc_buttons"] = []

            await query.message.edit_text(

                T[admin_lang]["broadcast_text_step"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["broadcast_cancel"],
                            callback_data="bc_cancel"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - ADD MORE BUTTON
        # =================================================

        if query.data == "bc_add_more_button":

            context.user_data["bc_step"] = "button_name"

            await query.message.edit_text(

                T[admin_lang]["broadcast_button_name_step"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["broadcast_cancel"],
                            callback_data="bc_cancel"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - START SEND WITH BUTTONS
        # =================================================

        if query.data == "bc_start_send":

            bc_text = context.user_data.get("bc_text", "")

            bc_buttons = context.user_data.get("bc_buttons", [])

            # Inline keyboard yig'ish
            inline_keyboard = None

            if bc_buttons:

                keyboard = []

                for btn in bc_buttons:

                    keyboard.append([

                        InlineKeyboardButton(
                            btn["name"],
                            url=btn["url"]
                        )

                    ])

                inline_keyboard = InlineKeyboardMarkup(keyboard)

            await query.message.edit_text(

                "⏳ <b>Yuborilmoqda...</b>",

                parse_mode="HTML"
            )

            sent, failed = await send_broadcast_with_buttons(
                context,
                bc_text,
                inline_keyboard
            )

            context.user_data.clear()

            await query.message.edit_text(

                T[admin_lang]["broadcast_done"].format(
                    sent=sent,
                    failed=failed
                ),

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["admin_back"],
                            callback_data="admin_back"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # BROADCAST - CANCEL
        # =================================================

        if query.data == "bc_cancel":

            context.user_data.clear()

            await query.message.edit_text(

                T[admin_lang]["broadcast_cancelled"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["admin_back"],
                            callback_data="admin_back"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # CHANNELS
        # =================================================

        if query.data == "channel_list":
            await query.message.edit_text(
                T[admin_lang]["channel_menu_title"],
                parse_mode="HTML",
                reply_markup=channel_manage_keyboard("main")
            )
            return

        if query.data == "public_channels":
            await query.message.edit_text(
                T[admin_lang]["public_channel_menu"],
                parse_mode="HTML",
                reply_markup=channel_manage_keyboard("public")
            )
            return

        if query.data == "private_channels":
            await query.message.edit_text(
                T[admin_lang]["private_channel_menu"],
                parse_mode="HTML",
                reply_markup=channel_manage_keyboard("private")
            )
            return

        if query.data == "channel_settings":
            await query.message.edit_text(
                T[admin_lang]["channel_settings_text"],
                parse_mode="HTML",
                reply_markup=channel_manage_keyboard("settings")
            )
            return

        if query.data == "clear_join_requests":
            data["join_requests"] = {}
            save_data(data)
            await query.answer(T[admin_lang]["join_requests_cleared"], show_alert=True)
            await query.message.edit_text(
                T[admin_lang]["channel_settings_text"],
                parse_mode="HTML",
                reply_markup=channel_manage_keyboard("settings")
            )
            return

        if query.data == "sub_setting_approval":
            settings = data.setdefault("subscription_settings", {})
            settings["approval_required"] = not bool(settings.get("approval_required", True))
            save_data(data)
            await query.message.edit_text(T[admin_lang]["channel_settings_text"], parse_mode="HTML", reply_markup=channel_manage_keyboard("settings"))
            return

        if query.data == "sub_setting_pending":
            settings = data.setdefault("subscription_settings", {})
            settings["allow_pending"] = not bool(settings.get("allow_pending", False))
            save_data(data)
            await query.message.edit_text(T[admin_lang]["channel_settings_text"], parse_mode="HTML", reply_markup=channel_manage_keyboard("settings"))
            return

        if query.data == "sub_setting_auto":
            settings = data.setdefault("subscription_settings", {})
            settings["auto_accept"] = not bool(settings.get("auto_accept", False))
            save_data(data)
            await query.message.edit_text(T[admin_lang]["channel_settings_text"], parse_mode="HTML", reply_markup=channel_manage_keyboard("settings"))
            return

        if query.data == "sub_setting_text":
            language = get_admin_language()
            context.user_data["editing_subscription_text"] = language
            current = data.get("subscription_settings", {}).get("text", {}).get(language, "")
            prompt = T[admin_lang]["subscription_text_prompt"]
            if current:
                prompt += f"\\n\\n<b>Hozirgi matn:</b>\\n{current}"
            await query.message.edit_text(prompt, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
                [admin_style_button(T[admin_lang]["back"], "channel_settings", "default")]
            ]))
            return

        if query.data == "sub_setting_style":
            settings = data.setdefault("subscription_settings", {})
            current = settings.get("channel_style", "primary")
            style_names = {
                "primary": T[admin_lang]["style_primary"],
                "success": T[admin_lang]["style_success"],
                "danger": T[admin_lang]["style_danger"],
                "default": T[admin_lang]["style_default"]
            }
            await query.message.edit_text(
                T[admin_lang]["channel_style_prompt"].format(style=style_names.get(current, current)),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [admin_style_button(T[admin_lang]["style_primary"], "sub_style_primary", "primary")],
                    [admin_style_button(T[admin_lang]["style_success"], "sub_style_success", "success")],
                    [admin_style_button(T[admin_lang]["style_danger"], "sub_style_danger", "danger")],
                    [admin_style_button(T[admin_lang]["style_default"], "sub_style_default", "default")],
                    [admin_style_button(T[admin_lang]["back"], "channel_settings", "default")]
                ])
            )
            return

        if query.data.startswith("sub_style_"):
            style = query.data.replace("sub_style_", "")
            if style not in BUTTON_STYLES:
                return
            data.setdefault("subscription_settings", {})["channel_style"] = style
            save_data(data)
            await query.message.edit_text(T[admin_lang]["channel_settings_text"], parse_mode="HTML", reply_markup=channel_manage_keyboard("settings"))
            return

        if query.data == "add_public_channel":
            context.user_data["adding_channel"] = True
            context.user_data["adding_channel_type"] = "public"
            await query.message.edit_text(
                T[admin_lang]["public_channel_format"],
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    admin_style_button(T[admin_lang]["back"], "public_channels", "default")
                ]])
            )
            return

        if query.data == "add_private_channel":
            context.user_data["adding_channel"] = True
            context.user_data["adding_channel_type"] = "private"
            await query.message.edit_text(
                T[admin_lang]["private_channel_format"],
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    admin_style_button(T[admin_lang]["back"], "private_channels", "default")
                ]])
            )
            return

        # Eski callback nomlari ham ishlashi uchun saqlab qolindi.
        if query.data == "add_channel":
            context.user_data["adding_channel"] = True
            context.user_data["adding_channel_type"] = "public"
            await query.message.edit_text(
                T[admin_lang]["public_channel_format"],
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    admin_style_button(T[admin_lang]["back"], "public_channels", "default")
                ]])
            )
            return

        def _channel_rows(channel_type=None):
            rows = []
            for i, ch in enumerate(data.get("channels", [])):
                ctype = ch.get("type") or ("public" if ch.get("username") else "private")
                if channel_type and ctype != channel_type:
                    continue
                icon = "🌐" if ctype == "public" else "🔐"
                rows.append([
                    admin_style_button(f"{icon} {ch.get('name', 'Kanal')}", f"channel_info_{i}", "default")
                ])
            return rows

        if query.data in {"public_channel_list", "private_channel_list"}:
            ctype = "public" if query.data.startswith("public") else "private"
            rows = _channel_rows(ctype)
            if not rows:
                text = T[admin_lang]["no_channels"]
            else:
                title = T[admin_lang]["public_channels"] if ctype == "public" else T[admin_lang]["private_channels"]
                text = f"<b>{title}</b>\n\n"
                for i, ch in enumerate(data.get("channels", []), 1):
                    real_type = ch.get("type") or ("public" if ch.get("username") else "private")
                    if real_type != ctype:
                        continue
                    text += f"{i}. {'🌐' if ctype == 'public' else '🔐'} <b>{ch.get('name','Kanal')}</b>\n"
                    text += f"🆔 <code>{ch.get('chat_id')}</code>\n"
                    text += f"🔗 {ch.get('url') or ch.get('invite_link','')}\n\n"
            rows.append([admin_style_button(T[admin_lang]["back"], "public_channels" if ctype == "public" else "private_channels", "default")])
            await query.message.edit_text(text, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup(rows))
            return

        if query.data in {"delete_public_channel", "delete_private_channel"}:
            ctype = "public" if query.data.startswith("delete_public") else "private"
            rows = []
            for i, ch in enumerate(data.get("channels", [])):
                real_type = ch.get("type") or ("public" if ch.get("username") else "private")
                if real_type == ctype:
                    rows.append([admin_style_button(f"🗑 {ch.get('name','Kanal')}", f"delete_channel_{i}", "danger")])
            if not rows:
                rows.append([admin_style_button(T[admin_lang]["back"], "public_channels" if ctype == "public" else "private_channels", "default")])
                await query.message.edit_text(T[admin_lang]["no_channels"], parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
            else:
                rows.append([admin_style_button(T[admin_lang]["back"], "public_channels" if ctype == "public" else "private_channels", "default")])
                await query.message.edit_text(T[admin_lang]["select_delete_channel"], parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
            return

        if query.data.startswith("delete_channel_"):
            try:
                index = int(query.data.replace("delete_channel_", ""))
            except ValueError:
                return
            channels = data.get("channels", [])
            if 0 <= index < len(channels):
                channel = channels.pop(index)
                save_data(data)
                await query.answer(T[admin_lang]["channel_deleted"].format(name=channel.get("name", "Kanal")), show_alert=True)
                ctype = channel.get("type") or ("public" if channel.get("username") else "private")
                await query.message.edit_text(
                    T[admin_lang]["public_channel_menu"] if ctype == "public" else T[admin_lang]["private_channel_menu"],
                    parse_mode="HTML", reply_markup=channel_manage_keyboard("public" if ctype == "public" else "private")
                )
            return

        if query.data.startswith("channel_info_"):
            try:
                index = int(query.data.replace("channel_info_", ""))
                channel = data.get("channels", [])[index]
            except (ValueError, IndexError):
                return
            ctype = channel.get("type") or ("public" if channel.get("username") else "private")
            text = (
                f"<b>{channel.get('name','Kanal')}</b>\n\n"
                f"{T[admin_lang]['channel_type_public'] if ctype == 'public' else T[admin_lang]['channel_type_private']}\n"
                f"🆔 <code>{channel.get('chat_id')}</code>\n"
                f"🔗 {channel.get('url') or channel.get('invite_link','')}"
            )
            await query.message.edit_text(text, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["back"], "public_channel_list" if ctype == "public" else "private_channel_list", "default")]]))
            return

        # =================================================
        # BUTTONS MAIN LIST
        # =================================================

        if query.data == "button_list":
            await query.message.edit_text(
                T[admin_lang]["select_language_buttons"],
                parse_mode="HTML",
                reply_markup=buttons_language_keyboard()
            )
            return

        # =================================================
        # BUTTON LANGUAGE
        # =================================================

        if query.data.startswith(
            "buttons_"
        ):

            language = query.data.replace(
                "buttons_",
                ""
            )

            if language not in LANGUAGES:

                return

            context.user_data[
                "admin_language_section"
            ] = language

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            text = (
                f"<b>{T[admin_lang]['buttons']}</b>\n\n"
                f"🌐 <b>{LANGUAGES[language]}</b>\n\n"
            )

            if not buttons:

                text += T[
                    admin_lang
                ]["no_buttons"]

            else:

                icons = {

                    "text":
                        "📝",

                    "photo":
                        "🖼",

                    "video":
                        "🎥",

                    "document":
                        "📄",

                    "audio":
                        "🎵",

                    "voice":
                        "🎤"

                }

                for i, button in enumerate(
                    buttons,
                    1
                ):

                    icon = icons.get(
                        button.get(
                            "type",
                            "text"
                        ),
                        "📝"
                    )

                    inline_count = len(
                        button.get(
                            "children",
                            []
                        )
                    )

                    reply_count = len(
                        button.get(
                            "reply_children",
                            []
                        )
                    )

                    text += (

                        f"{i}. {icon} "
                        f"<b>{button['name']}</b>\n"

                        f"   🔗 Inline: "
                        f"<b>{inline_count}</b> | "

                        f"📂 Ichki: "
                        f"<b>{reply_count}</b>\n\n"

                    )

            keyboard = []

            for i, button in enumerate(buttons):
                obj = admin_style_button(
                    f"⚙️ {button['name']}",
                    f"manage_button_{i}",
                    button.get("style", "default")
                )
                if keyboard and len(keyboard[-1]) == 1 and len(keyboard[-1][0].text) < 22 and len(obj.text) < 22:
                    keyboard[-1].append(obj)
                else:
                    keyboard.append([obj])

            keyboard.append([
                admin_style_button(T[admin_lang]["add_button"], "add_button", "success"),
                admin_style_button(T[admin_lang]["delete_button"], "delete_button", "danger")
            ])

            keyboard.append([

                InlineKeyboardButton(
                    T[admin_lang]["back"],
                    callback_data="button_list"
                )

            ])

            await query.message.edit_text(

                text,

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

            return

        # =================================================
        # MANAGE BUTTON
        # =================================================

        if query.data.startswith(
            "manage_button_"
        ):

            try:

                index = int(
                    query.data.replace(
                        "manage_button_",
                        ""
                    )
                )

            except ValueError:

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not (
                0 <= index < len(buttons)
            ):

                return

            button = buttons[index]

            inline_buttons = button.get(
                "children",
                []
            )

            reply_children = button.get(
                "reply_children",
                []
            )

            text = (

                f"🔘 <b>{button['name']}</b>\n\n"

                f"🔗 Inline tugmalar: "
                f"<b>{len(inline_buttons)}</b>\n"

                f"📂 Ichki tugmalar: "
                f"<b>{len(reply_children)}</b>\n\n"

            )

            if inline_buttons:

                text += (
                    "<b>🔗 Inline tugmalar:</b>\n"
                )

                for i, child in enumerate(
                    inline_buttons,
                    1
                ):

                    child_type = child.get(
                        "type",
                        "text"
                    )

                    icon = (
                        "🔗"
                        if child_type == "url"
                        else "📝"
                    )

                    text += (

                        f"{i}. {icon} "
                        f"<b>{child['name']}</b>\n"

                    )

                text += "\n"

            if reply_children:

                text += (
                    "<b>📂 Ichki tugmalar:</b>\n"
                )

                for i, child in enumerate(
                    reply_children,
                    1
                ):

                    text += (

                        f"{i}. 📂 "
                        f"<b>{child['name']}</b>\n"

                    )

                text += "\n"

            if (
                not inline_buttons
                and not reply_children
            ):

                text += (
                    "❌ Qo‘shimcha tugmalar mavjud emas."
                )

            keyboard = []
            if reply_children:
                for ci, child in enumerate(reply_children):
                    keyboard.append([admin_style_button(f"📂 {ci+1}. {child.get('name','Button')}", f"manage_reply_child_{index}_{ci}", child.get("style","default"))])

            keyboard += [

                [
                    admin_style_button(
                        T[admin_lang]["inline_button"],
                        callback_data=(
                            f"add_child_{index}"
                        )
                    )
                ],

                [
                    admin_style_button(T[admin_lang]["delete_inline"], f"delete_child_{index}", "danger")
                ],

                [
                    admin_style_button(T[admin_lang]["reply_child"], f"add_reply_child_{index}", "success")
                ],

                [
                    admin_style_button(T[admin_lang]["delete_reply_child"], f"delete_reply_child_{index}", "danger")
                ],

                [
                    InlineKeyboardButton(
                        "↔️ Asosiy joylashuv",
                        callback_data="layout_main"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "↔️ Inline joylashuv",
                        callback_data=f"layout_inline_{index}"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "↔️ Ichki joylashuv",
                        callback_data=f"layout_reply_{index}"
                    )
                ],

                [
                    InlineKeyboardButton(
                        T[admin_lang]["rename_button"],
                        callback_data=(
                            f"rename_button_{index}"
                        )
                    )
                ],

                [
                    admin_style_button("➕ Xabar qo‘shish", f"add_content_{button.get('uid')}", "success"),
                    admin_style_button(T[admin_lang]["preview_button"], f"preview_button_{index}", "primary")
                ],

                [
                    InlineKeyboardButton(
                        T[admin_lang]["back"],
                        callback_data=(
                            f"buttons_{language}"
                        )
                    )
                ]

            ]

            await query.message.edit_text(

                text,

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

            return

        # =================================================
        # ADD EXTRA MESSAGE TO ANY BUTTON
        # =================================================
        if query.data.startswith("add_content_"):
            uid = query.data.replace("add_content_", "")
            node = find_any_button_node(data.get("buttons", {}).get(context.user_data.get("admin_language_section", "uz"), []), uid)
            if not node:
                await query.answer("❌ Tugma topilmadi.", show_alert=True)
                return
            context.user_data["adding_extra_content_uid"] = uid
            await query.message.edit_text(
                "➕ <b>Qo‘shimcha xabar yuboring</b>\n\nMatn, rasm, video, fayl, audio yoki voice yuborishingiz mumkin.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[admin_style_button("❌ Bekor qilish", "cancel_extra_content", "danger")]])
            )
            return

        if query.data == "cancel_extra_content":
            context.user_data.pop("adding_extra_content_uid", None)
            await query.message.edit_text("❌ Bekor qilindi.", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["admin_back"], "admin_back", "default")]]))
            return

        # =================================================
        # MANAGE INNER BUTTON
        # =================================================
        if query.data.startswith("manage_reply_child_"):
            parts = query.data.replace("manage_reply_child_", "").split("_")
            if len(parts) != 2:
                return
            try:
                parent_index, child_index = map(int, parts)
            except ValueError:
                return
            language = context.user_data.get("admin_language_section", "uz")
            buttons = data.get("buttons", {}).get(language, [])
            if not (0 <= parent_index < len(buttons)):
                return
            children = buttons[parent_index].get("reply_children", [])
            if not (0 <= child_index < len(children)):
                return
            child = children[child_index]
            text = f"📂 <b>{child.get('name','Button')}</b>\n\n"
            text += f"💬 Xabarlar: <b>{len(get_node_contents(child))}</b>\n"
            text += f"🔗 Inline tugmalar: <b>{len(child.get('children', []))}</b>"
            keyboard=[
                [admin_style_button("➕ Xabar qo‘shish", f"add_content_{child.get('uid')}", "success"),
                 admin_style_button("🔗 Inline qo‘shish", f"add_inner_inline_{parent_index}_{child_index}", "primary")],
                [admin_style_button("🗑 Inline o‘chirish", f"delete_inner_inline_{parent_index}_{child_index}", "danger")],
                [admin_style_button("👁 Ko‘rish", f"preview_reply_child_{parent_index}_{child_index}", "primary")],
                [admin_style_button(T[admin_lang]["back"], f"manage_button_{parent_index}", "default")]
            ]
            await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        if query.data.startswith("preview_reply_child_"):
            parts=query.data.replace("preview_reply_child_","").split("_")
            if len(parts)!=2:return
            try: parent_index,child_index=map(int,parts)
            except ValueError:return
            language=context.user_data.get("admin_language_section","uz")
            buttons=data.get("buttons",{}).get(language,[])
            if not (0<=parent_index<len(buttons)):return
            children=buttons[parent_index].get("reply_children",[])
            if not (0<=child_index<len(children)):return
            await send_reply_child_content(query.message, children[child_index], language)
            return

        if query.data.startswith("delete_inner_inline_"):
            parts=query.data.replace("delete_inner_inline_","").split("_")
            if len(parts)!=2:return
            try: parent_index,child_index=map(int,parts)
            except ValueError:return
            language=context.user_data.get("admin_language_section","uz")
            buttons=data.get("buttons",{}).get(language,[])
            if not (0<=parent_index<len(buttons)):return
            children=buttons[parent_index].get("reply_children",[])
            if not (0<=child_index<len(children)):return
            inline=children[child_index].get("children",[])
            if not inline:
                await query.answer("❌ Inline tugma yo‘q.",show_alert=True); return
            removed=inline.pop()
            save_data(data)
            await query.answer(f"🗑 {removed.get('name','Inline')} o‘chirildi.",show_alert=True)
            return

        if query.data.startswith("add_inner_inline_"):
            parts=query.data.replace("add_inner_inline_","").split("_")
            if len(parts)!=2:return
            try: parent_index,child_index=map(int,parts)
            except ValueError:return
            context.user_data["adding_inner_inline"] = True
            context.user_data["inner_parent_index"] = parent_index
            context.user_data["inner_child_index"] = child_index
            context.user_data["inner_inline_step"] = 1
            await query.message.edit_text("🔗 <b>Inline tugma nomini yuboring:</b>",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[admin_style_button("❌ Bekor qilish","cancel_inner_inline","danger")]]))
            return

        if query.data == "cancel_inner_inline":
            for k in ["adding_inner_inline","inner_parent_index","inner_child_index","inner_inline_step","inner_inline_name","inner_inline_style"]:
                context.user_data.pop(k,None)
            await query.message.edit_text("❌ Bekor qilindi.",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["admin_back"],"admin_back","default")]]))
            return

        # =================================================
        # PREVIEW BUTTON
        # =================================================

        if query.data.startswith(
            "preview_button_"
        ):

            try:

                index = int(
                    query.data.replace(
                        "preview_button_",
                        ""
                    )
                )

            except ValueError:

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not (
                0 <= index < len(buttons)
            ):

                return

            button = buttons[index]

            await send_button_content(

                query.message,

                button,

                language
            )

            return

        # =================================================
        # RENAME BUTTON
        # =================================================

        if query.data.startswith(
            "rename_button_"
        ):

            try:

                index = int(
                    query.data.replace(
                        "rename_button_",
                        ""
                    )
                )

            except ValueError:

                return

            context.user_data[
                "renaming_button"
            ] = index

            await query.message.edit_text(

                T[admin_lang][
                    "edit_button_name"
                ],

                parse_mode="HTML"
            )

            return

        # =================================================
        # ADD OLD INLINE BUTTON
        # =================================================

        if query.data.startswith(
            "add_child_"
        ):

            try:

                parent_index = int(
                    query.data.replace(
                        "add_child_",
                        ""
                    )
                )

            except ValueError:

                return

            context.user_data[
                "adding_child"
            ] = True

            context.user_data[
                "child_step"
            ] = 1

            context.user_data[
                "child_parent_index"
            ] = parent_index

            await query.message.edit_text(

                T[admin_lang][
                    "inline_name_prompt"
                ],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["no_cancel"],
                            callback_data=(
                                f"cancel_child_{parent_index}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # CANCEL CHILD
        # =================================================

        if query.data.startswith(
            "cancel_child_"
        ):

            try:

                parent_index = int(
                    query.data.replace(
                        "cancel_child_",
                        ""
                    )
                )

            except ValueError:

                return

            for key in [
                "adding_child",
                "child_step",
                "child_type",
                "child_parent_index",
                "new_child_name",
                "new_child_style"
            ]:

                context.user_data.pop(key, None)

            await query.message.edit_text(

                T[admin_lang]["cancelled"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["back"],
                            callback_data=(
                                f"manage_button_{parent_index}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # OLD INLINE TYPE
        # =================================================

        if query.data == "child_type_url":

            context.user_data[
                "child_type"
            ] = "url"

            context.user_data[
                "child_step"
            ] = 2.5

            await query.message.edit_text(
                "🎨 <b>Inline tugma rangini tanlang:</b>",
                parse_mode="HTML",
                reply_markup=style_keyboard("child_style", f"cancel_child_{context.user_data.get('child_parent_index')}")
            )

            return

        if query.data == "child_type_text":

            context.user_data[
                "child_type"
            ] = "text"

            context.user_data[
                "child_step"
            ] = 2.5

            await query.message.edit_text(
                "🎨 <b>Inline tugma rangini tanlang:</b>",
                parse_mode="HTML",
                reply_markup=style_keyboard("child_style", f"cancel_child_{context.user_data.get('child_parent_index')}")
            )

            return

        # =================================================
        # REPLY CHILD STYLE
        # =================================================

        if query.data.startswith("reply_style_"):
            style = query.data.replace("reply_style_", "")
            context.user_data["new_reply_child_style"] = style
            context.user_data["reply_child_step"] = 2
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(T[admin_lang]["type_text"], callback_data="reply_child_type_text")],
                [InlineKeyboardButton(T[admin_lang]["type_url"], callback_data="reply_child_type_url")],
                [InlineKeyboardButton(T[admin_lang]["type_photo"], callback_data="reply_child_type_photo")],
                [InlineKeyboardButton(T[admin_lang]["type_video"], callback_data="reply_child_type_video")],
                [InlineKeyboardButton(T[admin_lang]["type_document"], callback_data="reply_child_type_document")],
                [InlineKeyboardButton(T[admin_lang]["type_audio"], callback_data="reply_child_type_audio")],
                [InlineKeyboardButton(T[admin_lang]["type_voice"], callback_data="reply_child_type_voice")],
                [InlineKeyboardButton(T[admin_lang]["type_inline"], callback_data="reply_child_type_inline")],
                [InlineKeyboardButton("🎯 Reaksiya", callback_data="reply_child_type_reaction")],
                [InlineKeyboardButton(T[admin_lang]["no_cancel"], callback_data=f"cancel_reply_child_{context.user_data.get('reply_child_parent_index')}")]
            ])
            await query.message.edit_text(T[admin_lang]["reply_child_type"], parse_mode="HTML", reply_markup=keyboard)
            return

        # =================================================
        # INLINE CHILD STYLE
        # =================================================

        if query.data.startswith("child_style_"):
            style = query.data.replace("child_style_", "")
            context.user_data["new_child_style"] = style
            context.user_data["child_step"] = 3
            child_type = context.user_data.get("child_type")
            if child_type == "url":
                prompt = T[admin_lang]["inline_url_prompt"]
            elif child_type == "text":
                prompt = T[admin_lang]["inline_text_prompt"]
            else:
                prompt = "🎯 <b>Reaksiya uchun sticker yuboring:</b>"
            await query.message.edit_text(prompt, parse_mode="HTML")
            return

        # =================================================
        # INNER REACTION STYLE
        # =================================================

        if query.data.startswith("reply_child_style_"):
            style = query.data.replace("reply_child_style_", "")
            context.user_data["new_reply_child_style"] = style
            context.user_data["reply_child_step"] = 3
            await query.message.edit_text("🎯 <b>Reaksiya uchun sticker yuboring:</b>", parse_mode="HTML")
            return

        # =================================================
        # REPLY INLINE STYLE
        # =================================================

        if query.data.startswith("reply_inline_style_"):
            style = query.data.replace("reply_inline_style_", "")
            context.user_data["new_reply_inline_style"] = style
            context.user_data["reply_child_step"] = 5
            await query.message.edit_text(
                T[admin_lang]["reply_child_inline_url_prompt"],
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(T[admin_lang]["no_cancel"], callback_data=f"cancel_reply_child_{context.user_data.get('reply_child_parent_index')}")]])
            )
            return

        if query.data.startswith("inner_inline_style_"):
            style=query.data.replace("inner_inline_style_","")
            context.user_data["inner_inline_style"]=style
            context.user_data["inner_inline_step"]=2.5
            await query.message.edit_text("🔘 <b>Inline tugma turini tanlang:</b>",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[admin_style_button("🔗 URL","inner_inline_type_url","primary"),admin_style_button("📝 Matn","inner_inline_type_text","primary")],[admin_style_button("🎯 Reaksiya","inner_inline_type_reaction","success")],[admin_style_button("❌ Bekor qilish","cancel_inner_inline","danger")]]))
            return
        if query.data.startswith("inner_inline_type_"):
            typ=query.data.replace("inner_inline_type_","")
            context.user_data["inner_inline_type"]=typ
            if typ=="reaction":
                context.user_data["inner_inline_step"]=3
                context.user_data["inner_inline_reaction"]=True
                await query.message.edit_text("🎯 <b>Reaksiya uchun sticker yuboring:</b>",parse_mode="HTML")
            else:
                context.user_data["inner_inline_step"]=3
                await query.message.edit_text("🔗 <b>URL yoki matnni yuboring:</b>",parse_mode="HTML")
            return

        # =================================================
        # ADD REPLY CHILD
        # =================================================

        if query.data.startswith(
            "add_reply_child_"
        ):

            try:

                parent_index = int(
                    query.data.replace(
                        "add_reply_child_",
                        ""
                    )
                )

            except ValueError:

                return

            context.user_data[
                "adding_reply_child"
            ] = True

            context.user_data[
                "reply_child_step"
            ] = 1

            context.user_data[
                "reply_child_parent_index"
            ] = parent_index

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_name_prompt"
                ],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["no_cancel"],
                            callback_data=(
                                f"cancel_reply_child_{parent_index}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # CANCEL REPLY CHILD
        # =================================================

        if query.data.startswith(
            "cancel_reply_child_"
        ):

            try:

                parent_index = int(
                    query.data.replace(
                        "cancel_reply_child_",
                        ""
                    )
                )

            except ValueError:

                return

            for key in [
                "adding_reply_child",
                "reply_child_step",
                "reply_child_type",
                "reply_child_parent_index",
                "new_reply_child_name",
                "new_inline_name",
                "new_reply_child_style"
            ]:

                context.user_data.pop(key, None)

            await query.message.edit_text(

                T[admin_lang]["cancelled"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["back"],
                            callback_data=(
                                f"manage_button_{parent_index}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # REPLY CHILD TYPE
        # =================================================

        if query.data == "reply_child_type_url":

            context.user_data[
                "reply_child_type"
            ] = "url"

            context.user_data[
                "reply_child_step"
            ] = 3

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_url_prompt"
                ],

                parse_mode="HTML"
            )

            return

        if query.data == "reply_child_type_text":

            context.user_data[
                "reply_child_type"
            ] = "text"

            context.user_data[
                "reply_child_step"
            ] = 3

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_text_prompt"
                ],

                parse_mode="HTML"
            )

            return

        if query.data == "reply_child_type_photo":

            context.user_data[
                "reply_child_type"
            ] = "photo"

            context.user_data[
                "reply_child_step"
            ] = 3

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_media_prompt"
                ],

                parse_mode="HTML"
            )

            return

        if query.data == "reply_child_type_video":

            context.user_data[
                "reply_child_type"
            ] = "video"

            context.user_data[
                "reply_child_step"
            ] = 3

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_media_prompt"
                ],

                parse_mode="HTML"
            )

            return

        if query.data == "reply_child_type_document":

            context.user_data[
                "reply_child_type"
            ] = "document"

            context.user_data[
                "reply_child_step"
            ] = 3

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_media_prompt"
                ],

                parse_mode="HTML"
            )

            return

        if query.data == "reply_child_type_audio":

            context.user_data[
                "reply_child_type"
            ] = "audio"

            context.user_data[
                "reply_child_step"
            ] = 3

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_media_prompt"
                ],

                parse_mode="HTML"
            )

            return

        if query.data == "reply_child_type_voice":

            context.user_data[
                "reply_child_type"
            ] = "voice"

            context.user_data[
                "reply_child_step"
            ] = 3

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_media_prompt"
                ],

                parse_mode="HTML"
            )

            return

        if query.data == "reply_child_type_inline":

            context.user_data[
                "reply_child_type"
            ] = "inline"

            context.user_data[
                "reply_child_step"
            ] = 4

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_inline_name_prompt"
                ],

                parse_mode="HTML"
            )

            return

        # =================================================
        # DELETE INLINE
        # =================================================

        if query.data.startswith(
            "delete_child_"
        ):

            try:

                parent_index = int(
                    query.data.replace(
                        "delete_child_",
                        ""
                    )
                )

            except ValueError:

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not (
                0 <= parent_index
                < len(buttons)
            ):

                return

            children = buttons[
                parent_index
            ].get(
                "children",
                []
            )

            if not children:

                await query.answer(
                    "❌ Inline tugmalar mavjud emas!",
                    show_alert=True
                )

                return

            keyboard = []

            for i, child in enumerate(
                children
            ):

                keyboard.append([

                    InlineKeyboardButton(

                        f"🗑 {i + 1}. "
                        f"{child['name']}",

                        callback_data=(
                            f"remove_child_"
                            f"{parent_index}_"
                            f"{i}"
                        )
                    )

                ])

            keyboard.append([

                InlineKeyboardButton(
                    T[admin_lang]["back"],
                    callback_data=(
                        f"manage_button_"
                        f"{parent_index}"
                    )
                )

            ])

            await query.message.edit_text(

                T[admin_lang][
                    "delete_inline"
                ],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

            return

        # =================================================
        # REMOVE INLINE
        # =================================================

        if query.data.startswith(
            "remove_child_"
        ):

            try:

                parts = query.data.split("_")

                parent_index = int(
                    parts[2]
                )

                child_index = int(
                    parts[3]
                )

            except (
                ValueError,
                IndexError
            ):

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not (
                0 <= parent_index
                < len(buttons)
            ):

                return

            children = buttons[
                parent_index
            ].get(
                "children",
                []
            )

            if not (
                0 <= child_index
                < len(children)
            ):

                return

            removed = children.pop(
                child_index
            )

            save_data(data)

            await query.message.edit_text(

                T[admin_lang][
                    "inline_deleted"
                ].format(
                    name=removed["name"]
                ),

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["back"],
                            callback_data=(
                                f"manage_button_"
                                f"{parent_index}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # DELETE REPLY CHILD
        # =================================================

        if query.data.startswith(
            "delete_reply_child_"
        ):

            try:

                parent_index = int(
                    query.data.replace(
                        "delete_reply_child_",
                        ""
                    )
                )

            except ValueError:

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not (
                0 <= parent_index
                < len(buttons)
            ):

                return

            children = buttons[
                parent_index
            ].get(
                "reply_children",
                []
            )

            if not children:

                await query.answer(
                    "❌ Ichki tugmalar mavjud emas!",
                    show_alert=True
                )

                return

            keyboard = []

            for i, child in enumerate(
                children
            ):

                keyboard.append([

                    InlineKeyboardButton(

                        f"🗑 {i + 1}. "
                        f"{child['name']}",

                        callback_data=(
                            f"remove_reply_child_"
                            f"{parent_index}_"
                            f"{i}"
                        )
                    )

                ])

            keyboard.append([

                InlineKeyboardButton(
                    T[admin_lang]["back"],
                    callback_data=(
                        f"manage_button_"
                        f"{parent_index}"
                    )
                )

            ])

            await query.message.edit_text(

                T[admin_lang][
                    "select_delete_reply_child"
                ],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

            return

        # =================================================
        # REMOVE REPLY CHILD
        # =================================================

        if query.data.startswith(
            "remove_reply_child_"
        ):

            try:

                parts = query.data.split("_")

                parent_index = int(
                    parts[3]
                )

                child_index = int(
                    parts[4]
                )

            except (
                ValueError,
                IndexError
            ):

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not (
                0 <= parent_index
                < len(buttons)
            ):

                return

            children = buttons[
                parent_index
            ].get(
                "reply_children",
                []
            )

            if not (
                0 <= child_index
                < len(children)
            ):

                return

            removed = children.pop(
                child_index
            )

            save_data(data)

            await query.message.edit_text(

                T[admin_lang][
                    "reply_child_deleted"
                ].format(
                    name=removed["name"]
                ),

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["back"],
                            callback_data=(
                                f"manage_button_"
                                f"{parent_index}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # MAIN BUTTON STYLE
        # =================================================

        if query.data.startswith("main_style_"):
            style = query.data.replace("main_style_", "")
            context.user_data["new_button_style"] = style
            context.user_data["button_step"] = 2
            await query.message.edit_text(
                T[admin_lang]["button_content"],
                parse_mode="HTML"
            )
            return

        # =================================================
        # BUTTON LAYOUT SETTINGS
        # =================================================

        if query.data == "layout_main":
            language = context.user_data.get("admin_language_section", "uz")
            current = data.get("layouts", {}).get(language, {}).get("main", "default")
            await query.message.edit_text(
                f"↔️ <b>Asosiy tugmalar joylashuvi</b>\n\nHozirgi: <b>{current}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚡ Avto sozlash", callback_data="layout_main_auto")],
                    [InlineKeyboardButton("✋ Qo'lda sozlash", callback_data="layout_main_manual")],
                    [InlineKeyboardButton("↩️ Asliga qaytarish", callback_data="layout_main_reset")],
                    [InlineKeyboardButton(T[admin_lang]["back"], callback_data=f"buttons_{language}")]
                ])
            )
            return

        if query.data in ("layout_main_auto", "layout_main_reset"):
            language = context.user_data.get("admin_language_section", "uz")
            layouts = data.setdefault("layouts", {}).setdefault(language, {})
            layouts["main"] = "auto" if query.data.endswith("auto") else "default"
            if query.data.endswith("reset"):
                layouts.pop("main_rows", None)
            save_data(data)
            await query.message.edit_text(
                "✅ Joylashuv saqlandi.", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(T[admin_lang]["back"], callback_data="layout_main")]])
            )
            return

        if query.data == "layout_main_manual":
            context.user_data["manual_layout_target"] = ("main", context.user_data.get("admin_language_section", "uz"))
            await query.message.edit_text(
                "✋ <b>Qatorlarni kiriting</b>\n\nMasalan: <code>1,2,2,1</code>\n1 = bitta, 2 = ikkita tugma bir qatorda.",
                parse_mode="HTML"
            )
            return

        for prefix, field in (("layout_inline_", "inline"), ("layout_reply_", "reply")):
            if query.data.startswith(prefix) and query.data[len(prefix):].isdigit():
                parent_index = int(query.data[len(prefix):])
                language = context.user_data.get("admin_language_section", "uz")
                buttons = data.get("buttons", {}).get(language, [])
                if not (0 <= parent_index < len(buttons)):
                    return
                parent = buttons[parent_index]
                current = parent.get(field + "_layout", "default")
                title = "Inline" if field == "inline" else "Ichki"
                await query.message.edit_text(
                    f"↔️ <b>{title} tugmalar joylashuvi</b>\n\nHozirgi: <b>{current}</b>",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⚡ Avto sozlash", callback_data=f"layout_{field}_auto_{parent_index}")],
                        [InlineKeyboardButton("✋ Qo'lda sozlash", callback_data=f"layout_{field}_manual_{parent_index}")],
                        [InlineKeyboardButton("↩️ Asliga qaytarish", callback_data=f"layout_{field}_reset_{parent_index}")],
                        [InlineKeyboardButton(T[admin_lang]["back"], callback_data=f"manage_button_{parent_index}")]
                    ])
                )
                return

        for field in ("inline", "reply"):
            if query.data.startswith(f"layout_{field}_"):
                parts = query.data.split("_")
                if len(parts) != 4 or not parts[3].isdigit():
                    return
                mode, parent_index = parts[2], int(parts[3])
                language = context.user_data.get("admin_language_section", "uz")
                buttons = data.get("buttons", {}).get(language, [])
                if not (0 <= parent_index < len(buttons)):
                    return
                parent = buttons[parent_index]
                if mode == "manual":
                    context.user_data["manual_layout_target"] = (field, language, parent_index)
                    await query.message.edit_text(
                        "✋ <b>Qatorlarni kiriting</b>\n\nMasalan: <code>1,2,2,1</code>",
                        parse_mode="HTML"
                    )
                    return
                parent[field + "_layout"] = "auto" if mode == "auto" else "default"
                if mode == "reset":
                    parent.pop(field + "_rows", None)
                save_data(data)
                await query.message.edit_text(
                    "✅ Joylashuv saqlandi.", parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(T[admin_lang]["back"], callback_data=f"layout_{field}_{parent_index}")]])
                )
                return

        # =================================================
        # ADD BUTTON
        # =================================================

        if query.data == "add_button":

            context.user_data[
                "adding_button"
            ] = True

            context.user_data[
                "button_step"
            ] = 1

            await query.message.edit_text(

                T[admin_lang][
                    "button_name"
                ],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["no_cancel"],
                            callback_data="cancel_add_button"
                        )
                    ]

                ])
            )

            return

        # =================================================
        # CANCEL ADD BUTTON
        # =================================================

        if query.data == "cancel_add_button":

            for key in [
                "adding_button",
                "button_step",
                "new_button_name",
                "new_button_style"
            ]:

                context.user_data.pop(key, None)

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            await query.message.edit_text(

                T[admin_lang]["cancelled"],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["back"],
                            callback_data=(
                                f"buttons_{language}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # DELETE BUTTON
        # =================================================

        if query.data == "delete_button":

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not buttons:

                await query.message.edit_text(

                    T[admin_lang][
                        "no_buttons"
                    ],

                    parse_mode="HTML",

                    reply_markup=InlineKeyboardMarkup([

                        [
                            InlineKeyboardButton(
                                T[admin_lang]["back"],
                                callback_data=(
                                    f"buttons_{language}"
                                )
                            )
                        ]

                    ])
                )

                return

            keyboard = []

            for i, button in enumerate(
                buttons
            ):

                keyboard.append([

                    InlineKeyboardButton(

                        f"🗑 {i + 1}. "
                        f"{button['name']}",

                        callback_data=(
                            f"confirm_remove_button_{i}"
                        )
                    )

                ])

            keyboard.append([

                InlineKeyboardButton(
                    T[admin_lang]["back"],
                    callback_data=(
                        f"buttons_{language}"
                    )
                )

            ])

            await query.message.edit_text(

                T[admin_lang][
                    "select_delete_button"
                ],

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

            return

        # =================================================
        # CONFIRM REMOVE BUTTON
        # =================================================

        if query.data.startswith(
            "confirm_remove_button_"
        ):

            try:

                index = int(
                    query.data.replace(
                        "confirm_remove_button_",
                        ""
                    )
                )

            except ValueError:

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if not (
                0 <= index
                < len(buttons)
            ):

                return

            button = buttons[index]

            await query.message.edit_text(

                f"{T[admin_lang]['confirm_delete']}\n\n"
                f"🔘 <b>{button['name']}</b>",

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["yes_delete"],
                            callback_data=(
                                f"remove_button_{index}"
                            )
                        )
                    ],

                    [
                        InlineKeyboardButton(
                            T[admin_lang]["no_cancel"],
                            callback_data=(
                                f"buttons_{language}"
                            )
                        )
                    ]

                ])
            )

            return

        # =================================================
        # REMOVE BUTTON
        # =================================================

        if query.data.startswith(
            "remove_button_"
        ):

            try:

                index = int(
                    query.data.replace(
                        "remove_button_",
                        ""
                    )
                )

            except ValueError:

                return

            language = context.user_data.get(
                "admin_language_section",
                "uz"
            )

            buttons = data[
                "buttons"
            ].get(
                language,
                []
            )

            if 0 <= index < len(buttons):

                button = buttons.pop(
                    index
                )

                save_data(data)

                await query.message.edit_text(

                    T[admin_lang][
                        "button_deleted"
                    ].format(
                        name=button["name"]
                    ),

                    parse_mode="HTML",

                    reply_markup=InlineKeyboardMarkup([

                        [
                            InlineKeyboardButton(
                                T[admin_lang]["buttons"],
                                callback_data=(
                                    f"buttons_{language}"
                                )
                            )
                        ],

                        [
                            InlineKeyboardButton(
                                T[admin_lang]["admin_back"],
                                callback_data="admin_back"
                            )
                        ]

                    ])
                )

            return

    except Exception as e:

        logger.error(
            f"Callback handler error: {e}",
            exc_info=True
        )

        try:

            await query.answer(
                T[admin_lang][
                    "error_occurred"
                ],
                show_alert=True
            )

        except Exception:

            pass


# =========================================================
# MEDIA HANDLER
# =========================================================

async def media_handler(
    update,
    context
):

    user = update.effective_user

    if not is_admin(user.id):

        return

    message = update.message

    admin_lang = get_admin_language()

    # =====================================================
    # EXTRA CONTENT FOR BUTTON
    # =====================================================
    if context.user_data.get("adding_extra_content_uid"):
        uid = context.user_data.pop("adding_extra_content_uid")
        language = context.user_data.get("admin_language_section", "uz")
        node = find_any_button_node(data.get("buttons", {}).get(language, []), uid)
        if not node:
            await update.message.reply_text("❌ Tugma topilmadi.")
            return
        content_type = None; content = None; caption = message.caption or ""
        if message.photo: content_type="photo"; content=message.photo[-1].file_id
        elif message.video: content_type="video"; content=message.video.file_id
        elif message.document: content_type="document"; content=message.document.file_id
        elif message.audio: content_type="audio"; content=message.audio.file_id
        elif message.voice: content_type="voice"; content=message.voice.file_id
        if not content_type:
            await update.message.reply_text("❌ Bu fayl turi qo‘llanmaydi.")
            return
        append_node_content(node, content_type, content, caption)
        save_data(data)
        await update.message.reply_text("✅ <b>Qo‘shimcha xabar qo‘shildi!</b>", parse_mode="HTML", reply_markup=admin_keyboard())
        return

    # =====================================================
    # BROADCAST MEDIA
    # =====================================================

    bc_type = context.user_data.get("bc_type")

    if bc_type == "media":

        context.user_data["bc_type"] = None

        await process_broadcast(
            update,
            context,
            media=True
        )

        return

    # Eski broadcasting (zaxira)
    if context.user_data.get("broadcasting"):

        await process_broadcast(
            update,
            context,
            media=True
        )

        return
        
    if bc_type == "forward":

        context.user_data["bc_type"] = None

        await send_forward_broadcast(
            context,
            message,
            update
        )

        context.user_data.clear()

        return

    # =====================================================
    # ADD BUTTON
    # =====================================================

    if context.user_data.get(
        "adding_button"
    ):

        step = context.user_data.get(
            "button_step",
            1
        )

        if step != 2:

            await update.message.reply_text(
                "❌ Avval tugma nomini yuboring."
            )

            return

        button_name = context.user_data.get(
            "new_button_name"
        )

        language = context.user_data.get(
            "admin_language_section",
            "uz"
        )

        content_type = None

        content = None

        caption = ""

        if message.photo:

            content_type = "photo"

            content = (
                message.photo[-1].file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.video:

            content_type = "video"

            content = (
                message.video.file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.document:

            content_type = "document"

            content = (
                message.document.file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.audio:

            content_type = "audio"

            content = (
                message.audio.file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.voice:

            content_type = "voice"

            content = (
                message.voice.file_id
            )

            caption = (
                message.caption or ""
            )

        else:

            await update.message.reply_text(
                T[admin_lang][
                    "unsupported_media"
                ]
            )

            return

        data[
            "buttons"
        ][language].append({

            "uid":
                uuid.uuid4().hex[:10],

            "name":
                button_name,

            "type":
                content_type,

            "content":
                content,

            "caption":
                caption,

            "children":
                [],

            "reply_children":
                []

        })

        save_data(data)

        context.user_data.pop(
            "adding_button",
            None
        )

        context.user_data.pop(
            "button_step",
            None
        )

        context.user_data.pop(
            "new_button_name",
            None
        )

        await update.message.reply_text(

            T[admin_lang][
                "button_added"
            ].format(

                language=LANGUAGES[
                    language
                ],

                name=button_name
            ),

            parse_mode="HTML",

            reply_markup=ReplyKeyboardMarkup(
                [
                    ["👑 Admin panel"],
                    ["👥 Foydalanuvchilar"]
                ],
                resize_keyboard=True
            )
        )

        return

    # =====================================================
    # ADD INLINE TO INNER BUTTON
    # =====================================================
    if context.user_data.get("adding_inner_inline"):
        step=context.user_data.get("inner_inline_step",1)
        if step==1:
            if len(text)>50:
                await update.message.reply_text("❌ Inline tugma nomi 50 belgidan oshmasin."); return
            context.user_data["inner_inline_name"]=text
            context.user_data["inner_inline_step"]=2
            await update.message.reply_text("🎨 <b>Inline tugma rangini tanlang:</b>",parse_mode="HTML",reply_markup=style_keyboard("inner_inline_style","cancel_inner_inline"))
            return
        if step==3:
            typ=context.user_data.get("inner_inline_type")
            if typ=="url" and not (text.startswith("https://") or text.startswith("http://") or text.startswith("tg://")):
                await update.message.reply_text("❌ URL noto‘g‘ri."); return
            language=context.user_data.get("admin_language_section","uz")
            buttons=data.get("buttons",{}).get(language,[])
            pi=context.user_data.get("inner_parent_index"); ci=context.user_data.get("inner_child_index")
            if not (isinstance(pi,int) and isinstance(ci,int) and 0<=pi<len(buttons)): return
            children=buttons[pi].get("reply_children",[])
            if not (0<=ci<len(children)): return
            children[ci].setdefault("children",[]).append({"uid":uuid.uuid4().hex[:10],"name":context.user_data.get("inner_inline_name","Inline"),"type":typ,"content":text,"caption":"","style":context.user_data.get("inner_inline_style","default"),"children":[],"reply_children":[]})
            save_data(data)
            for k in ["adding_inner_inline","inner_parent_index","inner_child_index","inner_inline_step","inner_inline_name","inner_inline_style","inner_inline_type"]: context.user_data.pop(k,None)
            await update.message.reply_text("✅ <b>Ichki tugmaga inline tugma qo‘shildi!</b>",parse_mode="HTML",reply_markup=admin_keyboard())
            return

    # =====================================================
    # ADD REPLY CHILD MEDIA (ichki tugma uchun)
    # =====================================================

    if context.user_data.get(
        "adding_reply_child"
    ):

        step = context.user_data.get(
            "reply_child_step",
            1
        )

        if step != 3:

            await update.message.reply_text(
                "❌ Avval ichki tugma nomini va turini tanlang."
            )

            return

        reply_child_type = context.user_data.get(
            "reply_child_type"
        )

        language = context.user_data.get(
            "admin_language_section",
            "uz"
        )

        parent_index = context.user_data.get(
            "reply_child_parent_index"
        )

        child_name = context.user_data.get(
            "new_reply_child_name"
        )

        buttons = data[
            "buttons"
        ].get(
            language,
            []
        )

        if not (
            isinstance(parent_index, int)
            and 0 <= parent_index < len(buttons)
        ):

            context.user_data.clear()

            return

        content_type = None

        content = None

        caption = ""

        if message.photo and reply_child_type == "photo":

            content_type = "photo"

            content = message.photo[-1].file_id

            caption = message.caption or ""

        elif message.video and reply_child_type == "video":

            content_type = "video"

            content = message.video.file_id

            caption = message.caption or ""

        elif message.document and reply_child_type == "document":

            content_type = "document"

            content = message.document.file_id

            caption = message.caption or ""

        elif message.audio and reply_child_type == "audio":

            content_type = "audio"

            content = message.audio.file_id

            caption = message.caption or ""

        elif message.voice and reply_child_type == "voice":

            content_type = "voice"

            content = message.voice.file_id

            caption = message.caption or ""

        else:

            await update.message.reply_text(
                T[admin_lang][
                    "unsupported_media"
                ]
            )

            return

        child = {

            "uid":
                uuid.uuid4().hex[:10],

            "name":
                child_name,

            "type":
                content_type,

            "content":
                content,

            "caption":
                caption,

            "style":
                context.user_data.get("new_reply_child_style", "default"),

            "children":
                [],

            "reply_children":
                []

        }

        if "reply_children" not in buttons[
            parent_index
        ]:

            buttons[
                parent_index
            ][
                "reply_children"
            ] = []

        buttons[
            parent_index
        ][
            "reply_children"
        ].append(
            child
        )

        save_data(data)

        for key in [
            "adding_reply_child",
            "reply_child_step",
            "reply_child_type",
            "reply_child_parent_index",
            "new_reply_child_name",
            "new_inline_name"
        ]:

            context.user_data.pop(key, None)

        await update.message.reply_text(

            T[admin_lang][
                "reply_child_added"
            ].format(
                name=child_name
            ),

            parse_mode="HTML"
        )

        return

    # =====================================================
    # UPDATE BUTTON CONTENT
    # =====================================================

    if context.user_data.get(
        "updating_content"
    ):

        index = context.user_data.get(
            "updating_content_index"
        )

        language = context.user_data.get(
            "admin_language_section",
            "uz"
        )

        buttons = data[
            "buttons"
        ].get(
            language,
            []
        )

        if not (
            isinstance(index, int)
            and 0 <= index < len(buttons)
        ):

            context.user_data.pop(
                "updating_content",
                None
            )

            return

        content_type = None

        content = None

        caption = ""

        if message.photo:

            content_type = "photo"

            content = (
                message.photo[-1].file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.video:

            content_type = "video"

            content = (
                message.video.file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.document:

            content_type = "document"

            content = (
                message.document.file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.audio:

            content_type = "audio"

            content = (
                message.audio.file_id
            )

            caption = (
                message.caption or ""
            )

        elif message.voice:

            content_type = "voice"

            content = (
                message.voice.file_id
            )

            caption = (
                message.caption or ""
            )

        else:

            await update.message.reply_text(
                T[admin_lang][
                    "unsupported_media"
                ]
            )

            return

        buttons[index][
            "type"
        ] = content_type

        buttons[index][
            "content"
        ] = content

        buttons[index][
            "caption"
        ] = caption

        save_data(data)

        context.user_data.pop(
            "updating_content",
            None
        )

        context.user_data.pop(
            "updating_content_index",
            None
        )

        await update.message.reply_text(

            T[admin_lang][
                "content_updated"
            ],

            parse_mode="HTML"
        )

        return


# =========================================================
# BROADCAST
# =========================================================

def get_broadcast_users(language=None):
    if not language or language == "all":
        return data.get("users", [])
    return [u for u in data.get("users", []) if u.get("language") == language]


async def process_broadcast(
    update,
    context,
    media=False
):

    admin_lang = get_admin_language()

    message = update.message

    await message.reply_text(
        T[admin_lang][
            "broadcast_started"
        ]
    )

    sent = 0

    failed = 0

    for user in get_broadcast_users(context.user_data.get("bc_language")):

        try:

            if media:

                if message.photo:

                    await context.bot.send_photo(

                        chat_id=user["id"],

                        photo=message.photo[
                            -1
                        ].file_id,

                        caption=(
                            message.caption
                            or ""
                        )
                    )

                elif message.video:

                    await context.bot.send_video(

                        chat_id=user["id"],

                        video=message.video.file_id,

                        caption=(
                            message.caption
                            or ""
                        )
                    )

                elif message.document:

                    await context.bot.send_document(

                        chat_id=user["id"],

                        document=(
                            message.document.file_id
                        ),

                        caption=(
                            message.caption
                            or ""
                        )
                    )

                elif message.audio:

                    await context.bot.send_audio(

                        chat_id=user["id"],

                        audio=(
                            message.audio.file_id
                        ),

                        caption=(
                            message.caption
                            or ""
                        )
                    )

                elif message.voice:

                    await context.bot.send_voice(

                        chat_id=user["id"],

                        voice=(
                            message.voice.file_id
                        )
                    )

            else:

                await context.bot.send_message(

                    chat_id=user["id"],

                    text=message.text
                )

            sent += 1

        except (
            Forbidden,
            BadRequest
        ):

            failed += 1

        except TelegramError:

            failed += 1

        await asyncio.sleep(
            0.05
        )

    context.user_data.pop(
        "broadcasting",
        None
    )

    await message.reply_text(

        T[admin_lang][
            "broadcast_done"
        ].format(

            sent=sent,

            failed=failed
        ),

        parse_mode="HTML"
    )
    
    
def personalize_text(text, user):
    """$firstname, $username, $id va h.k larni almashtirish"""

    result = text

    result = result.replace(
        "$firstname",
        user.get("first_name", "") or ""
    )

    result = result.replace(
        "$lastname",
        user.get("last_name", "") or ""
    )

    result = result.replace(
        "$username",
        user.get("username", "") or ""
    )

    result = result.replace(
        "$id",
        str(user.get("id", ""))
    )

    return result


# =========================================================
# SEND BROADCAST WITH BUTTONS
# =========================================================

async def send_broadcast_with_buttons(
    context,
    text,
    inline_keyboard
):

    sent = 0

    failed = 0

    users = get_broadcast_users(context.user_data.get("bc_language"))
    total = len(users)

    for user in users:

        try:

            await context.bot.send_message(

                chat_id=user["id"],

                text=text,

                parse_mode="HTML",

                reply_markup=inline_keyboard
            )

            sent += 1

        except (Forbidden, BadRequest):

            failed += 1

        except TelegramError:

            failed += 1

        await asyncio.sleep(0.05)

    return sent, failed


# =========================================================
# SEND PERSONALIZED BROADCAST
# =========================================================

async def send_personalized_broadcast(
    context,
    text,
    update
):

    admin_lang = get_admin_language()

    sent = 0

    failed = 0

    users = get_broadcast_users(context.user_data.get("bc_language"))
    total = len(users)

    # Progress xabar
    progress_msg = await update.message.reply_text(

        T[admin_lang]["broadcast_progress"].format(
            sent=0,
            failed=0,
            total=total,
            remaining=total
        ),

        parse_mode="HTML"
    )

    last_update = time.time()

    for user in users:

        try:

            personalized = personalize_text(text, user)

            await context.bot.send_message(

                chat_id=user["id"],

                text=personalized,

                parse_mode="HTML"
            )

            sent += 1

        except (Forbidden, BadRequest):

            failed += 1

        except TelegramError:

            failed += 1

        # Har 1 sekundda progress yangilash
        if time.time() - last_update > 1.5:

            try:

                await progress_msg.edit_text(

                    T[admin_lang]["broadcast_progress"].format(
                        sent=sent,
                        failed=failed,
                        total=total,
                        remaining=total - sent - failed
                    ),

                    parse_mode="HTML"
                )

            except BadRequest:

                pass

            last_update = time.time()

        await asyncio.sleep(0.05)

    # Yakuniy xabar
    try:

        await progress_msg.edit_text(

            T[admin_lang]["broadcast_done"].format(
                sent=sent,
                failed=failed
            ),

            parse_mode="HTML"
        )

    except BadRequest:

        pass


# =========================================================
# SEND FORWARD BROADCAST
# =========================================================

async def send_forward_broadcast(
    context,
    message,
    update
):

    admin_lang = get_admin_language()

    from_chat_id = message.chat_id

    message_id = message.message_id

    sent = 0

    failed = 0

    users = get_broadcast_users(context.user_data.get("bc_language"))
    total = len(users)

    progress_msg = await update.message.reply_text(

        T[admin_lang]["broadcast_progress"].format(
            sent=0,
            failed=0,
            total=total,
            remaining=total
        ),

        parse_mode="HTML"
    )

    last_update = time.time()

    for user in users:

        try:

            await context.bot.forward_message(

                chat_id=user["id"],

                from_chat_id=from_chat_id,

                message_id=message_id
            )

            sent += 1

        except (Forbidden, BadRequest):

            failed += 1

        except TelegramError:

            failed += 1

        if time.time() - last_update > 1.5:

            try:

                await progress_msg.edit_text(

                    T[admin_lang]["broadcast_progress"].format(
                        sent=sent,
                        failed=failed,
                        total=total,
                        remaining=total - sent - failed
                    ),

                    parse_mode="HTML"
                )

            except BadRequest:

                pass

            last_update = time.time()

        await asyncio.sleep(0.05)

    try:

        await progress_msg.edit_text(

            T[admin_lang]["broadcast_done"].format(
                sent=sent,
                failed=failed
            ),

            parse_mode="HTML"
        )

    except BadRequest:

        pass


# =========================================================
# TEXT HANDLER
# =========================================================

async def text_handler(
    update,
    context
):

    user = update.effective_user

    text = update.message.text

    if is_rate_limited(
        user.id
    ):

        return

    admin_lang = get_admin_language()

    if bot_maintenance_enabled() and not is_admin(user.id):
        await update.message.reply_text(maintenance_text(get_user_language(user.id) or "uz"), parse_mode="HTML")
        return

    try:

        # =================================================
        # ADMIN
        # =================================================

        if is_admin(user.id):

            # =============================================
            # ADMIN PANEL
            # =============================================

            if text == "👑 Admin panel":

                await admin_panel(
                    update,
                    context
                )

                return

            # =============================================
            # CODE ORQALI TUGMA
            # =============================================
            if context.user_data.get("adding_button_by_code"):
                context.user_data.pop("adding_button_by_code", None)
                try:
                    try: obj = json.loads(text)
                    except Exception: obj = ast.literal_eval(text)
                    if not isinstance(obj, dict): raise ValueError
                    language=str(obj.get("language", "")).lower().strip(); name=str(obj.get("name", "")).strip(); btype=str(obj.get("type", "text")).lower().strip()
                    content=obj.get("content", ""); caption=str(obj.get("caption", "") or ""); style=str(obj.get("style", "default")).lower().strip()
                    allowed={"text","url","photo","video","document","audio","voice"}
                    if language not in LANGUAGES or not name or len(name)>64 or btype not in allowed or content in (None, ""): raise ValueError
                    if btype == "url" and not str(content).startswith(("http://","https://","tg://")): raise ValueError
                    if style not in BUTTON_STYLES: style="default"
                    btn={"uid":uuid.uuid4().hex[:10],"name":name,"type":btype,"content":str(content),"caption":caption,"style":style,"children":obj.get("children",[]) if isinstance(obj.get("children",[]),list) else [],"reply_children":obj.get("reply_children",[]) if isinstance(obj.get("reply_children",[]),list) else []}
                    data.setdefault("buttons",{}).setdefault(language,[]).append(btn); normalize_buttons(data["buttons"][language]); save_data(data); add_admin_log("BUTTON_ADD", user.id, f"{language}: {name}")
                    await update.message.reply_text(T[admin_lang]["code_button_added"], parse_mode="HTML", reply_markup=settings_keyboard(admin_lang))
                except Exception:
                    await update.message.reply_text(T[admin_lang]["code_button_error"], parse_mode="HTML", reply_markup=settings_keyboard(admin_lang))
                return

            # =============================================
            # BOT HOLATI MATNI
            # =============================================
            if context.user_data.get("editing_maintenance_text"):
                language=context.user_data.pop("editing_maintenance_text")
                data.setdefault("bot_settings",{}).setdefault("maintenance_text",{})[language]=text
                save_data(data); add_admin_log("MAINTENANCE_TEXT", user.id, language)
                await update.message.reply_text("✅ <b>Bot holati matni saqlandi!</b>", parse_mode="HTML", reply_markup=settings_keyboard(admin_lang))
                return

            # =============================================
            # REQUIRED SUBSCRIPTION TEXT EDIT
            # =============================================
            if context.user_data.get("editing_subscription_text"):
                language = context.user_data.pop("editing_subscription_text")
                data.setdefault("subscription_settings", {}).setdefault("text", {})[language] = text
                save_data(data)
                add_admin_log("SUBSCRIPTION_TEXT", user.id, language)
                await update.message.reply_text(
                    T[admin_lang]["subscription_text_saved"],
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [admin_style_button(T[admin_lang]["channel_settings"], "channel_settings", "default")],
                        [admin_style_button(T[admin_lang]["admin_back"], "admin_back", "default")]
                    ])
                )
                return

            # =============================================
            # START MESSAGE EDIT
            # =============================================
            if context.user_data.get("editing_start_message"):
                language = context.user_data.pop("editing_start_message")
                data.setdefault("start_messages", {})[language] = text
                save_data(data)
                await update.message.reply_text(
                    "✅ <b>Start xabari saqlandi!</b>",
                    parse_mode="HTML",
                    reply_markup=admin_keyboard()
                )
                return

            # =============================================
            # EXTRA CONTENT FOR MAIN/INNER BUTTON
            # =============================================
            if context.user_data.get("adding_extra_content_uid"):
                uid = context.user_data.pop("adding_extra_content_uid")
                language = context.user_data.get("admin_language_section", "uz")
                node = find_any_button_node(data.get("buttons", {}).get(language, []), uid)
                if not node:
                    await update.message.reply_text("❌ Tugma topilmadi.")
                    return
                append_node_content(node, "text", text, "")
                save_data(data)
                await update.message.reply_text("✅ <b>Qo‘shimcha xabar qo‘shildi!</b>", parse_mode="HTML", reply_markup=admin_keyboard())
                return

            # =============================================
            # MANUAL LAYOUT INPUT
            # =============================================

            if context.user_data.get("manual_layout_target"):
                values = parse_manual_layout(text)
                if not values:
                    await update.message.reply_text(
                        "❌ Noto'g'ri format. Masalan: <code>1,2,2,1</code>",
                        parse_mode="HTML"
                    )
                    return
                target = context.user_data.pop("manual_layout_target")
                if target[0] == "main":
                    _, language = target
                    layouts = data.setdefault("layouts", {}).setdefault(language, {})
                    layouts["main"] = "manual"
                    layouts["main_rows"] = values
                else:
                    field, language, parent_index = target
                    buttons = data.get("buttons", {}).get(language, [])
                    if 0 <= parent_index < len(buttons):
                        buttons[parent_index][field + "_layout"] = "manual"
                        buttons[parent_index][field + "_rows"] = values
                save_data(data)
                await update.message.reply_text("✅ Qo'lda joylashuv saqlandi.")
                return

            # =============================================
            # BOTNI ISHLATISH
            # =============================================

            if text == "👥 Foydalanuvchilar":

                context.user_data.clear()

                language = get_user_language(
                    user.id
                )

                if not language:

                    await update.message.reply_text(

                        T["uz"][
                            "choose_language"
                        ],

                        parse_mode="HTML",

                        reply_markup=language_keyboard()
                    )

                    return

                blocked = await subscription_message(

                    update,

                    context,

                    language
                )

                if blocked:

                    return

                await update.message.reply_text(

                    T[language][
                        "bot_ready"
                    ],

                    parse_mode="HTML",

                    reply_markup=user_keyboard(
                        language
                    )
                )

                return

            # =============================================
            # BROADCAST
            # =============================================

            bc_type = context.user_data.get("bc_type")

            if bc_type:

                # =========================================
                # FORWARD
                # =========================================

                if bc_type == "forward":
                    context.user_data["bc_type"] = None
                    await send_forward_broadcast(
                        context,
                        update.message,
                        update
                    )
                    context.user_data.clear()
                    return

                # =========================================
                # SIMPLE / PERSONALIZED
                # =========================================

                if bc_type in ["simple", "personalized"]:

                    if not text.strip():
                        await update.message.reply_text(
                            T[admin_lang]["broadcast_empty_text"]
                        )
                        return

                    context.user_data["bc_type"] = None

                    if bc_type == "simple":
                        await process_broadcast(
                            update,
                            context,
                            media=False
                        )
                    else:
                        await send_personalized_broadcast(
                            context,
                            text,
                            update
                        )
                        context.user_data.clear()

                    return

                # =========================================
                # SINGLE USER
                # =========================================

                if bc_type == "single":

                    if "|" not in text:

                        await update.message.reply_text(
                            T[admin_lang]["broadcast_single_invalid"],
                            parse_mode="HTML"
                        )

                        return

                    parts = text.split("|", 1)

                    try:

                        target_id = int(parts[0].strip())

                    except ValueError:

                        await update.message.reply_text(
                            T[admin_lang]["broadcast_single_invalid"],
                            parse_mode="HTML"
                        )

                        return

                    msg_text = parts[1].strip()

                    try:

                        await context.bot.send_message(

                            chat_id=target_id,

                            text=msg_text,

                            parse_mode="HTML"
                        )

                        await update.message.reply_text(

                            T[admin_lang]["broadcast_single_sent"].format(
                                user_id=target_id
                            ),

                            parse_mode="HTML"
                        )

                    except (Forbidden, BadRequest, TelegramError):

                        await update.message.reply_text(

                            T[admin_lang]["broadcast_single_failed"],

                            parse_mode="HTML"
                        )

                    context.user_data.clear()

                    return

                # =========================================
                # WITH BUTTON - STEP: TEXT
                # =========================================

                if bc_type == "with_button":

                    step = context.user_data.get("bc_step")

                    # STEP 1: TEXT
                    if step == "text":

                        if not text.strip():

                            await update.message.reply_text(
                                T[admin_lang]["broadcast_empty_text"]
                            )

                            return

                        context.user_data["bc_text"] = text

                        context.user_data["bc_step"] = "button_name"

                        await update.message.reply_text(

                            T[admin_lang]["broadcast_button_name_step"],

                            parse_mode="HTML",

                            reply_markup=InlineKeyboardMarkup([

                                [
                                    InlineKeyboardButton(
                                        T[admin_lang]["broadcast_cancel"],
                                        callback_data="bc_cancel"
                                    )
                                ]

                            ])
                        )

                        return

                    # STEP 2: BUTTON NAME
                    if step == "button_name":

                        if len(text) > 50:

                            await update.message.reply_text(
                                T[admin_lang]["name_too_long"]
                            )

                            return

                        context.user_data["bc_temp_button_name"] = text

                        context.user_data["bc_step"] = "button_url"

                        await update.message.reply_text(

                            T[admin_lang]["broadcast_button_url_step"],

                            parse_mode="HTML",

                            reply_markup=InlineKeyboardMarkup([

                                [
                                    InlineKeyboardButton(
                                        T[admin_lang]["broadcast_cancel"],
                                        callback_data="bc_cancel"
                                    )
                                ]

                            ])
                        )

                        return

                    # STEP 3: BUTTON URL
                    if step == "button_url":

                        if not (
                            text.startswith("https://")
                            or text.startswith("http://")
                            or text.startswith("tg://")
                        ):

                            await update.message.reply_text(
                                T[admin_lang]["broadcast_button_url_error"]
                            )

                            return

                        btn_name = context.user_data.get(
                            "bc_temp_button_name"
                        )

                        buttons = context.user_data.get(
                            "bc_buttons",
                            []
                        )

                        buttons.append({

                            "name": btn_name,

                            "url": text

                        })

                        context.user_data["bc_buttons"] = buttons

                        context.user_data["bc_step"] = None

                        # Tugmalar ro'yxatini ko'rsatish
                        text_preview = (
                            T[admin_lang]["broadcast_button_added"]
                            + "\n\n"
                        )

                        for i, b in enumerate(buttons, 1):

                            text_preview += (
                                f"{i}. 🔘 {b['name']}\n"
                                f"   🔗 {b['url']}\n"
                            )

                        await update.message.reply_text(

                            text_preview,

                            parse_mode="HTML",

                            reply_markup=InlineKeyboardMarkup([

                                [
                                    InlineKeyboardButton(
                                        T[admin_lang]["broadcast_add_more_button"],
                                        callback_data="bc_add_more_button"
                                    )
                                ],

                                [
                                    InlineKeyboardButton(
                                        T[admin_lang]["broadcast_start_send"],
                                        callback_data="bc_start_send"
                                    )
                                ],

                                [
                                    InlineKeyboardButton(
                                        T[admin_lang]["broadcast_cancel"],
                                        callback_data="bc_cancel"
                                    )
                                ]

                            ])
                        )

                        return

            # =============================================
            # RENAME BUTTON
            # =============================================

            if "renaming_button" in context.user_data:

                index = context.user_data[
                    "renaming_button"
                ]

                language = context.user_data.get(
                    "admin_language_section",
                    "uz"
                )

                buttons = data[
                    "buttons"
                ].get(
                    language,
                    []
                )

                if not (
                    0 <= index < len(buttons)
                ):

                    context.user_data.pop(
                        "renaming_button",
                        None
                    )

                    return

                if len(text) > 50:

                    await update.message.reply_text(
                        T[admin_lang][
                            "name_too_long"
                        ]
                    )

                    return

                old_name = buttons[
                    index
                ]["name"]

                buttons[index][
                    "name"
                ] = text

                save_data(data)

                context.user_data.pop(
                    "renaming_button",
                    None
                )

                await update.message.reply_text(

                    T[admin_lang][
                        "button_renamed"
                    ].format(

                        old=old_name,

                        new=text
                    ),

                    parse_mode="HTML"
                )

                return

            # =================================================
            # YANGI ICHKI REPLY TUGMA
            # =================================================

            if context.user_data.get(
                "adding_reply_child"
            ):

                step = context.user_data.get(
                    "reply_child_step",
                    1
                )

                language = context.user_data.get(
                    "admin_language_section",
                    "uz"
                )

                parent_index = context.user_data.get(
                    "reply_child_parent_index"
                )

                buttons = data[
                    "buttons"
                ].get(
                    language,
                    []
                )

                if not (
                    isinstance(
                        parent_index,
                        int
                    )
                    and
                    0 <= parent_index < len(buttons)
                ):

                    context.user_data.clear()

                    return

                # =========================================
                # 1. NOM
                # =========================================

                if step == 1:

                    if len(text) > 50:

                        await update.message.reply_text(

                            T[admin_lang][
                                "reply_child_name_too_long"
                            ]

                        )

                        return

                    context.user_data[
                        "new_reply_child_name"
                    ] = text

                    context.user_data[
                        "reply_child_step"
                    ] = 1.5

                    await update.message.reply_text(
                        "🎨 <b>Ichki tugma rangini tanlang:</b>",
                        parse_mode="HTML",
                        reply_markup=style_keyboard(
                            "reply_style",
                            f"cancel_reply_child_{parent_index}"
                        )
                    )

                    return

                    keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            T[admin_lang]["type_text"],
            callback_data="reply_child_type_text"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["type_url"],
            callback_data="reply_child_type_url"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["type_photo"],
            callback_data="reply_child_type_photo"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["type_video"],
            callback_data="reply_child_type_video"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["type_document"],
            callback_data="reply_child_type_document"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["type_audio"],
            callback_data="reply_child_type_audio"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["type_voice"],
            callback_data="reply_child_type_voice"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["type_inline"],
            callback_data="reply_child_type_inline"
        )
    ],
    [
        InlineKeyboardButton(
            "🎯 Reaksiya",
            callback_data="reply_child_type_reaction"
        )
    ],
    [
        InlineKeyboardButton(
            T[admin_lang]["no_cancel"],
            callback_data=f"cancel_reply_child_{parent_index}"
        )
    ]
])

                    await update.message.reply_text(

                        T[admin_lang][
                            "reply_child_type"
                        ],

                        parse_mode="HTML",

                        reply_markup=keyboard
                    )

                    return

                # =========================================
                # 3. CONTENT (text yoki url)
                # =========================================

                if step == 3:

                    child_type = context.user_data.get(
                        "reply_child_type"
                    )

                    child_name = context.user_data.get(
                        "new_reply_child_name"
                    )

                    if child_type == "url":

                        if not (
                            text.startswith(
                                "https://"
                            )
                            or
                            text.startswith(
                                "http://"
                            )
                            or
                            text.startswith(
                                "tg://"
                            )
                        ):

                            await update.message.reply_text(

                                T[admin_lang][
                                    "reply_child_url_error"
                                ]

                            )

                            return

                    child = {

                        "uid":
                            uuid.uuid4().hex[:10],

                        "name":
                            child_name,

                        "type":
                            child_type,

                        "content":
                            text,

                        "caption":
                            "",

                        "style":
                            context.user_data.get("new_reply_child_style", "default"),

                        "children":
                            [],

                        "reply_children":
                            []

                    }

                    if (
                        "reply_children"
                        not in buttons[parent_index]
                    ):

                        buttons[
                            parent_index
                        ][
                            "reply_children"
                        ] = []

                    buttons[
                        parent_index
                    ][
                        "reply_children"
                    ].append(
                        child
                    )

                    save_data(data)

                    context.user_data.pop(
                        "adding_reply_child",
                        None
                    )

                    context.user_data.pop(
                        "reply_child_step",
                        None
                    )

                    context.user_data.pop(
                        "reply_child_type",
                        None
                    )

                    context.user_data.pop(
                        "reply_child_parent_index",
                        None
                    )

                    context.user_data.pop(
                        "new_reply_child_name",
                        None
                    )

                    await update.message.reply_text(

                        T[admin_lang][
                            "reply_child_added"
                        ].format(
                            name=child_name
                        ),

                        parse_mode="HTML"
                    )

                    return

                # =========================================
                # 4. INLINE NAME
                # =========================================

                if step == 4:

                    if len(text) > 50:

                        await update.message.reply_text(

                            T[admin_lang][
                                "reply_child_name_too_long"
                            ]

                        )

                        return

                    context.user_data[
                        "new_inline_name"
                    ] = text

                    context.user_data[
                        "reply_child_step"
                    ] = 4.5

                    await update.message.reply_text(
                        "🎨 <b>Ichki inline tugma rangini tanlang:</b>",
                        parse_mode="HTML",
                        reply_markup=style_keyboard(
                            "reply_inline_style",
                            f"cancel_reply_child_{parent_index}"
                        )
                    )

                    return

                    await update.message.reply_text(

                        T[admin_lang][
                            "reply_child_inline_url_prompt"
                        ],

                        parse_mode="HTML",

                        reply_markup=InlineKeyboardMarkup([

                            [
                                InlineKeyboardButton(
                                    T[admin_lang]["no_cancel"],
                                    callback_data=(
                                        f"cancel_reply_child_{parent_index}"
                                    )
                                )
                            ]

                        ])
                    )

                    return

                # =========================================
                # 5. INLINE URL
                # =========================================

                if step == 5:

                    child_name = context.user_data.get(
                        "new_reply_child_name"
                    )

                    inline_name = context.user_data.get(
                        "new_inline_name"
                    )

                    if not (
                        text.startswith(
                            "https://"
                        )
                        or
                        text.startswith(
                            "http://"
                        )
                        or
                        text.startswith(
                            "tg://"
                        )
                    ):

                        await update.message.reply_text(

                            T[admin_lang][
                                "reply_child_url_error"
                            ]

                        )

                        return

                    inline_child = {

                        "uid":
                            uuid.uuid4().hex[:10],

                        "name":
                            inline_name,

                        "type":
                            "url",

                        "content":
                            text,

                        "caption":
                            "",

                        "style":
                            context.user_data.get("new_reply_inline_style", "default"),

                        "children":
                            [],

                        "reply_children":
                            []

                    }

                    child = {

                        "uid":
                            uuid.uuid4().hex[:10],

                        "name":
                            child_name,

                        "type":
                            "text",

                        "content":
                            "",

                        "caption":
                            "",

                        "children":
                            [inline_child],

                        "reply_children":
                            []

                    }

                    if (
                        "reply_children"
                        not in buttons[parent_index]
                    ):

                        buttons[
                            parent_index
                        ][
                            "reply_children"
                        ] = []

                    buttons[
                        parent_index
                    ][
                        "reply_children"
                    ].append(
                        child
                    )

                    save_data(data)

                    for key in [
                        "adding_reply_child",
                        "reply_child_step",
                        "reply_child_type",
                        "reply_child_parent_index",
                        "new_reply_child_name",
                        "new_inline_name",
                        "new_reply_inline_style"
                    ]:

                        context.user_data.pop(key, None)

                    await update.message.reply_text(

                        T[admin_lang][
                            "reply_child_added"
                        ].format(
                            name=child_name
                        ),

                        parse_mode="HTML"
                    )

                    return

            # =================================================
            # OLD INLINE TUGMA
            # =================================================

            if context.user_data.get(
                "adding_child"
            ):

                step = context.user_data.get(
                    "child_step",
                    1
                )

                language = context.user_data.get(
                    "admin_language_section",
                    "uz"
                )

                parent_index = context.user_data.get(
                    "child_parent_index"
                )

                buttons = data[
                    "buttons"
                ].get(
                    language,
                    []
                )

                if not (
                    isinstance(
                        parent_index,
                        int
                    )
                    and
                    0 <= parent_index < len(buttons)
                ):

                    context.user_data.clear()

                    return

                # =========================================
                # 1. NOM
                # =========================================

                if step == 1:

                    if len(text) > 50:

                        await update.message.reply_text(

                            T[admin_lang][
                                "inline_name_too_long"
                            ]

                        )

                        return

                    context.user_data[
                        "new_child_name"
                    ] = text

                    context.user_data[
                        "child_step"
                    ] = 2

                    keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "🔗 URL",
            callback_data="child_type_url"
        )
    ],
    [
        InlineKeyboardButton(
            "📝 Matn",
            callback_data="child_type_text"
        )
    ],
    [
        InlineKeyboardButton(
            "🎯 Reaksiya",
            callback_data="child_type_reaction"
        )
    ]
])

                    await update.message.reply_text(

                        T[admin_lang][
                            "inline_type"
                        ],

                        parse_mode="HTML",

                        reply_markup=keyboard
                    )

                    return

                # =========================================
                # 3. URL / TEXT
                # =========================================

                if step == 3:

                    child_type = context.user_data.get(
                        "child_type"
                    )

                    child_name = context.user_data.get(
                        "new_child_name"
                    )

                    if child_type == "url":

                        if not (
                            text.startswith(
                                "https://"
                            )
                            or
                            text.startswith(
                                "http://"
                            )
                            or
                            text.startswith(
                                "tg://"
                            )
                        ):

                            await update.message.reply_text(

                                T[admin_lang][
                                    "inline_url_error"
                                ]

                            )

                            return

                    child = {

                        "uid":
                            uuid.uuid4().hex[:10],

                        "name":
                            child_name,

                        "type":
                            child_type,

                        "content":
                            text,

                        "caption":
                            "",

                        "style":
                            context.user_data.get("new_child_style", "default"),

                        "children":
                            [],

                        "reply_children":
                            []

                    }

                    if (
                        "children"
                        not in buttons[parent_index]
                    ):

                        buttons[
                            parent_index
                        ][
                            "children"
                        ] = []

                    buttons[
                        parent_index
                    ][
                        "children"
                    ].append(
                        child
                    )

                    save_data(data)

                    context.user_data.pop(
                        "adding_child",
                        None
                    )

                    context.user_data.pop(
                        "child_step",
                        None
                    )

                    context.user_data.pop(
                        "child_type",
                        None
                    )

                    context.user_data.pop(
                        "child_parent_index",
                        None
                    )

                    context.user_data.pop(
                        "new_child_name",
                        None
                    )

                    await update.message.reply_text(

                        T[admin_lang][
                            "inline_added"
                        ].format(
                            name=child_name
                        ),

                        parse_mode="HTML"
                    )

                    return

            # =================================================
            # ADD ADMIN   ← FAQAT BITTA TO'G'RI BLOK
            # =================================================

            if context.user_data.get("adding_admin"):

                text_clean = text.strip()

                if not text_clean.isdigit():

                    await update.message.reply_text(
                        T[admin_lang]["admin_invalid_id"]
                    )

                    return

                new_admin_id = int(text_clean)

                admins = data.get("admins", [ADMIN_ID])

                if new_admin_id in admins:

                    await update.message.reply_text(
                        T[admin_lang]["admin_already"]
                    )

                    context.user_data.pop("adding_admin", None)

                    return

                admins.append(new_admin_id)

                data["admins"] = admins

                save_data(data)

                context.user_data.pop("adding_admin", None)

                await update.message.reply_text(

                    T[admin_lang]["admin_added"].format(
                        user_id=new_admin_id
                    ),

                    parse_mode="HTML",

                    reply_markup=InlineKeyboardMarkup([

                        [
                            InlineKeyboardButton(
                                T[admin_lang]["admins"],
                                callback_data="admin_manage"
                            )
                        ],

                        [
                            InlineKeyboardButton(
                                T[admin_lang]["admin_back"],
                                callback_data="admin_back"
                            )
                        ]

                    ])
                )

                return

            # =================================================
            # ADD CHANNEL
            # =================================================

            if context.user_data.get("adding_channel"):
                channel_type = context.user_data.get("adding_channel_type", "public")
                try:
                    parts = [x.strip() for x in text.split("|")]

                    if channel_type == "public":
                        if len(parts) != 2:
                            raise ValueError
                        username, name = parts
                        if not username.startswith("@"):
                            username = "@" + username
                        if not name:
                            raise ValueError

                        chat = await context.bot.get_chat(username)
                        chat_id = chat.id
                        if getattr(chat, "type", "") != "channel":
                            raise ValueError

                        url = "https://t.me/" + username.lstrip("@")
                        invite_link = ""
                    else:
                        if len(parts) != 3:
                            raise ValueError
                        chat_id = int(parts[0])
                        name = parts[1]
                        invite_link = parts[2]
                        if not name or not (invite_link.startswith("https://t.me/") or invite_link.startswith("http://t.me/")):
                            raise ValueError
                        chat = await context.bot.get_chat(chat_id)
                        if getattr(chat, "type", "") != "channel":
                            raise ValueError
                        url = invite_link
                        username = ""

                    bot_member = await context.bot.get_chat_member(chat_id=chat_id, user_id=context.bot.id)
                    if bot_member.status not in ["administrator", "creator"]:
                        await update.message.reply_text(T[admin_lang]["bot_not_admin"])
                        return

                    for existing in data.get("channels", []):
                        if existing.get("chat_id") == chat_id:
                            await update.message.reply_text(T[admin_lang]["channel_already"])
                            context.user_data.pop("adding_channel", None)
                            context.user_data.pop("adding_channel_type", None)
                            return

                    item = {
                        "chat_id": chat_id,
                        "username": username,
                        "name": name,
                        "url": url,
                        "type": channel_type,
                        "invite_link": invite_link
                    }
                    data.setdefault("channels", []).append(item)
                    save_data(data)

                    context.user_data.pop("adding_channel", None)
                    context.user_data.pop("adding_channel_type", None)

                    if channel_type == "private":
                        response = T[admin_lang]["private_channel_added"].format(name=name, url=invite_link)
                    else:
                        response = T[admin_lang]["channel_added"].format(name=name, url=url)

                    await update.message.reply_text(response, parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup([[admin_style_button(T[admin_lang]["channels"], "channel_list", "primary")]]))

                except (ValueError, TypeError, TelegramError) as e:
                    logger.error(f"Channel add error: {e}")
                    await update.message.reply_text(
                        T[admin_lang]["private_channel_error"] if channel_type == "private" else T[admin_lang]["channel_error"],
                        parse_mode="HTML"
                    )
                return

            # =================================================
            # ADD MAIN BUTTON
            # =================================================

            if context.user_data.get(
                "adding_button"
            ):

                step = context.user_data.get(
                    "button_step",
                    1
                )

                # =============================================
                # 1. NAME
                # =============================================

                if step == 1:

                    if len(text) > 50:

                        await update.message.reply_text(

                            T[admin_lang][
                                "name_too_long"
                            ]
                        )

                        return

                    context.user_data[
                        "new_button_name"
                    ] = text

                    context.user_data[
                        "button_step"
                    ] = 1.5

                    await update.message.reply_text(
                        "🎨 <b>Asosiy tugma rangini tanlang:</b>",
                        parse_mode="HTML",
                        reply_markup=style_keyboard(
                            "main_style",
                            "cancel_add_button"
                        )
                    )

                    return

                # =============================================
                # 2. TEXT
                # =============================================

                if step == 2:

                    language = context.user_data.get(
                        "admin_language_section",
                        "uz"
                    )

                    button_name = context.user_data.get(
                        "new_button_name"
                    )

                    data[
                        "buttons"
                    ][language].append({

                        "uid":
                            uuid.uuid4().hex[:10],

                        "name":
                            button_name,

                        "type":
                            "text",

                        "content":
                            text,

                        "caption":
                            "",

                        "style":
                            context.user_data.get("new_button_style", "default"),

                        "children":
                            [],

                        "reply_children":
                            []

                    })

                    save_data(data)

                    context.user_data.pop(
                        "adding_button",
                        None
                    )

                    context.user_data.pop(
                        "button_step",
                        None
                    )

                    context.user_data.pop(
                        "new_button_name",
                        None
                    )

                    await update.message.reply_text(

                        T[admin_lang][
                            "button_added"
                        ].format(

                            language=LANGUAGES[
                                language
                            ],

                            name=button_name

                        ),

                        parse_mode="HTML",

                        reply_markup=ReplyKeyboardMarkup(
                            [
                                ["👑 Admin panel"],
                                ["👥 Foydalanuvchilar"]
                            ],
                            resize_keyboard=True
                        )
                    )

                    return

        # =================================================
        # USER
        # =================================================

        language = get_user_language(
            user.id
        )

        if not language:

            await update.message.reply_text(

                T["uz"][
                    "choose_language"
                ],

                parse_mode="HTML",

                reply_markup=language_keyboard()
            )

            return

        # =================================================
        # ORQAGA
        # =================================================

        if text == "↩️ Orqaga":

            current_uid = context.user_data.get(
                "current_parent_uid"
            )

            if not current_uid:

                await update.message.reply_text(

                    T[language][
                        "main_menu"
                    ],

                    parse_mode="HTML",

                    reply_markup=user_keyboard(
                        language
                    )
                )

                return

            parent = find_parent_reply_button(

                data[
                    "buttons"
                ].get(
                    language,
                    []
                ),

                current_uid
            )

            if parent:

                context.user_data[
                    "current_parent_uid"
                ] = parent.get(
                    "uid"
                )

                await update.message.reply_text(

                    T[language]["select_section"],

                    parse_mode="HTML",

                    reply_markup=user_keyboard(

                        language,

                        parent.get(
                            "reply_children",
                            []
                        ),

                        show_back=True
                    )
                )

            else:

                context.user_data.pop(
                    "current_parent_uid",
                    None
                )

                await update.message.reply_text(

                    T[language][
                        "main_menu"
                    ],

                    parse_mode="HTML",

                    reply_markup=user_keyboard(
                        language
                    )
                )

            return

        # =================================================
        # LANGUAGE CHANGE
        # =================================================

        if text == T[language][
            "change_language"
        ]:

            context.user_data.pop(
                "current_parent_uid",
                None
            )

            await update.message.reply_text(

                T[language][
                    "choose_language"
                ],

                parse_mode="HTML",

                reply_markup=language_keyboard()
            )

            return

        # =================================================
        # SUBSCRIPTION
        # =================================================

        blocked = await subscription_message(

            update,

            context,

            language
        )

        if blocked:

            return

        # =================================================
        # REPLY INTERNAL BUTTONS
        # =================================================

        current_uid = context.user_data.get(
            "current_parent_uid"
        )

        if current_uid:

            current_button = find_reply_button_by_uid(

                data[
                    "buttons"
                ].get(
                    language,
                    []
                ),

                current_uid
            )

            if current_button:

                for child in current_button.get(
                    "reply_children",
                    []
                ):

                    if text == child[
                        "name"
                    ]:

                        nested = child.get(
                            "reply_children",
                            []
                        )

                        if nested:

                            context.user_data[
                                "current_parent_uid"
                            ] = child[
                                "uid"
                            ]

                            await update.message.reply_text(

                                T[language]["select_section"],

                                parse_mode="HTML",

                                reply_markup=user_keyboard(

                                    language,

                                    nested,

                                    show_back=True
                                )
                            )

                        else:

                            # Ichki tugmaning o'zi reaksiya bo'lsa,
                            # reply keyboard orqali ham hisoblaymiz.
                            if child.get("type") == "reaction":

                                reaction_uid = child.get(
                                    "reaction_uid",
                                    child.get("uid", "")
                                )
                                reaction_data = data.get(
                                    "reactions", {}
                                ).get(reaction_uid)

                                if not reaction_data:
                                    reaction_data = {
                                        "users": [],
                                        "count": 0,
                                        "sticker": child.get("content", ""),
                                        "name": child.get("name", "Reaksiya")
                                    }
                                    data.setdefault("reactions", {})[reaction_uid] = reaction_data
                                    save_data(data)

                                raw_users = reaction_data.get("users", [])
                                users_list = []
                                for uid in raw_users:
                                    try:
                                        uid = int(uid)
                                    except (TypeError, ValueError):
                                        continue
                                    if uid not in users_list:
                                        users_list.append(uid)

                                if user.id in users_list:
                                    users_list.remove(user.id)
                                    status_text = "❌ Reaksiya bekor qilindi."
                                else:
                                    users_list.append(user.id)
                                    status_text = "❤️ Reaksiya qoldirdingiz, rahmat!"

                                reaction_data["users"] = users_list
                                reaction_data["count"] = len(users_list)
                                data.setdefault("reactions", {})[reaction_uid] = reaction_data
                                save_data(data)

                                if reaction_data.get("sticker"):
                                    try:
                                        await update.message.reply_sticker(
                                            sticker=reaction_data["sticker"]
                                        )
                                    except Exception:
                                        pass

                                # Yangilangan son bilan ichki menyuni qayta chiqaramiz.
                                await update.message.reply_text(
                                    f"{status_text}\n👥 Jami: {reaction_data['count']}",
                                    reply_markup=user_keyboard(
                                        language,
                                        current_button.get("reply_children", []),
                                        show_back=True
                                    )
                                )

                            else:

                                await send_reply_child_content(

                                    update.message,

                                    child,

                                    language
                                )

                        return

        # =================================================
        # MAIN BUTTON
        # =================================================

        for button in data[
            "buttons"
        ].get(
            language,
            []
        ):

            if text == button[
                "name"
            ]:

                # Asosiy tugmaning kontenti ichki tugmalar bo'lsa ham
                # o'zgarmaydi. Ichki tugmalar alohida keyboard bo'lib
                # chiqadi; asosiy xabar "Bo'limni tanlang" bilan
                # almashtirilmaydi.
                if button.get("reply_children"):

                    context.user_data[
                        "current_parent_uid"
                    ] = button[
                        "uid"
                    ]

                await send_button_content(

                    update.message,

                    button,

                    language

                )

                return

        # =================================================
        # MAIN MENU
        # =================================================

        if text == T[language][
            "main_menu"
        ]:

            context.user_data.pop(
                "current_parent_uid",
                None
            )

            await update.message.reply_text(

                T[language][
                    "main_menu"
                ],

                parse_mode="HTML",

                reply_markup=user_keyboard(
                    language
                )
            )

            return

    except Exception as e:

        logger.error(

            f"Text handler error: {e}",

            exc_info=True
        )

        try:

            await update.message.reply_text(

                T[admin_lang][
                    "error_occurred"
                ]
            )

        except Exception:

            pass


# =========================================================
# SEND REPLY CHILD CONTENT
# =========================================================

async def send_reply_child_content(message, child, language):
    inline_children = child.get("children", [])
    inline_items = []
    for child_index, inline_child in enumerate(inline_children):
        inline_name = inline_child.get("name", "Button")
        inline_type = inline_child.get("type", "text")
        if inline_type == "url":
            obj = make_inline_button(inline_name, url=inline_child.get("content", ""), style=inline_child.get("style", "default"))
        elif inline_type == "reaction":
            reaction_uid = inline_child.get("reaction_uid", inline_child.get("uid", ""))
            rd = data.get("reactions", {}).get(reaction_uid, {})
            users=[]
            for uid in rd.get("users", []):
                try: uid=int(uid)
                except (TypeError,ValueError): continue
                if uid not in users: users.append(uid)
            rd["users"]=users; rd["count"]=len(users); data.setdefault("reactions",{})[reaction_uid]=rd
            obj = make_inline_button(f"{inline_name} ({len(users)})", callback_data=f"reaction_{reaction_uid}", style=inline_child.get("style", "default"))
        else:
            obj = make_inline_button(inline_name, callback_data=f"rchild_{child_index}_{child.get('uid')}", style=inline_child.get("style", "default"))
        inline_items.append((getattr(obj,"text",inline_name),obj))
    inline_keyboard = None
    if inline_items:
        inline_keyboard = InlineKeyboardMarkup(build_button_rows(inline_items, child.get("inline_layout","default"), child.get("inline_rows",[])))

    contents = get_node_contents(child)
    if not contents and inline_keyboard:
        contents=[{"type":"text","content":"🔘 <b>Tanlang:</b>","caption":""}]
    for idx,item in enumerate(contents):
        ctype=item.get("type","text"); content=item.get("content",""); caption=item.get("caption","")
        markup=inline_keyboard if idx==len(contents)-1 else None
        if ctype=="text": await message.reply_text(content or "🔘 <b>Tanlang:</b>", parse_mode="HTML", reply_markup=markup)
        elif ctype=="photo": await message.reply_photo(content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype=="video": await message.reply_video(content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype=="document": await message.reply_document(content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype=="audio": await message.reply_audio(content, caption=caption or None, parse_mode="HTML", reply_markup=markup)
        elif ctype=="voice": await message.reply_voice(content, reply_markup=markup)
        elif ctype=="url": await message.reply_text(f'🔗 <a href="{content}">Havolani ochish</a>', parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=markup)

    nested=child.get("reply_children",[])
    if nested:
        await message.reply_text(T[language]["select_section"], parse_mode="HTML", reply_markup=user_keyboard(language,nested,show_back=True,layout_mode=child.get("reply_layout","default"),manual_rows=child.get("reply_rows",[])))


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update,
    context
):

    logger.error(

        f"Update {update} caused error "
        f"{context.error}",

        exc_info=True
    )
    
    
async def sticker_handler(
    update,
    context
):
    user = update.effective_user
    message = update.message
    
    if not is_admin(user.id):
        return
    
    admin_lang = get_admin_language()
    
    # =================================================
    # REACTION STICKER (inline tugma qo'shishda)
    # =================================================
    
    if context.user_data.get("adding_child"):
        step = context.user_data.get("child_step", 1)
        child_type = context.user_data.get("child_type")
        
        if step == 3 and child_type == "reaction":
            language = context.user_data.get("admin_language_section", "uz")
            parent_index = context.user_data.get("child_parent_index")
            child_name = context.user_data.get("new_child_name")
            
            buttons = data["buttons"].get(language, [])
            
            if not (isinstance(parent_index, int) and 0 <= parent_index < len(buttons)):
                context.user_data.clear()
                return
            
            sticker_id = message.sticker.file_id
            reaction_uid = uuid.uuid4().hex[:10]
            
            # Reaction ma'lumotini saqlash
            data["reactions"][reaction_uid] = {
    "users": [],
    "count": 0,
    "sticker": sticker_id,
    "name": child_name
}
            
            child = {
                "uid": uuid.uuid4().hex[:10],
                "name": child_name,
                "type": "reaction",
                "content": sticker_id,
                "reaction_uid": reaction_uid,
                "caption": "",
                "style": context.user_data.get("new_child_style", "default"),
                "children": [],
                "reply_children": []
            }
            
            if "children" not in buttons[parent_index]:
                buttons[parent_index]["children"] = []
            
            buttons[parent_index]["children"].append(child)
            save_data(data)
            
            for key in ["adding_child", "child_step", "child_type", 
                       "child_parent_index", "new_child_name", "new_child_style"]:
                context.user_data.pop(key, None)
            
            await update.message.reply_text(
                f"✅ <b>Reaksiya tugmasi qo'shildi!</b>\n\n"
                f"🎯 {child_name}\n"
                f"👥 Jami reaksiyalar: 0",
                parse_mode="HTML"
            )
            return
    
    if context.user_data.get("adding_inner_inline") and context.user_data.get("inner_inline_type") == "reaction" and message.sticker:
        language=context.user_data.get("admin_language_section","uz")
        buttons=data.get("buttons",{}).get(language,[])
        pi=context.user_data.get("inner_parent_index"); ci=context.user_data.get("inner_child_index")
        if isinstance(pi,int) and isinstance(ci,int) and 0<=pi<len(buttons):
            children=buttons[pi].get("reply_children",[])
            if 0<=ci<len(children):
                rid=uuid.uuid4().hex[:10]
                data.setdefault("reactions",{})[rid]={"users":[],"count":0,"sticker":message.sticker.file_id,"name":context.user_data.get("inner_inline_name","Reaksiya")}
                children[ci].setdefault("children",[]).append({"uid":uuid.uuid4().hex[:10],"name":context.user_data.get("inner_inline_name","Reaksiya"),"type":"reaction","content":message.sticker.file_id,"reaction_uid":rid,"caption":"","style":context.user_data.get("inner_inline_style","default"),"children":[],"reply_children":[]})
                save_data(data)
                for k in ["adding_inner_inline","inner_parent_index","inner_child_index","inner_inline_step","inner_inline_name","inner_inline_style","inner_inline_type","inner_inline_reaction"]: context.user_data.pop(k,None)
                await message.reply_text("✅ <b>Ichki tugmaga reaksiya qo‘shildi!</b>",parse_mode="HTML",reply_markup=admin_keyboard())
                return

    if context.user_data.get("adding_reply_child"):
        step = context.user_data.get("reply_child_step", 1)
        reply_child_type = context.user_data.get("reply_child_type")
        
        if step == 3 and reply_child_type == "reaction":
            language = context.user_data.get("admin_language_section", "uz")
            parent_index = context.user_data.get("reply_child_parent_index")
            child_name = context.user_data.get("new_reply_child_name")
            
            buttons = data["buttons"].get(language, [])
            
            if not (isinstance(parent_index, int) and 0 <= parent_index < len(buttons)):
                context.user_data.clear()
                return
            
            sticker_id = message.sticker.file_id
            reaction_uid = uuid.uuid4().hex[:10]
            
            data["reactions"][reaction_uid] = {
    "users": [],
    "count": 0,
    "sticker": sticker_id,
    "name": child_name
}
            
            child = {
                "uid": uuid.uuid4().hex[:10],
                "name": child_name,
                "type": "reaction",
                "content": sticker_id,
                "reaction_uid": reaction_uid,
                "caption": "",
                "style": context.user_data.get("new_reply_child_style", "default"),
                "children": [],
                "reply_children": []
            }
            
            if "reply_children" not in buttons[parent_index]:
                buttons[parent_index]["reply_children"] = []
            
            buttons[parent_index]["reply_children"].append(child)
            save_data(data)
            
            for key in ["adding_reply_child", "reply_child_step", "reply_child_type",
                       "reply_child_parent_index", "new_reply_child_name", "new_inline_name"]:
                context.user_data.pop(key, None)
            
            await update.message.reply_text(
                f"✅ <b>Ichki reaksiya tugmasi qo'shildi!</b>\n\n"
                f"🎯 {child_name}\n"
                f"👥 Jami reaksiyalar: 0",
                parse_mode="HTML"
            )
            return


# =========================================================
# JOIN REQUESTS (ZAYAVKA)
# =========================================================

async def join_request_handler(update, context):
    req = update.chat_join_request
    if not req:
        return

    chat_id = str(req.chat.id)
    user_id = req.from_user.id
    settings = data.setdefault("subscription_settings", {})

    if settings.get("auto_accept", False):
        try:
            await context.bot.approve_chat_join_request(
                chat_id=req.chat.id,
                user_id=user_id
            )
            pending = data.setdefault("join_requests", {}).get(chat_id, [])
            if user_id in pending:
                pending.remove(user_id)
            save_data(data)
            return
        except TelegramError as e:
            logger.error(f"Auto join request approval error: {e}")

    data.setdefault("join_requests", {}).setdefault(chat_id, [])
    ids = data["join_requests"][chat_id]
    if user_id not in ids:
        ids.append(user_id)
        data["join_requests"][chat_id] = ids[-50000:]
        save_data(data)

# =========================================================
# POST INIT
# =========================================================

async def post_init(
    application
):

    await application.bot.set_my_commands([

        BotCommand(
            "start",
            "Botni ishga tushirish"
        )

    ])

    logger.info(
        "Bot commands set"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print("🤖 Bot ishga tushmoqda...")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # =====================================================
    # STICKER HANDLER
    # =====================================================

    application.add_handler(
        MessageHandler(
            filters.Sticker.ALL,
            sticker_handler
        )
    )

    # =====================================================
    # CHANNEL JOIN REQUESTS
    # =====================================================
    application.add_handler(
        ChatJoinRequestHandler(join_request_handler)
    )

    # =====================================================
    # START COMMAND
    # =====================================================

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # =====================================================
    # CALLBACK QUERY
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    # =====================================================
    # MEDIA HANDLER
    # =====================================================

    application.add_handler(
        MessageHandler(
            (
                filters.PHOTO
                | filters.VIDEO
                | filters.Document.ALL
                | filters.AUDIO
                | filters.VOICE
            ),
            media_handler
        )
    )

    # =====================================================
    # TEXT HANDLER
    # =====================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    # =====================================================
    # ERROR HANDLER
    # =====================================================

    application.add_error_handler(
        error_handler
    )

    print("🔄 Telegram bot initialize qilinmoqda...")

    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()