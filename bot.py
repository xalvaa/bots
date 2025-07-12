from telegram import Update, Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pathlib import Path
import datetime
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8026101501:AAG2oj032H-QotYbYAHnhcOES2niIu43rCo"
ADMIN_CHAT_ID = "@KD_Swetty"  # Или ID чата администратора
APPLICATIONS_FILE = Path("applications.txt")

class FootballSchoolBot:
    def __init__(self, token: str):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Регистрация обработчиков
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r"^📝 Оставить заявку$"), self.show_application_form))
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r"^ℹ️ Информация о школе$"), self.show_school_info))
        self.dispatcher.add_handler(MessageHandler(Filters.regex(r"^❓ FAQ$"), self.show_faq))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

    @staticmethod
    def main_menu_keyboard():
        """Создаем клавиатуру главного меню"""
        return ReplyKeyboardMarkup([
            [KeyboardButton("📝 Оставить заявку")],
            [KeyboardButton("ℹ️ Информация о школе"), KeyboardButton("❓ FAQ")]
        ], resize_keyboard=True)

    def start(self, update: Update, context: CallbackContext):
        """Обработка команды /start"""
        user = update.effective_user
        update.message.reply_text(
            f"Привет, {user.first_name}! 🐯⚽\n"
            "Добро пожаловать в футбольную школу 'Невские Тигры'!\n"
            "Выберите действие:",
            reply_markup=self.main_menu_keyboard()
        )

    def show_application_form(self, update: Update, context: CallbackContext):
        """Показываем форму для заявки"""
        update.message.reply_text(
            "📝 Для оформления заявки отправьте:\n"
            "1. ФИО ребенка\n"
            "2. Возраст\n"
            "3. Контактный телефон\n\n"
            "<i>Пример: Иванов Алексей, 8 лет, +79111234567</i>",
            parse_mode="HTML"
        )
        context.user_data['expecting_application'] = True

    def handle_message(self, update: Update, context: CallbackContext):
        """Обработка входящих сообщений"""
        if context.user_data.get('expecting_application'):
            self.process_application(update, context)
        else:
            update.message.reply_text(
                "Пожалуйста, используйте кнопки меню👇",
                reply_markup=self.main_menu_keyboard()
            )

    def process_application(self, update: Update, context: CallbackContext):
        """Обработка данных заявки"""
        application_text = update.message.text
        user = update.effective_user
        
        # Логирование заявки
        logger.info(f"Новая заявка от @{user.username}: {application_text}")
        
        # Сохранение в файл
        try:
            with APPLICATIONS_FILE.open("a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} | @{user.username or 'N/A'} | {application_text}\n")
        except Exception as e:
            logger.error(f"Ошибка сохранения заявки: {e}")

        # Отправка уведомления администратору
        self.notify_admin(application_text, user)
        
        update.message.reply_text(
            "✅ Ваша заявка принята! Мы свяжемся с вами в ближайшее время.",
            reply_markup=self.main_menu_keyboard()
        )
        context.user_data.pop('expecting_application', None)

    def notify_admin(self, application_text: str, user):
        """Отправка уведомления администратору"""
        try:
            bot = Bot(TOKEN)
            message = (
                f"⚠️ <b>НОВАЯ ЗАЯВКА</b> ⚠️\n\n"
                f"{application_text}\n\n"
                f"👤 Пользователь: @{user.username or 'нет username'}\n"
                f"🆔 ID: {user.id}\n"
                f"⏱️ Время: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=message,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    def show_school_info(self, update: Update, context: CallbackContext):
        """Информация о школе"""
        update.message.reply_text(
            "🏟️ <b>Футбольная школа 'Невские Тигры'</b>\n\n"
            "📍 Адрес: г. Санкт-Петербург, ул. Спортивная, 1\n"
            "🕒 Режим работы:\n"
            "   - Пн-Пт: 9:00-21:00\n"
            "   - Сб-Вс: 10:00-18:00\n\n"
            "⚽ Возрастные группы: 5-16 лет\n"
            "📞 Контактный телефон: +7 (911) 123-45-67\n\n"
            "Мы профессионально развиваем юных футболистов!",
            parse_mode="HTML"
        )

    def show_faq(self, update: Update, context: CallbackContext):
        """Часто задаваемые вопросы"""
        update.message.reply_text(
            "❓ <b>Часто задаваемые вопросы</b>\n\n"
            "1. <b>С какого возраста принимаете?</b>\n"
            "   - С 5 лет\n\n"
            "2. <b>Сколько стоит обучение?</b>\n"
            "   - 3000 руб./месяц\n\n"
            "3. <b>Какая экипировка нужна?</b>\n"
            "   - Спортивная форма и бутсы\n\n"
            "4. <b>Есть ли пробные занятия?</b>\n"
            "   - Да, первая тренировка бесплатно",
            parse_mode="HTML"
        )

    def run(self):
        """Запуск бота"""
        logger.info("Starting bot...")
        self.updater.start_polling()
        self.updater.idle()

if __name__ == "__main__":
    bot = FootballSchoolBot(TOKEN)
    bot.run()
