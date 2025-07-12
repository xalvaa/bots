from telegram import Update, Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from typing import override, Self, Never
import datetime
from pathlib import Path

TOKEN = "8026101501:AAG2oj032H-QotYbYAHnhcOES2niIu43rCo"
ADMIN_CHAT_ID = "@KD_Swetty"
APPLICATIONS_FILE = Path("applications.txt")

class TigresBot:
    def __init__(self: Self, token: str) -> None:
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self._setup_handlers()

    def _setup_handlers(self: Self) -> None:
        """Настройка обработчиков команд с использованием @override"""
        handlers = [
            (CommandHandler("start", self.start)),
            (MessageHandler(Filters.regex(r"^📝 Оставить заявку$"), self.application)),
            (MessageHandler(Filters.regex(r"^ℹ️ Информация о школе$"), self.handle_message)),
            (MessageHandler(Filters.regex(r"^❓ FAQ$"), self.handle_message)),
            (MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        ]
        
        for handler in handlers:
            self.dispatcher.add_handler(handler)

    @override
    def start(self: Self, update: Update, context: CallbackContext) -> None:
        """Обработка команды /start с typed dict"""
        user_info: dict[str, str] = {
            "first_name": update.message.from_user.first_name,
            "username": update.message.from_user.username or "не указан"
        }
        
        update.message.reply_text(
            f"Добро пожаловать в 'Невские Тигры'! 🐯⚽\n"
            f"Привет, {user_info['first_name']}!\n"
            "Выберите действие:",
            reply_markup=self.main_menu_keyboard()
        )

    def main_menu_keyboard(self: Self) -> ReplyKeyboardMarkup:
        """Создание клавиатуры с использованием type hints"""
        return ReplyKeyboardMarkup([
            [KeyboardButton("📝 Оставить заявку")],
            [KeyboardButton("ℹ️ Информация о школе"), KeyboardButton("❓ FAQ")]
        ], resize_keyboard=True)

    @override
    def application(self: Self, update: Update, context: CallbackContext) -> None:
        """Обработка заявки с использованием pathlib"""
        update.message.reply_text(
            "Для заявки отправьте:\n"
            "1. Имя и фамилию ребёнка\n"
            "2. Возраст\n"
            "3. Контактный телефон\n\n"
            "<i>Пример: Иван Петров, 8 лет, +79111234567</i>",
            parse_mode="HTML"
        )
        context.user_data['waiting_for_application'] = True

    def notify_admin(self: Self, text: str, user: dict) -> None:
        """Улучшенная отправка уведомлений с typed Bot"""
        try:
            admin_bot: Bot = Bot(TOKEN)
            message = (
                f"🚀 <b>Новая заявка</b> 🚀\n\n{text}\n\n"
                f"👤 @{user.get('username', 'не указан')}\n"
                f"🕒 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            admin_bot.send_message(ADMIN_CHAT_ID, message, parse_mode="HTML")
        except Exception as e:
            print(f"Ошибка: {e!r}")

    @override
    def handle_message(self: Self, update: Update, context: CallbackContext) -> None:
        """Основной обработчик с match-case (Python 3.10+)"""
        if context.user_data.get('waiting_for_application'):
            self._process_application(update, context)
            return

        match update.message.text:
            case "ℹ️ Информация о школе":
                self._send_school_info(update)
            case "❓ FAQ":
                self._send_faq(update)
            case _:
                update.message.reply_text(
                    "Используйте кнопки меню",
                    reply_markup=self.main_menu_keyboard()
                )

    def _process_application(self: Self, update: Update, context: CallbackContext) -> None:
        """Обработка заявки с использованием pathlib"""
        app_text = update.message.text
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Запись в файл с использованием pathlib
        with APPLICATIONS_FILE.open("a", encoding="utf-8") as f:
            f.write(f"{timestamp} - {app_text}\n")
        
        # Отправка уведомления
        self.notify_admin(app_text, {
            "username": update.message.from_user.username,
            "id": update.message.from_user.id
        })
        
        update.message.reply_text(
            "✅ Заявка принята! Мы свяжемся с вами.",
            reply_markup=self.main_menu_keyboard()
        )
        context.user_data['waiting_for_application'] = False

    def _send_school_info(self: Self, update: Update) -> None:
        """Информация о школе с f-strings"""
        update.message.reply_text(
            f"🏟️ <b>Невские Тигры</b>\n\n"
            f"📍 Адрес: СПб, ул. Спортивная, 1\n"
            f"🕒 Часы работы: Пн-Вс 9:00-21:00\n"
            f"📞 Контакты: +7 (911) 123-45-67",
            parse_mode="HTML"
        )

    def _send_faq(self: Self, update: Update) -> None:
        """FAQ с использованием многострочных строк"""
        update.message.reply_text("""
❓ <b>Частые вопросы:</b>

1. <b>Возраст:</b> 5-16 лет
2. <b>Стоимость:</b> 3000 руб/мес
3. <b>Экипировка:</b> Форма + бутсы
4. <b>Пробное занятие:</b> Бесплатно
        """, parse_mode="HTML")

    def run(self: Self) -> Never:
        """Запуск бота с аннотацией Never"""
        print("🟢 Бот запущен")
        self.updater.start_polling()
        self.updater.idle()

if __name__ == "__main__":
    bot = TigresBot(TOKEN)
    bot.run()
