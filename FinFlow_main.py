import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (Application,
                          CommandHandler, MessageHandler,
                          filters, ContextTypes)
import json
import os
import matplotlib.pyplot as plt
import io


class FinanceBot:
    """
    Телеграм-бот для управления личными финансами.

    Позволяет пользователям отслеживать доходы и расходы,
    просматривать статистику и получать визуализацию данных.
    :ivar token: Токен бота Telegram
    :type token: str
    :ivar data: Финансовые данные всех пользователей
    :type data: dict
    :ivar kb: Главная клавиатура
    :type kb: list
    :ivar exp_cat: Категории расходов
    :type exp_cat: list
    :ivar inc_cat: Категории доходов
    :type inc_cat: list
    """

    def __init__(self, token: str):
        """
        Инициализирует бота с заданным токеном.

        :param token: Токен бота, полученный от BotFather
        :type token: str
        """
        self.token = token
        self.data = self.load_data()
        self.kb = [
            ["Доход", "Расход"],
            ["Баланс", "Статистика"],
            ["Категории"]
        ]
        self.exp_cat = [
            ["Еда", "Транспорт", "Жилье"],
            ["Развлечения", "Одежда", "Здоровье"],
            ["Образование", "Прочее", "Назад"]
        ]
        self.inc_cat = [
            ["Зарплата", "Бизнес", "Инвестиции"],
            ["Подарок", "Премия", "Прочее"],
            ["Назад"]
        ]

    def load_data(self):
        """
        Загружает финансовые данные пользователей из JSON файла.

        :return: Словарь с данными пользователей или пустой словарь при ошибке
        :rtype: dict
        """
        try:
            if os.path.exists("data.json"):
                with open("data.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_data(self):
        """
        Сохраняет финансовые данные пользователей в JSON файл.

        :raises OSError: При проблемах с записью в файл
        """
        try:
            with open("data.json", "w", encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            raise OSError

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /start - начало работы с ботом.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param context: Контекст выполнения, содержит дополнительные данные
        :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
        """
        keyboard = ReplyKeyboardMarkup(self.kb, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите действие:",
            reply_markup=keyboard
        )

    async def hand_mess(self, update: Update,
                        context: ContextTypes.DEFAULT_TYPE):

        """
        Обрабатывает все текстовые сообщения от пользователя.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param context: Контекст выполнения, содержит доп.данные(bt,ct,usr_dat)
        :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
        """
        text = update.message.text
        user_id = str(update.message.from_user.id)

        if text == "Доход":
            context.user_data["action"] = "income"
            keyboard = ReplyKeyboardMarkup(self.inc_cat, resize_keyboard=True)
            await update.message.reply_text(
                "Выберите категорию дохода:",
                reply_markup=keyboard
            )

        elif text == "Расход":
            context.user_data["action"] = "expense"
            keyboard = ReplyKeyboardMarkup(self.exp_cat, resize_keyboard=True)
            await update.message.reply_text(
                "Выберите категорию расхода:",
                reply_markup=keyboard
            )

        elif text == "Баланс":
            await self.show_bal(update, user_id)

        elif text == "Статистика":
            await self.show_stat(update, user_id)

        elif text == "Категории":
            await self.show_cat(update, user_id)

        elif text in ["Еда", "Транспорт", "Жилье", "Развлечения",
                      "Одежда", "Здоровье", "Образование", "Подарки"]:
            context.user_data["category"] = text
            await update.message.reply_text(f"Введите сумму для {text}:")

        elif text in ["Зарплата", "Бизнес", "Инвестиции", "Подарок",
                      "Премия", "Прочее"]:
            context.user_data["category"] = text
            await update.message.reply_text(f"Введите сумму для {text}:")

        elif text == "Назад":
            keyboard = ReplyKeyboardMarkup(self.kb, resize_keyboard=True)
            await update.message.reply_text(
                "Возвращаемся в главное меню",
                reply_markup=keyboard
            )

        else:
            await self.hand_amnt(update, context, user_id, text)

    async def hand_amnt(self, update: Update,
                        context: ContextTypes.DEFAULT_TYPE,
                        user_id: str, text: str):
        """
        Обрабатывает ввод суммы для дохода или расхода.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param context: Контекст выполнения, содержит дополнительные данные
        :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
        :param user_id: ID пользователя в Telegram
        :type user_id: str
        :param text: Текст сообщения, который должен содержать сумму
        :type text: str
        :raises ValueError: Если текст не может быть преобразован в число
        """
        try:
            amount = float(text)
            action = context.user_data.get("action")
            category = context.user_data.get("category")

            if not action or not category:
                await update.message.reply_text(
                    "Ошибка: не выбрано действие или категория"
                )
                return

            if user_id not in self.data:
                self.data[user_id] = []

            record = {
                "type": "income" if action == "income" else "expense",
                "amount": amount,
                "category": category
            }

            self.data[user_id].append(record)
            self.save_data()

            keyboard = ReplyKeyboardMarkup(self.kb, resize_keyboard=True)
            await update.message.reply_text(
                f"{category} {amount} руб. добавлен!",
                reply_markup=keyboard
            )

            context.user_data.clear()

        except ValueError:
            await update.message.reply_text("Введите число!")

    async def show_bal(self, update: Update, user_id: str):
        """
        Показывает текущий баланс пользователя.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param user_id: ID пользователя в Telegram
        :type user_id: str
        """
        if user_id not in self.data:
            await update.message.reply_text("Нет операций")
            return

        inc = sum(r['amount'] for r in self.data[user_id]
                  if r['type'] == 'income')
        exp = sum(r['amount'] for r in self.data[user_id]
                  if r['type'] == 'expense')
        bal = inc - exp

        text = f"""
Доходы: {inc} руб.
Расходы: {exp} руб.
Баланс: {bal} руб.
        """

        await update.message.reply_text(text)

    async def show_stat(self, update: Update, user_id: str):
        """
        Показывает статистику с графиками доходов и расходов.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param user_id: ID пользователя в Telegram
        :type user_id: str
        """
        if user_id not in self.data or not self.data[user_id]:
            await update.message.reply_text("Нет данных для статистики")
            return

        exp_by_cat = {}
        inc_by_cat = {}

        for record in self.data[user_id]:
            cat = record["category"]
            amount = record["amount"]

            if record["type"] == "expense":
                exp_by_cat[cat] = exp_by_cat.get(cat, 0) + amount
            else:
                inc_by_cat[cat] = inc_by_cat.get(cat, 0) + amount

        await self.send_inc_chrt(update, inc_by_cat)
        await self.send_exp_chrt(update, exp_by_cat)
        await self.send_txt_stat(update, inc_by_cat, exp_by_cat)

    async def send_inc_chrt(self, update: Update, income_by_category: dict):
        """
        Создает и отправляет круговую диаграмму доходов.

        :param update: Объект с информацией о входящем сообщения
        :type update: telegram.Update
        :param income_by_category: Словарь с категориями доходов и суммами
        :type income_by_category: dict
        """
        if not income_by_category:
            await update.message.reply_text("Нет данных о доходах")
            return

        plt.figure(figsize=(8, 6))

        categories = list(income_by_category.keys())
        amounts = list(income_by_category.values())

        colors = ['#90EE90', '#98FB98', '#8FBC8F',
                  '#3CB371', '#2E8B57', '#228B22']

        plt.pie(
            amounts,
            labels=categories,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(categories)],
            textprops={'fontsize': 10}
        )

        plt.title('Доходы по категориям', fontsize=14, fontweight='bold')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        total_income = sum(amounts)
        await update.message.reply_photo(
            photo=buf,
            caption=f"Общие доходы: {total_income} руб."
        )

    async def send_exp_chrt(self, update: Update, expenses_by_category: dict):
        """
        Создает и отправляет круговую диаграмму расходов.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param expenses_by_category: Словарь с категориями расходов и суммами
        :type expenses_by_category: dict
        """
        if not expenses_by_category:
            await update.message.reply_text("Нет данных о расходах")
            return

        plt.figure(figsize=(8, 6))

        categories = list(expenses_by_category.keys())
        amounts = list(expenses_by_category.values())

        colors = ['#FFB6C1', '#FF69B4', '#FF1493',
                  '#DC143C', '#B22222', '#8B0000']

        plt.pie(
            amounts,
            labels=categories,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(categories)],
            textprops={'fontsize': 10}
        )

        plt.title('Расходы по категориям', fontsize=14, fontweight='bold')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        total_expenses = sum(amounts)
        await update.message.reply_photo(
            photo=buf,
            caption=f"Общие расходы: {total_expenses} руб."
        )

    async def send_txt_stat(self, update: Update,
                            income_by_category: dict,
                            expenses_by_category: dict):
        """
        Отправляет детальную текстовую статистику.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param income_by_category: Словарь с категориями доходов и суммами
        :type income_by_category: dict
        :param expenses_by_category: Словарь с категориями расходов и суммами
        :type expenses_by_category: dict
        """
        total_income = sum(income_by_category.values())
        total_expenses = sum(expenses_by_category.values())
        balance = total_income - total_expenses

        text = "Детальная статистика:\n\n"
        text += f"Общие доходы: {total_income} руб.\n"

        if income_by_category:
            text += "Доходы по категориям:\n"
            for category, amount in sorted(
                income_by_category.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                percent = (amount / total_income) * 100
                text += f"  {category}: {amount} руб. ({percent:.1f}%)\n"

        text += f"\nОбщие расходы: {total_expenses} руб.\n"

        if expenses_by_category:
            text += "Расходы по категориям:\n"
            for category, amount in sorted(
                expenses_by_category.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                percent = (amount / total_expenses) * 100
                text += f"  {category}: {amount} руб. ({percent:.1f}%)\n"

        text += f"\nИтоговый баланс: {balance} руб."

        await update.message.reply_text(text)

    async def show_cat(self, update: Update, user_id: str):
        """
        Показывает статистику по категориям доходов и расходов.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param user_id: ID пользователя в Telegram
        :type user_id: str
        """
        if user_id not in self.data:
            await update.message.reply_text("Нет операций")
            return

        expenses_by_category = {}
        income_by_category = {}

        for record in self.data[user_id]:
            category = record["category"]
            amount = record["amount"]

            if record["type"] == "expense":
                expenses_by_category[category] = (
                    expenses_by_category.get(category, 0) + amount
                )
            else:
                income_by_category[category] = (
                    income_by_category.get(category, 0) + amount
                )

        text = "Статистика по категориям:\n\n"
        text += "Расходы:\n"

        if expenses_by_category:
            total_expenses = sum(expenses_by_category.values())
            for category, amount in sorted(
                expenses_by_category.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                percent = (amount / total_expenses) * 100
                text += f"{category}: {amount} руб. ({percent:.1f}%)\n"
        else:
            text += "Нет расходов\n"

        text += "\nДоходы:\n"

        if income_by_category:
            total_income = sum(income_by_category.values())
            for category, amount in sorted(
                income_by_category.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                percent = (amount / total_income) * 100
                text += f"{category}: {amount} руб. ({percent:.1f}%)\n"
        else:
            text += "Нет доходов\n"

        await update.message.reply_text(text)

    def run(self):
        try:
            """
            Запускает бота и начинает обработку сообщений.
                        
            :raises telegram.error.InvalidToken: Если указан неверный токен
            :raises telegram.error.NetworkError: При проблемах с сетью
            """
            app = Application.builder().token(self.token).build()
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(MessageHandler(filters.TEXT, self.hand_mess))

            print("Бот запущен!")
            app.run_polling()
        except telegram.error.InvalidToken:
            raise telegram.error.InvalidToken
        except telegram.error.NetworkError:
            raise telegram.error.NetworkError


if __name__ == "__main__":
    TOKEN = "7094551997:AAHwaTRiMud4BmB7YBLCBkFJ78vg7W8nDpE"
    FinanceBot(TOKEN).run()
