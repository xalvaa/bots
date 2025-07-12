from telegram import Update, Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
ADMIN_CHAT_ID = "@KD_Swetty"  # Или ID чата, если это не username

# ... (остальные функции из предыдущего кода остаются без изменений)

# Обработчик кнопки "Оставить заявку"
def application(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Чтобы оставить заявку, отправьте:\n"
        "1. Имя и фамилию ребёнка\n"
        "2. Возраст\n"
        "3. Контактный телефон родителя\n\n"
        "Пример:\n"
        "Иван Петров, 8 лет, +79111234567"
    )
    context.user_data['waiting_for_application'] = True

# Обработчик текстовых сообщений
def handle_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_application'):
        application_text = update.message.text
        
        # Сохраняем заявку
        with open("applications.txt", "a") as f:
            f.write(f"{application_text}\n")
        
        # Отправляем уведомление администратору
        try:
            admin_bot = Bot(token=TOKEN)
            admin_bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🔥 Новая заявка в 'Невские Тигры':\n\n{application_text}\n\n"
                     f"От: @{update.message.from_user.username or 'нет username'}"
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")
        
        update.message.reply_text(
            "✅ Спасибо! Ваша заявка принята.\n"
            "Мы свяжемся с вами в ближайшее время.",
            reply_markup=main_menu_keyboard()
        )
        context.user_data['waiting_for_application'] = False
    else:
        # ... (остальной код обработки сообщений без изменений)

# ... (остальной код без изменений)
