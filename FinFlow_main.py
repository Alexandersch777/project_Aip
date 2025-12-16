# Импортируем необходимые библиотеки
from telegram import Update, ReplyKeyboardMarkup  # для работы с Telegram API и клавиатурами
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes  # для создания бота
import json  # для работы с JSON файлами (сохранение/загрузка данных)
import os  # для работы с файловой системой
import matplotlib.pyplot as plt  # для создания графиков и диаграмм
import io  # для работы с байтовыми потоками (создание изображений в памяти)


class FinanceBot:
    """
    Телеграм-бот для управления личными финансами.

    Позволяет пользователям отслеживать доходы и расходы,
    просматривать статистику и получать визуализацию данных.
    """

    def __init__(self, token: str):
        """
        Инициализирует бота с заданным токеном.

        :param token: Токен бота, полученный от BotFather
        :type token: str
        """
        # Конструктор класса, вызывается при создании объекта бота
        self.token = token  # сохраняем токен бота для авторизации в Telegram
        self.data = self.load_data()  # загружаем данные пользователей из файла

        # Создаем главную клавиатуру с кнопками
        self.kb = [
            ["Доход", "Расход"],  # первая строка кнопок
            ["Баланс", "Статистика"],  # вторая строка кнопок
            ["Категории"]  # третья строка кнопок
        ]

        # Клавиатура с категориями для расходов
        self.exp_cat = [
            ["Еда", "Транспорт", "Жилье"],  # основные категории расходов
            ["Развлечения", "Одежда", "Здоровье"],  # дополнительные категории
            ["Образование", "Прочее", "Назад"]  # специальные категории и кнопка назад
        ]

        # Клавиатура с категориями для доходов
        self.inc_cat = [
            ["Зарплата", "Бизнес", "Инвестиции"],  # основные источники доходов
            ["Подарок", "Премия", "Прочее"],  # дополнительные источники
            ["Назад"]  # кнопка возврата
        ]

    def load_data(self):
        """
        Загружает финансовые данные пользователей из JSON файла.

        :return: Словарь с данными пользователей или пустой словарь при ошибке
        :rtype: dict
        :raises json.JSONDecodeError: Если файл содержит некорректный JSON
        :raises OSError: При проблемах с доступом к файлу
        """
        try:
            # Проверяем существует ли файл с данными
            if os.path.exists("data.json"):
                # Открываем файл для чтения
                with open("data.json", "r") as f:
                    # Загружаем JSON данные и преобразуем в Python словарь
                    return json.load(f)
        except:
            # Если произошла ошибка (файл не существует или поврежден)
            pass  # просто пропускаем ошибку
        return {}  # возвращаем пустой словарь если файла нет или ошибка

    def save_data(self):
        """
        Сохраняет финансовые данные пользователей в JSON файл.

        :raises OSError: При проблемах с записью в файл
        :raises TypeError: Если данные не могут быть сериализованы в JSON
        """
        try:
            # Открываем файл для записи
            with open("data.json", "w") as f:
                # Сохраняем данные в формате JSON с отступами
                json.dump(self.data, f)
        except:
            # Если произошла ошибка при сохранении
            pass  # пропускаем ошибку

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработчик команды /start - начало работы с ботом.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param context: Контекст выполнения, содержит дополнительные данные
        :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
        """
        # Создаем клавиатуру на основе нашего шаблона
        keyboard = ReplyKeyboardMarkup(self.kb, resize_keyboard=True)
        # Отправляем приветственное сообщение с клавиатурой
        await update.message.reply_text(
            "Выберите действие:",  # текст сообщения
            reply_markup=keyboard  # прикрепляем клавиатуру
        )
    async def hand_mess(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает все текстовые сообщения от пользователя.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param context: Контекст выполнения, содержит дополнительные данные
        :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
        """
        # Получаем текст сообщения от пользователя
        text = update.message.text
        # Получаем ID пользователя (преобразуем в строку для consistency)
        user_id = str(update.message.from_user.id)

        # Обрабатываем нажатие кнопки "Доход"
        if text == "Доход":
            # Сохраняем в контексте что пользователь хочет добавить доход
            context.user_data["action"] = "income"
            # Создаем клавиатуру с категориями доходов
            keyboard = ReplyKeyboardMarkup(self.inc_cat, resize_keyboard=True)
            # Просим выбрать категорию
            await update.message.reply_text("Выберите категорию дохода:", reply_markup=keyboard)

        # Обрабатываем нажатие кнопки "Расход"
        elif text == "Расход":
            context.user_data["action"] = "expense"  # сохраняем тип операции
            keyboard = ReplyKeyboardMarkup(self.exp_cat, resize_keyboard=True)
            await update.message.reply_text("Выберите категорию расхода:", reply_markup=keyboard)
        # Обрабатываем нажатие кнопки "Баланс"
        elif text == "Баланс":
            # Вызываем функцию показа баланса
            await self.show_bal(update, user_id)
        # Обрабатываем нажатие кнопки "Статистика"
        elif text == "Статистика":
            # Вызываем функцию показа статистики с диаграммами
            await self.show_stat(update, user_id)
        # Обрабатываем нажатие кнопки "Категории"
        elif text == "Категории":
            await self.show_cat(update, user_id)
        # Обрабатываем выбор категорий расходов (все кнопки с эмодзи еды, транспорта и т.д.)
        elif text in ["Еда", "Транспорт", "Жилье", "Развлечения",
                      "Одежда", "Здоровье", "Образование", "Подарки"]:
            # Сохраняем выбранную категорию во временные данные пользователя
            context.user_data["category"] = text
            # Просим ввести сумму для выбранной категории
            await update.message.reply_text(f"Введите сумму для {text}:")
        # Обрабатываем выбор категорий доходов
        elif text in ["Зарплата", "Бизнес", "Инвестиции", "Подарок",
                      "Премия", "Прочее"]:
            context.user_data["category"] = text
            await update.message.reply_text(f"Введите сумму для {text}:")

        # Обрабатываем кнопку "Назад"
        elif text == "Назад":
            # Возвращаем главную клавиатуру
            keyboard = ReplyKeyboardMarkup(self.kb, resize_keyboard=True)
            await update.message.reply_text("Возвращаемся в главное меню", reply_markup=keyboard)

        else:
            # Если это не команда и не кнопка, считаем что пользователь ввел сумму
            await self.hand_amnt(update, context, user_id, text)

    async def hand_amnt(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str, text: str):
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
            # Пытаемся преобразовать текст в число с плавающей точкой
            amount = float(text)
            # Получаем тип операции (доход/расход) из временных данных
            action = context.user_data.get("action")
            # Получаем выбранную категорию
            category = context.user_data.get("category")

            # Проверяем что все необходимые данные есть
            if not action or not category:
                await update.message.reply_text("Ошибка: не выбрано действие или категория")
                return  # прерываем выполнение если данных нет

            # Если у пользователя еще нет данных, создаем пустой список
            if user_id not in self.data:
                self.data[user_id] = []

            # Создаем запись о транзакции
            record = {
                "type": "income" if action == "income" else "expense",  # тип операции
                "amount": amount,  # сумма
                "category": category  # категория
            }

            # Добавляем запись в данные пользователя
            self.data[user_id].append(record)
            # Сохраняем все данные в файл
            self.save_data()

            # Показываем главную клавиатуру снова
            keyboard = ReplyKeyboardMarkup(self.kb, resize_keyboard=True)
            # Подтверждаем добавление операции
            await update.message.reply_text(
                f"{category} {amount} руб. добавлен!",  # сообщение подтверждения
                reply_markup=keyboard  # возвращаем главную клавиатуру
            )

            # Очищаем временные данные пользователя
            context.user_data.clear()

        except ValueError:
            # Если преобразование в число не удалось
            await update.message.reply_text("Введите число!")

    async def show_bal(self, update: Update, user_id: str):
        """
        Показывает текущий баланс пользователя.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param user_id: ID пользователя в Telegram
        :type user_id: str
        """
        # Проверяем есть ли данные у пользователя
        if user_id not in self.data:
            await update.message.reply_text("Нет операций")
            return

        # Суммируем все доходы (транзакции с типом 'income')
        income = sum(r['amount'] for r in self.data[user_id] if r['type'] == 'income')
        # Суммируем все расходы (транзакции с типом 'expense')
        expense = sum(r['amount'] for r in self.data[user_id] if r['type'] == 'expense')
        # Вычисляем баланс
        balance = income - expense
        # Форматируем текст с результатами
        text = f"""
Доходы: {income} руб.
Расходы: {expense} руб.
Баланс: {balance} руб.
        """
        # Отправляем сообщение с балансом
        await update.message.reply_text(text)

    async def show_stat(self, update: Update, user_id: str):
        """
        Показывает статистику с графиками доходов и расходов.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param user_id: ID пользователя в Telegram
        :type user_id: str
        """
        # Проверяем есть ли данные для статистики
        if user_id not in self.data or not self.data[user_id]:
            await update.message.reply_text("Нет данных для статистики")
            return

        # Создаем словари для группировки данных по категориям
        expenses_by_category = {}  # для расходов
        income_by_category = {}  # для доходов

        # Проходим по всем транзакциям пользователя
        for record in self.data[user_id]:
            category = record["category"]  # получаем категорию
            amount = record["amount"]  # получаем сумму

            # В зависимости от типа операции добавляем в соответствующий словарь
            if record["type"] == "expense":
                # Увеличиваем сумму для данной категории расходов
                expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
            else:
                # Увеличиваем сумму для данной категории доходов
                income_by_category[category] = income_by_category.get(category, 0) + amount

        # Отправляем диаграмму доходов
        await self.send_inc_chrt(update, income_by_category)

        # Отправляем диаграмму расходов
        await self.send_exp_chrt(update, expenses_by_category)

        # Отправляем текстовую статистику
        await self.send_txt_stat(update, income_by_category, expenses_by_category)

    async def send_inc_chrt(self, update: Update, income_by_category: dict):
        """
        Создает и отправляет круговую диаграмму доходов.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param income_by_category: Словарь с категориями доходов и суммами
        :type income_by_category: dict
        """
        # Проверяем есть ли данные о доходах
        if not income_by_category:
            await update.message.reply_text("Нет данных о доходах")
            return

        # Создаем новую фигуру для графика
        plt.figure(figsize=(8, 6))

        # Получаем списки категорий и сумм
        categories = list(income_by_category.keys())
        amounts = list(income_by_category.values())

        # Задаем зеленые цвета для доходов
        colors = ['#90EE90', '#98FB98', '#8FBC8F', '#3CB371', '#2E8B57', '#228B22']

        # Создаем круговую диаграмму
        plt.pie(amounts,
                labels=categories,  # подписи категорий
                autopct='%1.1f%%',  # проценты на диаграмме
                startangle=90,  # начальный угол
                colors=colors[:len(categories)],  # цвета (обрезаем по количеству категорий)
                textprops={'fontsize': 10})  # размер шрифта

        # Устанавливаем заголовок
        plt.title(' Доходы по категориям', fontsize=14, fontweight='bold')

        # Создаем байтовый буфер для сохранения изображения
        buf = io.BytesIO()
        # Сохраняем график в буфер в формате PNG
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        # Перемещаем указатель в начало буфера
        buf.seek(0)
        # Закрываем график для освобождения памяти
        plt.close()

        # Считаем общую сумму доходов
        total_income = sum(amounts)
        # Отправляем изображение пользователю
        await update.message.reply_photo(
            photo=buf,  # изображение из буфера
            caption=f"Общие доходы: {total_income} руб."  # подпись к фото
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

        # Задаем красные цвета для расходов
        colors = ['#FFB6C1', '#FF69B4', '#FF1493', '#DC143C', '#B22222', '#8B0000']

        plt.pie(amounts,
                labels=categories,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(categories)],
                textprops={'fontsize': 10})
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

    async def send_txt_stat(self, update: Update, income_by_category: dict, expenses_by_category: dict):
        """
        Отправляет детальную текстовую статистику.

        :param update: Объект с информацией о входящем сообщении
        :type update: telegram.Update
        :param income_by_category: Словарь с категориями доходов и суммами
        :type income_by_category: dict
        :param expenses_by_category: Словарь с категориями расходов и суммами
        :type expenses_by_category: dict
        """
        # Считаем общие суммы
        total_income = sum(income_by_category.values())
        total_expenses = sum(expenses_by_category.values())
        balance = total_income - total_expenses

        # Начинаем формировать текст статистики
        text = "Детальная статистика:\n\n"

        # Добавляем раздел доходов
        text += f"Общие доходы: {total_income} руб.\n"
        if income_by_category:
            text += "Доходы по категориям:\n"
            # Сортируем категории по убыванию суммы
            for category, amount in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
                # Вычисляем процент от общей суммы
                percent = (amount / total_income) * 100
                text += f"  {category}: {amount} руб. ({percent:.1f}%)\n"

        # Добавляем раздел расходов
        text += f"\n Общие расходы: {total_expenses} руб.\n"
        if expenses_by_category:
            text += "Расходы по категориям:\n"
            for category, amount in sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True):
                percent = (amount / total_expenses) * 100
                text += f"  {category}: {amount} руб. ({percent:.1f}%)\n"

        # Добавляем итоговый баланс
        text += f"\n Итоговый баланс: {balance} руб."

        # Отправляем текстовую статистику
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

        # Собираем данные по категориям (аналогично show_statistics_with_charts)
        expenses_by_category = {}
        income_by_category = {}

        for record in self.data[user_id]:
            category = record["category"]
            amount = record["amount"]

            if record["type"] == "expense":
                expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
            else:
                income_by_category[category] = income_by_category.get(category, 0) + amount

        text = "Статистика по категориям:\n\n"

        text += "Расходы:\n"
        if expenses_by_category:
            total_expenses = sum(expenses_by_category.values())
            for category, amount in sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True):
                percent = (amount / total_expenses) * 100
                text += f"{category}: {amount} руб. ({percent:.1f}%)\n"
        else:
            text += "Нет расходов\n"

        text += "\n Доходы:\n"
        if income_by_category:
            total_income = sum(income_by_category.values())
            for category, amount in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
                percent = (amount / total_income) * 100
                text += f"{category}: {amount} руб. ({percent:.1f}%)\n"
        else:
            text += "Нет доходов\n"

        await update.message.reply_text(text)

    def run(self):
        """
        Запускает бота и начинает обработку сообщений.

        :raises telegram.error.InvalidToken: Если указан неверный токен
        :raises telegram.error.NetworkError: При проблемах с сетью
        """
        # Создаем приложение бота с указанным токеном
        app = Application.builder().token(self.token).build()

        # Регистрируем обработчики команд и сообщений
        app.add_handler(CommandHandler("start", self.start))  # обработчик команды /start
        app.add_handler(MessageHandler(filters.TEXT, self.hand_mess))  # обработчик всех текстовых сообщений

        print("Бот запущен!")
        # Запускаем бота в режиме опроса сервера Telegram
        app.run_polling()


# Точка входа в программу
if __name__ == "__main__":
    # Токен бота (должен быть получен от @BotFather)
    TOKEN = "7094551997:AAHwaTRiMud4BmB7YBLCBkFJ78vg7W8nDpE"
    # Создаем экземпляр бота и запускаем его
    FinanceBot(TOKEN).run()