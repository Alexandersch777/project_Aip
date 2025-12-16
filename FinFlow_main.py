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
